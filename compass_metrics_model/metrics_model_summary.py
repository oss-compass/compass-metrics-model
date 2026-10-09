
import logging

from functools import reduce
from urllib.parse import urlparse

from perceval.backend import uuid

from grimoire_elk.elastic import ElasticSearch
from grimoirelab_toolkit.datetime import datetime_utcnow

from elasticsearch import Elasticsearch, RequestsHttpConnection

from .utils import (get_uuid, get_date_list)

MAX_BULK_UPDATE_SIZE = 5000

logger = logging.getLogger(__name__)

class MetricsSummary:
    """
    MetricsSummary mainly designed to summarize the global data of MetricsModel.
    :param metric_index: summarization target index name
    :param from_date: summarization start date
    :param end_date: summarization end date
    :param out_index: summarization storage index name
    """
    def __init__(self, metric_index, model_name, from_date, end_date, out_index):
        self.from_date = from_date
        self.end_date = end_date
        self.out_index = out_index
        self.model_name = model_name
        self.metric_index = metric_index
        self.summary_name = self.__class__.__name__

    def base_stat_method(self, field):
        query = {
            f"{field}_mean": {
                'avg': {
                    'field': field
                }
            },
            f"{field}_median": {
                'percentiles': {
                    'field': field,
                    'percents': [50]
                }
            }
        }
        return query

    def apply_stat_method(self, fields):
        return reduce(lambda query, field: {**self.base_stat_method(field), **query}, fields, {})

    def metrics_model_summary_query(self, date=None, category=None, category_urls=None):
        query = {
            "size": 0,
            "from": 0,
            "query": {
                "bool": {
                    "filter": self.summary_query_filters(date, category_urls)
                }
            },
            "aggs": self.apply_stat_method(self.summary_fields())
        }
        body = self.es_in.search(index=self.metric_index, body=query)
        return body

    def summary_query_filters(self, date, category_urls=None):
        """原有两条过滤条件保持不变；仅在显式传入分类成员时追加第三条。

        空列表是有意义的输入（该分类没有成员），必须与"未请求分类"区分：
        前者追加一个匹配不到任何文档的 terms 条件，后者完全不追加。
        """
        filters = [
            {
                "range": {
                    "grimoire_creation_date": {
                        "lte": date.strftime("%Y-%m-%d"),
                        "gte": date.strftime("%Y-%m-%d")
                    }
                }
            },
            {
                "term": {
                    "model_name.keyword": self.model_name
                }
            }
        ]
        if category_urls is not None:
            # 必须走 label.keyword：指标索引里 label 是 text + keyword 子字段
            # （上游 compass-web-service 三处映射声明一致如此，且其精确过滤一律用
            #   label.keyword）。对**裸** label 做 terms 是拿整串 URL 去比词元，
            # 而 text 字段里存的是分词后的词元，故**静默返回 0 条**——
            # 每个分类的汇总都会从空集算出来。真实引擎实测见
            # tests/acceptance/test_real_index_a01_a04.py。
            filters.append({"terms": {"label.keyword": category_urls}})
        return filters

    def metrics_model_enrich(self, result, field):
        result['res'] = {
            **result['res'],
            **{
                f"{field}_mean": result['aggs'][f"{field}_mean"]['value'],
                f"{field}_median": result['aggs'][f"{field}_median"]['values']['50.0'],
            }
        }
        return result

    def metrics_model_after_query(self, response):
        aggregations = response.get('aggregations')
        return reduce(self.metrics_model_enrich, self.summary_fields(), {'aggs': aggregations, 'res': {}})

    def ensure_summary_index_mapping(self, es_client):
        """在写入任何分类文档之前，确保 out_index 的映射已声明 category。

        为什么必须在写入之前
        --------------------
        映射可以新增字段，但不能改变已有字段的类型。若第一份带 category 的文档
        先落地，OpenSearch 的动态映射会把它建成 text + keyword 子字段，此后改成
        keyword 会报 mapper [category] cannot be changed from type [text] to
        [keyword]，只能新建索引并重导数据。

        索引已存在且 category 类型不符时**明确报错**：静默继续的后果是查询侧按
        裸字段名 term: {category: ...} 过滤时大批分类静默返回错数据，且没有任何
        异常提示——那正是这类缺陷最难被发现的地方。
        """
        index = self.out_index
        required_fields = {'category': {'type': 'keyword', 'normalizer': 'lowercase'}}

        if not es_client.indices.exists(index=index):
            es_client.indices.create(
                index=index,
                body={'mappings': {'properties': {k: dict(v) for k, v in required_fields.items()}}})
            logger.info("已创建汇总索引 %s，并声明字段 %s", index, sorted(required_fields))
            return 'created'

        current = es_client.indices.get_mapping(index=index)
        properties = ((current.get(index) or {}).get('mappings') or {}).get('properties') or {}

        mismatched = []
        missing = {}
        for field, declared in required_fields.items():
            actual = properties.get(field)
            if actual is None:
                missing[field] = declared
            elif actual.get('type') != declared['type']:
                mismatched.append((field, actual.get('type'), declared['type']))

        if mismatched:
            detail = "; ".join("%s 现为 %s，要求 %s" % (f, a, d) for f, a, d in mismatched)
            raise ValueError(
                "汇总索引 %s 的字段类型与要求不符，拒绝继续写入：%s。"
                "已有字段的类型无法修改，需新建索引并重导数据；继续写入会让查询侧"
                "按裸字段名过滤时静默返回错数据。" % (index, detail))

        if missing:
            es_client.indices.put_mapping(index=index, body={'properties': missing})
            logger.info("已为汇总索引 %s 补充字段 %s", index, sorted(missing))
            return 'field_added'

        return 'already_ok'

    def metrics_model_summary(self, elastic_url, category_scopes=None,
                              category_source_commit=None,
                              category_source_digest=None):
        is_https = urlparse(elastic_url).scheme == 'https'
        self.es_in = Elasticsearch(
            elastic_url, use_ssl=is_https, verify_certs=False, connection_class=RequestsHttpConnection)
        self.es_out = ElasticSearch(elastic_url, self.out_index)
        date_list = get_date_list(self.from_date, self.end_date)

        # 分类集合由调用方传入 —— 成员名单来自上游 compass-projects-information
        # 的 collections/*.yml，汇总层并不认识这份数据，故不由本层自行读取。
        # 不传时退化为 [(None, None)]，即原有的"一天一条全局"，行为完全不变。
        scopes = list(category_scopes.items()) if category_scopes else [(None, None)]
        if category_scopes:
            # 必须在首次写入分类文档之前完成，理由见 ensure_summary_index_mapping
            self.ensure_summary_index_mapping(self.es_in)

        item_datas = []
        for date in date_list:
            print(str(date) + "--" + self.summary_name)
            for category, category_urls in scopes:
                response = self.metrics_model_summary_query(date, category, category_urls)
                summary_data = self.metrics_model_after_query(response)['res']
                summary_meta = {
                    'uuid': get_uuid(str(date), self.summary_name, category),
                    'model_name': self.summary_name,
                    'grimoire_creation_date': date.isoformat(),
                    'metadata__enriched_on': datetime_utcnow().isoformat(),
                    # A06「统计单位明确」：一个单位是一个**项目**。
                    # repo 层级下 label 就是仓库 URL，故统计的单位是项目本身。
                    # 全局与分类文档都写，两种模式的单位都要说得清。
                    'stat_unit': 'project',
                }
                if category is not None:
                    summary_meta['category'] = category
                    # A06「统计单位明确」：样本量按**不同项目**计。
                    # 名单里若有重复条目，直接取 len() 会让样本量虚高。
                    summary_meta['category_member_count'] = len(set(category_urls or []))
                    # A06「类别版本明确」：提交哈希记「哪一版仓库」，
                    # 摘要记「哪一份名单」；两者都为 None 时不写，让缺失可见。
                    if category_source_commit is not None:
                        summary_meta['category_source_commit'] = category_source_commit
                    if category_source_digest is not None:
                        summary_meta['category_source_digest'] = category_source_digest
                summary_item = {**summary_meta, **summary_data}
                item_datas.append(summary_item)
                if len(item_datas) > MAX_BULK_UPDATE_SIZE:
                    self.es_out.bulk_upload(item_datas, "uuid")
                    item_datas = []
        self.es_out.bulk_upload(item_datas, "uuid")

