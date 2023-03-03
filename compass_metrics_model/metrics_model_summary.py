
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

    def metrics_model_summary_query(self, date=None):
        query = {
            "size": 0,
            "from": 0,
            "query": {
                "bool": {
                    "filter": [
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
                }
            },
            "aggs": self.apply_stat_method(self.summary_fields())
        }
        body = self.es_in.search(index=self.metric_index, body=query)
        return body

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

    def metrics_model_summary(self, elastic_url):
        is_https = urlparse(elastic_url).scheme == 'https'
        self.es_in = Elasticsearch(
            elastic_url, use_ssl=is_https, verify_certs=False, connection_class=RequestsHttpConnection)
        self.es_out = ElasticSearch(elastic_url, self.out_index)
        date_list = get_date_list(self.from_date, self.end_date)

        item_datas = []
        for date in date_list:
            print(str(date) + "--" + self.summary_name)
            response = self.metrics_model_summary_query(date)
            summary_data = self.metrics_model_after_query(response)['res']
            summary_meta = {
                'uuid': get_uuid(str(date), self.summary_name),
                'model_name': self.summary_name,
                'grimoire_creation_date': date.isoformat(),
                'metadata__enriched_on': datetime_utcnow().isoformat()
            }
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

    def metrics_model_summary_query(self, date=None):
        query = {
            "size": 0,
            "from": 0,
            "query": {
                "bool": {
                    "filter": [
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
                        },
                        {
                            "term": {
                                "is_org": True
                            }
                        }
                    ]
                }
            },
            "aggs": self.apply_stat_method(self.summary_fields())
        }
        body = self.es_in.search(index=self.metric_index, body=query)
        return body