class ActivityMetricsSummary(MetricsSummary):
    def summary_fields(self):
        return [
            'activity_score',
            'contributor_count',
            'active_C2_contributor_count',
            'active_C1_pr_create_contributor',
            'active_C1_pr_comments_contributor',
            'active_C1_issue_create_contributor',
            'active_C1_issue_comments_contributor',
            'commit_frequency',
            'org_count',
            'created_since',
            'comment_frequency',
            'code_review_count',
            'updated_since',
            'closed_issues_count',
            'updated_issues_count',
            'recent_releases_count'
        ]

class CommunitySupportMetricsSummary(MetricsSummary):
    def summary_fields(self):
        return [
            'community_support_score',
            'issue_first_reponse_avg',
            'issue_first_reponse_mid',
            'issue_open_time_avg',
            'issue_open_time_mid',
            'bug_issue_open_time_avg',
            'bug_issue_open_time_mid',
            'pr_open_time_avg',
            'pr_open_time_mid',
            'pr_first_response_time_avg',
            'pr_first_response_time_mid',
            'comment_frequency',
            'code_review_count',
            'updated_issues_count',
            'closed_prs_count'
        ]

class CodeQualityGuaranteeMetricsSummary(MetricsSummary):
    def summary_fields(self):
        return [
            'code_quality_guarantee',
            'contributor_count',
            'active_C2_contributor_count',
            'active_C1_pr_create_contributor',
            'active_C1_pr_comments_contributor',
            'commit_frequency',
            'commit_frequency_inside',
            'is_maintained',
            'LOC_frequency',
            'lines_added_frequency',
            'lines_removed_frequency',
            'pr_issue_linked_ratio',
            'code_review_ratio',
            'code_merge_ratio',
            'pr_count',
            'pr_merged_count',
            'pr_commit_count',
            'pr_commit_linked_count',
            'git_pr_linked_ratio'
        ]

class OrganizationsActivityMetricsSummary(MetricsSummary):
    def summary_fields(self):
        return [
            'organizations_activity',
            'contributor_count',
            'commit_frequency',
            'org_count',
            'contribution_last'
        ]

    def metrics_model_summary_query(self, date=None, category=None, category_urls=None):
        # 复用基类的过滤条件（含可选分类），再追加本模型特有的 is_org。
        # 不这样做的话，传入分类会被静默忽略——返回全局值却声称是分类值。
        filters = self.summary_query_filters(date, category_urls) + [
            {
                "term": {
                    "is_org": True
                }
            }
        ]
        query = {
            "size": 0,
            "from": 0,
            "query": {
                "bool": {
                    "filter": filters
                }
            },
            "aggs": self.apply_stat_method(self.summary_fields())
        }
        body = self.es_in.search(index=self.metric_index, body=query)
        return body

