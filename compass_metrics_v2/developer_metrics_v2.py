from compass_metrics.db_dsl import get_contributor_query, get_uuid_count_query
from compass_common.datetime import check_times_has_overlap
from compass_common.opensearch_utils import get_all_index_data
from datetime import timedelta
from itertools import groupby
import pandas as pd
import datetime

from dateutil.relativedelta import relativedelta



def get_period_range(end_date: datetime, period: str):
    if period not in ("month", "quarter", "year"):
        raise ValueError("period must be one of: month, quarter, year")

    if period == "month":
        start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == "year":
        start_date = end_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:  # quarter
        month = ((end_date.month - 1) // 3) * 3 + 1
        start_date = end_date.replace(month=month, day=1, hour=0, minute=0, second=0, microsecond=0)

    if period == "month":
        # 下个月的第一天减去 1 秒（或1天）
        if end_date.month == 12:
            next_month = end_date.replace(year=end_date.year + 1, month=1, day=1)
        else:
            next_month = end_date.replace(month=end_date.month + 1, day=1)
        actual_end_date = next_month - timedelta(seconds=1)

    elif period == "year":
        actual_end_date = end_date.replace(month=12, day=31, hour=23, minute=59, second=59)

    else:  # quarter
        quarter_end_month = ((end_date.month - 1) // 3) * 3 + 3
        if quarter_end_month == 12:
            next_start = end_date.replace(year=end_date.year + 1, month=1, day=1)
        else:
            next_start = end_date.replace(month=quarter_end_month + 1, day=1)
        actual_end_date = next_start - timedelta(seconds=1)

    return start_date, actual_end_date


def get_previous_period_range(end_date: datetime, period: str):
    """
    返回上一个完整周期的起止时间，用于获取上周期累计值。
    """
    current_start, _ = get_period_range(end_date, period)
    if period == "month":
        prev_end = current_start - timedelta(microseconds=1)
        prev_start = (current_start - relativedelta(months=1)).replace(day=1)
    elif period == "year":
        prev_end = current_start - timedelta(microseconds=1)
        prev_start = (current_start - relativedelta(years=1)).replace(month=1, day=1)
    else:  # quarter
        prev_end = current_start - timedelta(microseconds=1)
        prev_start = (current_start - relativedelta(months=3)).replace(day=1)
    return prev_start, prev_end


def _base_contributor_query(repo_list, from_date, to_date, additional_filters=None):
    """基础贡献者查询，过滤机器人和时间范围"""
    query = {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {"terms": {"repo_name.keyword": repo_list}},
                    {"range": {"grimoire_creation_date": {"gte": from_date.isoformat(), "lt": to_date.isoformat()}}},
                    {"match_phrase": {"is_bot": "false"}}
                ]
            }
        }
    }
    if additional_filters:
        query["query"]["bool"]["must"].extend(additional_filters)
    return query


def _get_contributor_cardinality(client, index, query, field="contributor.keyword"):
    """获取贡献者去重数量"""
    query_copy = query.copy()
    query_copy["aggs"] = {
        "count": {
            "cardinality": {
                "field": field,
                "precision_threshold": 100000
            }
        }
    }
    result = client.search(index=index, body=query_copy)
    return result["aggregations"]["count"]["value"]


def _get_contribution_sum(client, index, query):
    """获取贡献量总和"""
    query_copy = query.copy()
    query_copy["aggs"] = {
        "total_contribution": {
            "sum": {"field": "contribution"}
        }
    }
    result = client.search(index=index, body=query_copy)
    return result["aggregations"]["total_contribution"]["value"]


def total_active_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """
    总活跃贡献者数：周期内有任何贡献行为的去重用户数。
    """
    from_date, to_date = get_period_range(end_date, period)
    query = _base_contributor_query(repo_list, from_date, to_date)
    count = _get_contributor_cardinality(client, contributors_enriched_index, query)
    return {"total_active_contributors": count, "period": period}


def code_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """
    活跃代码贡献者：周期内有代码提交或PR合并或PR评论的去重用户数。
    """
    from_date, to_date = get_period_range(end_date, period)
    code_types = ["pr_creation", "pr_comments", "code_author", "code_committer", "pr_merged"]
    query = _base_contributor_query(repo_list, from_date, to_date, [
        {"terms": {"contribution_type_list.contribution_type.keyword": code_types}}
    ])
    count = _get_contributor_cardinality(client, contributors_enriched_index, query)
    return {"code_contributors": count, "period": period}


def non_code_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """
    活跃非代码贡献者：周期内仅参与讨论但未提交代码的用户数。
    计算：总活跃贡献者 - 代码贡献者
    """
    total = total_active_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period)[
        "total_active_contributors"]
    code = code_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period)[
        "code_contributors"]
    non_code = total - code
    return {"non_code_contributors": max(0, non_code), "period": period}


def participating_orgs_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """
    参与贡献的组织个数：周期内参与贡献的组织个数。
    """
    from_date, to_date = get_period_range(end_date, period)
    query = _base_contributor_query(repo_list, from_date, to_date, [
        {"exists": {"field": "organization"}},
        {"match_phrase": {"ecological_type": "organization"}}
    ])
    count = _get_contributor_cardinality(client, contributors_enriched_index, query, "organization.keyword")
    return {"participating_orgs": count, "period": period}


def org_code_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """
    组织代码贡献者数量：周期内参与代码贡献的组织贡献者个数。
    """
    from_date, to_date = get_period_range(end_date, period)
    code_types = ["pr_creation", "pr_comments", "code_author", "code_committer", "pr_merged"]
    query = _base_contributor_query(repo_list, from_date, to_date, [
        {"terms": {"contribution_type_list.contribution_type.keyword": code_types}},
        {"match_phrase": {"ecological_type": "organization"}}
    ])
    count = _get_contributor_cardinality(client, contributors_enriched_index, query)
    return {"org_code_contributors": count, "period": period}


def org_code_contributors_ratio_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """
    组织代码贡献者数量占比：周期内组织代码贡献者数量占总代码贡献者数量的比例。
    """
    total_code = code_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period)[
        "code_contributors"]
    org_code = org_code_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period)[
        "org_code_contributors"]
    ratio = (org_code / total_code) if total_code > 0 else None
    return {
        "org_code_contributors_ratio": ratio,
        "org_code_contributors": org_code,
        "total_code_contributors": total_code,
        "period": period
    }


def org_non_code_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """
    组织非代码贡献者数量：周期内参与非代码贡献的组织贡献者个数。
    """
    from_date, to_date = get_period_range(end_date, period)
    # 非代码贡献类型：排除代码相关的贡献类型
    code_types = ["pr_creation", "pr_comments", "code_author", "code_committer", "pr_merged"]
    query = _base_contributor_query(repo_list, from_date, to_date, [
        {"match_phrase": {"ecological_type": "organization"}}
    ])
    # 使用脚本过滤掉有代码贡献的用户
    query["query"]["bool"]["must_not"] = [
        {"terms": {"contribution_type_list.contribution_type.keyword": code_types}}
    ]
    count = _get_contributor_cardinality(client, contributors_enriched_index, query)
    return {"org_non_code_contributors": count, "period": period}


def org_non_code_contributors_ratio_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """
    组织非代码贡献者数量占比：周期内组织非代码贡献者占总非代码贡献者数量的比例。
    """
    total_non_code = non_code_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period)[
        "non_code_contributors"]
    org_non_code = \
        org_non_code_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period)[
            "org_non_code_contributors"]
    ratio = (org_non_code / total_non_code) if total_non_code > 0 else None
    return {
        "org_non_code_contributors_ratio": ratio,
        "org_non_code_contributors": org_non_code,
        "total_non_code_contributors": total_non_code,
        "period": period
    }


def org_non_code_contribution_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """
    组织非代码贡献量：周期内组织非代码贡献量。
    """
    from_date, to_date = get_period_range(end_date, period)
    code_types = ["pr_creation", "pr_comments", "code_author", "code_committer", "pr_merged"]
    query = _base_contributor_query(repo_list, from_date, to_date, [
        {"match_phrase": {"ecological_type": "organization"}}
    ])
    query["query"]["bool"]["must_not"] = [
        {"terms": {"contribution_type_list.contribution_type.keyword": code_types}}
    ]
    total = _get_contribution_sum(client, contributors_enriched_index, query)
    return {"org_non_code_contribution": total, "period": period}


def org_non_code_contribution_ratio_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """
    组织非代码贡献量占比：周期内组织非代码贡献量占总非代码贡献量的比例。
    """
    from_date, to_date = get_period_range(end_date, period)
    code_types = ["pr_creation", "pr_comments", "code_author", "code_committer", "pr_merged"]
    # 总非代码贡献量
    total_query = _base_contributor_query(repo_list, from_date, to_date)
    total_query["query"]["bool"]["must_not"] = [
        {"terms": {"contribution_type_list.contribution_type.keyword": code_types}}
    ]
    total_non_code = _get_contribution_sum(client, contributors_enriched_index, total_query)

    # 组织非代码贡献量
    org_non_code = \
        org_non_code_contribution_by_period(client, contributors_enriched_index, end_date, repo_list, period)[
            "org_non_code_contribution"]

    ratio = (org_non_code / total_non_code) if total_non_code > 0 else None
    return {
        "org_non_code_contribution_ratio": ratio,
        "org_non_code_contribution": org_non_code,
        "total_non_code_contribution": total_non_code,
        "period": period
    }


def governance_orgs_by_period(client, contributors_enriched_index, end_date, repo_list, period="month",
                              exclude_orgs=None):
    """
    参与治理的组织数：周期内在社区治理角色中，来自非社区发起组织的去重组织数量。
    exclude_orgs: 社区发起组织的名单列表
    """
    from_date, to_date = get_period_range(end_date, period)
    query = _base_contributor_query(repo_list, from_date, to_date, [
        {"terms": {"ecological_type.keyword": ["organization manager", "organization participant"]}}
    ])
    if exclude_orgs:
        query["query"]["bool"]["must_not"] = [
            {"terms": {"organization.keyword": exclude_orgs}}
        ]
    count = _get_contributor_cardinality(client, contributors_enriched_index, query, "organization.keyword")
    return {"governance_orgs": count, "period": period}


def org_managers_by_period(client, contributors_enriched_index, end_date, repo_list, period="month", exclude_orgs=None):
    """
    组织管理者数量：周期内在社区治理角色中，来自非社区发起组织的去重管理者数量。
    """
    from_date, to_date = get_period_range(end_date, period)
    query = _base_contributor_query(repo_list, from_date, to_date, [
        {"match_phrase": {"ecological_type": "organization manager"}}
    ])
    if exclude_orgs:
        query["query"]["bool"]["must_not"] = [
            {"terms": {"organization.keyword": exclude_orgs}}
        ]
    count = _get_contributor_cardinality(client, contributors_enriched_index, query)
    return {"org_managers": count, "period": period}


def org_managers_ratio_by_period(client, contributors_enriched_index, end_date, repo_list, period="month",
                                 exclude_orgs=None):
    """
    组织管理者数量占比：周期内在社区治理角色中，来自组织的管理者数量占总管理者数量的比例。
    """
    from_date, to_date = get_period_range(end_date, period)
    # 总管理者数量
    total_query = _base_contributor_query(repo_list, from_date, to_date, [
        {"terms": {"ecological_type.keyword": ["organization manager", "individual manager"]}}
    ])
    if exclude_orgs:
        total_query["query"]["bool"]["must_not"] = [
            {"terms": {"organization.keyword": exclude_orgs}}
        ]
    total_managers = _get_contributor_cardinality(client, contributors_enriched_index, total_query)

    # 组织管理者数量
    org_managers = \
        org_managers_by_period(client, contributors_enriched_index, end_date, repo_list, period, exclude_orgs)[
            "org_managers"]

    ratio = (org_managers / total_managers) if total_managers > 0 else None
    return {
        "org_managers_ratio": ratio,
        "org_managers": org_managers,
        "total_managers": total_managers,
        "period": period
    }


def individual_code_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """
    个人代码贡献者数量：周期内有代码贡献行为的个人贡献者数量。
    """
    from_date, to_date = get_period_range(end_date, period)
    code_types = ["pr_creation", "pr_comments", "code_author", "code_committer", "pr_merged"]
    query = _base_contributor_query(repo_list, from_date, to_date, [
        {"terms": {"contribution_type_list.contribution_type.keyword": code_types}},
        {"match_phrase": {"ecological_type": "individual participant"}}
    ])
    count = _get_contributor_cardinality(client, contributors_enriched_index, query)
    return {"individual_code_contributors": count, "period": period}


def individual_code_contributors_ratio_by_period(client, contributors_enriched_index, end_date, repo_list,
                                                 period="month"):
    """
    个人代码贡献者数量占比：周期内个人代码贡献者数量占总代码贡献者数量的比例。
    """
    total_code = code_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period)[
        "code_contributors"]
    individual_code = \
        individual_code_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period)[
            "individual_code_contributors"]
    ratio = (individual_code / total_code) if total_code > 0 else None
    return {
        "individual_code_contributors_ratio": ratio,
        "individual_code_contributors": individual_code,
        "total_code_contributors": total_code,
        "period": period
    }


def individual_non_code_contributors_by_period(client, contributors_enriched_index, end_date, repo_list,
                                               period="month"):
    """
    个人非代码贡献者数量：周期内仅参与非代码贡献行为的个人贡献者数量。
    """
    from_date, to_date = get_period_range(end_date, period)
    code_types = ["pr_creation", "pr_comments", "code_author", "code_committer", "pr_merged"]
    query = _base_contributor_query(repo_list, from_date, to_date, [
        {"match_phrase": {"ecological_type": "individual participant"}}
    ])
    query["query"]["bool"]["must_not"] = [
        {"terms": {"contribution_type_list.contribution_type.keyword": code_types}}
    ]
    count = _get_contributor_cardinality(client, contributors_enriched_index, query)
    return {"individual_non_code_contributors": count, "period": period}


def individual_non_code_contributors_ratio_by_period(client, contributors_enriched_index, end_date, repo_list,
                                                     period="month"):
    """
    个人非代码贡献者数量占比：周期内个人非代码贡献者数量占总非代码贡献者数量的比例。
    """
    total_non_code = non_code_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period)[
        "non_code_contributors"]
    individual_non_code = \
        individual_non_code_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period)[
            "individual_non_code_contributors"]
    ratio = (individual_non_code / total_non_code) if total_non_code > 0 else None
    return {
        "individual_non_code_contributors_ratio": ratio,
        "individual_non_code_contributors": individual_non_code,
        "total_non_code_contributors": total_non_code,
        "period": period
    }


def individual_non_code_contribution_by_period(client, contributors_enriched_index, end_date, repo_list,
                                               period="month"):
    """
    个人非代码贡献量：周期内个人贡献者提交的非代码贡献总次数。
    """
    from_date, to_date = get_period_range(end_date, period)
    code_types = ["pr_creation", "pr_comments", "code_author", "code_committer", "pr_merged"]
    query = _base_contributor_query(repo_list, from_date, to_date, [
        {"match_phrase": {"ecological_type": "individual participant"}}
    ])
    query["query"]["bool"]["must_not"] = [
        {"terms": {"contribution_type_list.contribution_type.keyword": code_types}}
    ]
    total = _get_contribution_sum(client, contributors_enriched_index, query)
    return {"individual_non_code_contribution": total, "period": period}


def individual_non_code_contribution_ratio_by_period(client, contributors_enriched_index, end_date, repo_list,
                                                     period="month"):
    """
    个人非代码贡献量占比：周期内个人非代码贡献量占非代码总贡献量的比例。
    """
    from_date, to_date = get_period_range(end_date, period)
    code_types = ["pr_creation", "pr_comments", "code_author", "code_committer", "pr_merged"]
    # 总非代码贡献量
    total_query = _base_contributor_query(repo_list, from_date, to_date)
    total_query["query"]["bool"]["must_not"] = [
        {"terms": {"contribution_type_list.contribution_type.keyword": code_types}}
    ]
    total_non_code = _get_contribution_sum(client, contributors_enriched_index, total_query)

    # 个人非代码贡献量
    individual_non_code = \
        individual_non_code_contribution_by_period(client, contributors_enriched_index, end_date, repo_list, period)[
            "individual_non_code_contribution"]

    ratio = (individual_non_code / total_non_code) if total_non_code > 0 else None
    return {
        "individual_non_code_contribution_ratio": ratio,
        "individual_non_code_contribution": individual_non_code,
        "total_non_code_contribution": total_non_code,
        "period": period
    }


def individual_managers_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """
    个人管理者数量：周期内在社区治理角色中，来自个人的去重管理者数量。
    """
    from_date, to_date = get_period_range(end_date, period)
    query = _base_contributor_query(repo_list, from_date, to_date, [
        {"match_phrase": {"ecological_type": "individual manager"}}
    ])
    count = _get_contributor_cardinality(client, contributors_enriched_index, query)
    return {"individual_managers": count, "period": period}


def individual_managers_ratio_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """
    个人管理者数量占比：周期内在社区治理角色中，来自个人的管理者数量占总管理者数量的比例。
    """
    from_date, to_date = get_period_range(end_date, period)
    # 总管理者数量
    total_query = _base_contributor_query(repo_list, from_date, to_date, [
        {"terms": {"ecological_type.keyword": ["organization manager", "individual manager"]}}
    ])
    total_managers = _get_contributor_cardinality(client, contributors_enriched_index, total_query)

    # 个人管理者数量
    individual_managers = \
        individual_managers_by_period(client, contributors_enriched_index, end_date, repo_list, period)[
            "individual_managers"]

    ratio = (individual_managers / total_managers) if total_managers > 0 else None
    return {
        "individual_managers_ratio": ratio,
        "individual_managers": individual_managers,
        "total_managers": total_managers,
        "period": period
    }


def contributor_list_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """
    Contributor 列表：周期内在社区治理角色中，来自个人的管理者列表。
    """
    from_date, to_date = get_period_range(end_date, period)
    query = _base_contributor_query(repo_list, from_date, to_date, [
        {"terms": {"ecological_type.keyword": ["organization manager", "individual manager"]}}
    ])
    query["size"] = 1000
    query["_source"] = ["contributor", "organization", "ecological_type", "contribution"]

    result = client.search(index=contributors_enriched_index, body=query)
    contributors = []
    for hit in result["hits"]["hits"]:
        src = hit["_source"]
        contributors.append({
            "contributor": src.get("contributor"),
            "organization": src.get("organization"),
            "ecological_type": src.get("ecological_type"),
            "contribution": src.get("contribution")
        })

    return {
        "contributor_list": contributors,
        "total_managers": len(contributors),
        "period": period
    }


# =========================
# 开发者吸引、成长、晋升、留存 指标 (Developer Attraction, Growth, Promotion, Retention)
# =========================

CODE_CONTRIBUTION_TYPES = ["pr_creation", "pr_comments", "code_author", "code_committer", "pr_merged"]
ISSUE_CONTRIBUTION_TYPES = ["issue_creation", "issue_comments"]
ORG_ECOLOGICAL_TYPES = ["organization manager", "organization participant"]
INDIVIDUAL_ECOLOGICAL_TYPES = ["individual manager", "individual participant"]


def _get_contributor_set_in_period(client, contributors_enriched_index, repo_list, from_date, to_date,
                                   code_only=None, org_only=None, max_buckets=10000):
    """
    获取周期内贡献者集合。code_only: True=仅代码, False=仅非代码, None=全部。
    org_only: True=仅组织, False=仅个人, None=全部。
    """
    must = [
        {"terms": {"repo_name.keyword": repo_list}},
        {"range": {"grimoire_creation_date": {"gte": from_date.isoformat(), "lt": to_date.isoformat()}}},
        {"match_phrase": {"is_bot": "false"}}
    ]
    if code_only is True:
        must.append({"terms": {"contribution_type_list.contribution_type.keyword": CODE_CONTRIBUTION_TYPES}})
    elif code_only is False:
        must.append({"bool": {
            "must_not": [{"terms": {"contribution_type_list.contribution_type.keyword": CODE_CONTRIBUTION_TYPES}}]}})
    if org_only is True:
        must.append({"terms": {"ecological_type.keyword": ORG_ECOLOGICAL_TYPES}})
    elif org_only is False:
        must.append({"terms": {"ecological_type.keyword": INDIVIDUAL_ECOLOGICAL_TYPES}})

    query = {"size": 0, "query": {"bool": {"must": must}}}
    query["aggs"] = {"contributors": {"terms": {"field": "contributor.keyword", "size": max_buckets}}}
    res = client.search(index=contributors_enriched_index, body=query)
    buckets = res.get("aggregations", {}).get("contributors", {}).get("buckets", [])
    return {b["key"] for b in buckets}


def _get_org_set_in_period(client, contributors_enriched_index, repo_list, from_date, to_date, max_buckets=10000):
    """获取周期内参与贡献的组织集合。"""
    query = {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {"terms": {"repo_name.keyword": repo_list}},
                    {"range": {"grimoire_creation_date": {"gte": from_date.isoformat(), "lt": to_date.isoformat()}}},
                    {"match_phrase": {"is_bot": "false"}},
                    {"terms": {"ecological_type.keyword": ORG_ECOLOGICAL_TYPES}},
                    {"exists": {"field": "organization"}}
                ]
            }
        },
        "aggs": {"orgs": {"terms": {"field": "organization.keyword", "size": max_buckets}}}
    }
    res = client.search(index=contributors_enriched_index, body=query)
    buckets = res.get("aggregations", {}).get("orgs", {}).get("buckets", [])
    return {b["key"] for b in buckets}


def developer_background_profile(client, contributors_enriched_index, repo_list, from_date=None, to_date=None):
    """
    开发者背景画像：基于公开元数据识别开发者的地理位置、组织及关联社区标签。
    输入：用户公开元数据（Location, Company, Bio, Email）
    输出：结构化标签（Region, Organization, Communities）
    """
    if to_date is None:
        to_date = datetime.datetime.utcnow()
    if from_date is None:
        from_date = to_date - timedelta(days=90)
    query = {
        "size": 500,
        "query": {
            "bool": {
                "must": [
                    {"terms": {"repo_name.keyword": repo_list}},
                    {"range": {"grimoire_creation_date": {"gte": from_date.isoformat(), "lt": to_date.isoformat()}}},
                    {"match_phrase": {"is_bot": "false"}}
                ]
            }
        },
        "_source": ["contributor", "organization", "location", "company", "bio", "email", "ecological_type"],
        "aggs": {"by_contributor": {"terms": {"field": "contributor.keyword", "size": 1000}}}
    }
    res = client.search(index=contributors_enriched_index, body=query)
    profiles = []
    for hit in res.get("hits", {}).get("hits", []):
        s = hit.get("_source", {})
        profiles.append({
            "contributor": s.get("contributor"),
            "region": s.get("location"),
            "organization": s.get("organization") or s.get("company"),
            "communities": s.get("bio"),  # 可扩展为从 bio/email 解析社区标签
            "period": None
        })
    return {"developer_background_profile": profiles[:100], "period": None}


def developer_skill_profile(client, contributors_enriched_index, git_index, repo_list, from_date=None, to_date=None):
    """
    开发者技能画像：基于代码贡献特征识别技术栈、专注领域及能力角色。
    输入：commit 详情；输出：技能标签集（例：{Lang: Go, Domain: CloudNative}）。
    此处返回占位结构，实际需结合 commit 语言/文件路径等分析。
    """
    return {"developer_skill_profile": [], "period": None, "note": "需结合 commit 语言/文件路径等实现"}


def developer_willingness_profile(client, contributors_enriched_index, repo_list, from_date=None, to_date=None):
    """
    开发者意愿画像：情绪极性、友好度。需结合评论/Issue 文本分析，此处返回占位。
    """
    return {"developer_willingness_profile": [], "period": None, "note": "需结合评论/Issue 文本分析实现"}


def new_org_count_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """
    新增参与贡献的组织个数：本周期内首次产生有效贡献（代码或 Issue）的组织去重数量。
    输入：本周期活跃组织列表 - 历史所有周期组织列表。
    """
    from_date, to_date = get_period_range(end_date, period)
    current_orgs = _get_org_set_in_period(client, contributors_enriched_index, repo_list, from_date, to_date)
    historical_start = datetime.datetime(2000, 1, 1)
    historical_orgs = _get_org_set_in_period(client, contributors_enriched_index, repo_list, historical_start,
                                             from_date)
    new_orgs = current_orgs - historical_orgs
    return {"new_org_count": len(new_orgs), "period": period}


def new_org_code_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """
    新增组织代码开发者数量：本周期内首次产生代码贡献的组织成员数量。
    """
    from_date, to_date = get_period_range(end_date, period)
    current_set = _get_contributor_set_in_period(client, contributors_enriched_index, repo_list, from_date, to_date,
                                                 code_only=True, org_only=True)
    historical_start = datetime.datetime(2000, 1, 1)
    historical_set = _get_contributor_set_in_period(client, contributors_enriched_index, repo_list, historical_start,
                                                    from_date, code_only=True, org_only=True)
    new_count = len(current_set - historical_set)
    return {"new_org_code_contributors": new_count, "period": period}


def new_org_non_code_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """
    新增组织非代码开发者数量：本周期内首次产生非代码贡献的组织成员数量。
    """
    from_date, to_date = get_period_range(end_date, period)
    current_set = _get_contributor_set_in_period(client, contributors_enriched_index, repo_list, from_date, to_date,
                                                 code_only=False, org_only=True)
    historical_start = datetime.datetime(2000, 1, 1)
    historical_set = _get_contributor_set_in_period(client, contributors_enriched_index, repo_list, historical_start,
                                                    from_date, code_only=False, org_only=True)
    new_count = len(current_set - historical_set)
    return {"new_org_non_code_contributors": new_count, "period": period}


def new_individual_code_contributors_by_period(client, contributors_enriched_index, end_date, repo_list,
                                               period="month"):
    """
    新增个人代码开发者数量：本周期内首次产生代码贡献的个人开发者数量。
    """
    from_date, to_date = get_period_range(end_date, period)
    current_set = _get_contributor_set_in_period(client, contributors_enriched_index, repo_list, from_date, to_date,
                                                 code_only=True, org_only=False)
    historical_start = datetime.datetime(2000, 1, 1)
    historical_set = _get_contributor_set_in_period(client, contributors_enriched_index, repo_list, historical_start,
                                                    from_date, code_only=True, org_only=False)
    new_count = len(current_set - historical_set)
    return {"new_individual_code_contributors": new_count, "period": period}


def new_individual_non_code_contributors_by_period(client, contributors_enriched_index, end_date, repo_list,
                                                   period="month"):
    """
    新增个人非代码开发者数量：本周期内首次产生非代码贡献的个人开发者数量。
    """
    from_date, to_date = get_period_range(end_date, period)
    current_set = _get_contributor_set_in_period(client, contributors_enriched_index, repo_list, from_date, to_date,
                                                 code_only=False, org_only=False)
    historical_start = datetime.datetime(2000, 1, 1)
    historical_set = _get_contributor_set_in_period(client, contributors_enriched_index, repo_list, historical_start,
                                                    from_date, code_only=False, org_only=False)
    new_count = len(current_set - historical_set)
    return {"new_individual_non_code_contributors": new_count, "period": period}


def _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list, from_date, to_date,
                                                 org_only=None):
    """
    获取周期内每个贡献者的代码贡献量和 Issue 贡献量（用于分层）。
    返回 (contributor -> code_contribution), (contributor -> issue_contribution)，仅包含有贡献的 contributor。
    """
    query = {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {"terms": {"repo_name.keyword": repo_list}},
                    {"range": {"grimoire_creation_date": {"gte": from_date.isoformat(), "lt": to_date.isoformat()}}},
                    {"match_phrase": {"is_bot": "false"}}
                ]
            }
        },
        "aggs": {
            "by_contributor": {
                "terms": {"field": "contributor.keyword", "size": 10000},
                "aggs": {
                    "code_sum": {
                        "filter": {
                            "terms": {"contribution_type_list.contribution_type.keyword": CODE_CONTRIBUTION_TYPES}},
                        "aggs": {"s": {"sum": {"field": "contribution"}}}
                    },
                    "issue_sum": {
                        "filter": {
                            "terms": {"contribution_type_list.contribution_type.keyword": ISSUE_CONTRIBUTION_TYPES}},
                        "aggs": {"s": {"sum": {"field": "contribution"}}}
                    }
                }
            }
        }
    }
    if org_only is True:
        query["query"]["bool"]["must"].append({"terms": {"ecological_type.keyword": ORG_ECOLOGICAL_TYPES}})
    elif org_only is False:
        query["query"]["bool"]["must"].append({"terms": {"ecological_type.keyword": INDIVIDUAL_ECOLOGICAL_TYPES}})

    res = client.search(index=contributors_enriched_index, body=query)
    code_map = {}
    issue_map = {}
    for b in res.get("aggregations", {}).get("by_contributor", {}).get("buckets", []):
        key = b["key"]
        code_map[key] = b.get("code_sum", {}).get("s", {}).get("value") or 0
        issue_map[key] = b.get("issue_sum", {}).get("s", {}).get("value") or 0
    return code_map, issue_map


def _tier_counts_from_contribution_map(contribution_map, core_ratio=0.5, regular_end_ratio=0.8):
    """
    根据贡献量占比划分 core / regular / visitor，返回 (core_count, regular_count, visitor_count)。
    core: 累计贡献占比前 50% 的开发者；regular: 累计 50%–80%（即常客 20%–50% 贡献）；visitor: 剩余 <20%。
    """
    if not contribution_map:
        return 0, 0, 0
    total = sum(contribution_map.values())
    if total == 0:
        return 0, 0, len(contribution_map)
    sorted_contributors = sorted(contribution_map.items(), key=lambda x: -x[1])
    cum = 0.0
    core_count = regular_count = visitor_count = 0
    for _, v in sorted_contributors:
        cum += v
        ratio = cum / total
        if ratio <= core_ratio:
            core_count += 1
        elif ratio <= regular_end_ratio:
            regular_count += 1
        else:
            visitor_count += 1
    return core_count, regular_count, visitor_count


def org_code_core_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """组织代码核心开发者（含管理者）数量：本周期内代码贡献占比大于总代码贡献量 50% 的组织贡献者数量。"""
    from_date, to_date = get_period_range(end_date, period)
    code_map, _ = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                               from_date, to_date, org_only=True)
    core_count, _, _ = _tier_counts_from_contribution_map(code_map, core_ratio=0.5)
    return {"org_code_core_contributors": core_count, "period": period}


def org_issue_core_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """组织 Issue 核心开发者（含管理者）数量：本周期内 Issue 活跃度排名前 50% 的组织成员数量。"""
    from_date, to_date = get_period_range(end_date, period)
    _, issue_map = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                                from_date, to_date, org_only=True)
    core_count, _, _ = _tier_counts_from_contribution_map(issue_map, core_ratio=0.5)
    return {"org_issue_core_contributors": core_count, "period": period}


def org_code_regular_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """组织代码常客开发者数量：代码贡献占比 20%–50% 的组织成员。"""
    from_date, to_date = get_period_range(end_date, period)
    code_map, _ = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                               from_date, to_date, org_only=True)
    _, regular_count, _ = _tier_counts_from_contribution_map(code_map, core_ratio=0.5)
    return {"org_code_regular_contributors": regular_count, "period": period}


def org_issue_regular_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """组织 Issue 常客开发者数量：Issue 贡献处于中间层级。"""
    from_date, to_date = get_period_range(end_date, period)
    _, issue_map = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                                from_date, to_date, org_only=True)
    _, regular_count, _ = _tier_counts_from_contribution_map(issue_map, core_ratio=0.5)
    return {"org_issue_regular_contributors": regular_count, "period": period}


def org_code_visitor_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """组织代码访客开发者数量：代码贡献占比 <20%。"""
    from_date, to_date = get_period_range(end_date, period)
    code_map, _ = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                               from_date, to_date, org_only=True)
    _, _, visitor_count = _tier_counts_from_contribution_map(code_map, core_ratio=0.5)
    return {"org_code_visitor_contributors": visitor_count, "period": period}


def org_issue_visitor_contributors_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """组织 Issue 访客开发者数量：Issue 贡献低频。"""
    from_date, to_date = get_period_range(end_date, period)
    _, issue_map = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                                from_date, to_date, org_only=True)
    _, _, visitor_count = _tier_counts_from_contribution_map(issue_map, core_ratio=0.5)
    return {"org_issue_visitor_contributors": visitor_count, "period": period}


def individual_code_core_contributors_by_period(client, contributors_enriched_index, end_date, repo_list,
                                                period="month"):
    """个人代码核心开发者（含管理者）数量：本周期内代码贡献度前 50% 的个人开发者。"""
    from_date, to_date = get_period_range(end_date, period)
    code_map, _ = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                               from_date, to_date, org_only=False)
    core_count, _, _ = _tier_counts_from_contribution_map(code_map, core_ratio=0.5)
    return {"individual_code_core_contributors": core_count, "period": period}


def individual_issue_core_contributors_by_period(client, contributors_enriched_index, end_date, repo_list,
                                                 period="month"):
    """个人 Issue 核心开发者（含管理者）数量：本周期内 Issue 活跃度前 50%。"""
    from_date, to_date = get_period_range(end_date, period)
    _, issue_map = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                                from_date, to_date, org_only=False)
    core_count, _, _ = _tier_counts_from_contribution_map(issue_map, core_ratio=0.5)
    return {"individual_issue_core_contributors": core_count, "period": period}


def individual_code_regular_contributors_by_period(client, contributors_enriched_index, end_date, repo_list,
                                                   period="month"):
    """个人代码常客开发者数量：代码贡献中间层级。"""
    from_date, to_date = get_period_range(end_date, period)
    code_map, _ = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                               from_date, to_date, org_only=False)
    _, regular_count, _ = _tier_counts_from_contribution_map(code_map, core_ratio=0.5)
    return {"individual_code_regular_contributors": regular_count, "period": period}


def individual_issue_regular_contributors_by_period(client, contributors_enriched_index, end_date, repo_list,
                                                    period="month"):
    """个人 Issue 常客开发者数量：Issue 贡献 20%–50%。"""
    from_date, to_date = get_period_range(end_date, period)
    _, issue_map = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                                from_date, to_date, org_only=False)
    _, regular_count, _ = _tier_counts_from_contribution_map(issue_map, core_ratio=0.5)
    return {"individual_issue_regular_contributors": regular_count, "period": period}


def individual_code_visitor_contributors_by_period(client, contributors_enriched_index, end_date, repo_list,
                                                   period="month"):
    """个人代码访客开发者数量：代码贡献 <20%。"""
    from_date, to_date = get_period_range(end_date, period)
    code_map, _ = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                               from_date, to_date, org_only=False)
    _, _, visitor_count = _tier_counts_from_contribution_map(code_map, core_ratio=0.5)
    return {"individual_code_visitor_contributors": visitor_count, "period": period}


def individual_issue_visitor_contributors_by_period(client, contributors_enriched_index, end_date, repo_list,
                                                    period="month"):
    """个人 Issue 访客开发者数量：Issue 贡献低频 <20%。"""
    from_date, to_date = get_period_range(end_date, period)
    _, issue_map = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                                from_date, to_date, org_only=False)
    _, _, visitor_count = _tier_counts_from_contribution_map(issue_map, core_ratio=0.5)
    return {"individual_issue_visitor_contributors": visitor_count, "period": period}


def _get_core_contributor_set_from_maps(code_map, issue_map, dimension="code", core_ratio=0.5):
    """从 code_map 或 issue_map 中取贡献占比前 core_ratio 的贡献者集合。"""
    m = code_map if dimension == "code" else issue_map
    if not m:
        return set()
    total = sum(m.values())
    if total == 0:
        return set()
    sorted_contributors = sorted(m.items(), key=lambda x: -x[1])
    cum = 0
    core_set = set()
    for k, v in sorted_contributors:
        cum += v
        core_set.add(k)
        if cum >= total * core_ratio:
            break
    return core_set


def org_code_core_promotion_count_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """组织代码核心开发者（含管理者）晋升数量：上周期非核心，本周期成长为核心的组织成员数量。"""
    from_date, to_date = get_period_range(end_date, period)
    prev_start, prev_end = get_previous_period_range(end_date, period)
    code_map_t, _ = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                                 from_date, to_date, org_only=True)
    code_map_t1, _ = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                                  prev_start, prev_end, org_only=True)
    core_t = _get_core_contributor_set_from_maps(code_map_t, {}, dimension="code", core_ratio=0.5)
    core_t1 = _get_core_contributor_set_from_maps(code_map_t1, {}, dimension="code", core_ratio=0.5)
    non_core_t1 = set(code_map_t1.keys()) - core_t1
    promotion = len(core_t & non_core_t1)
    return {"org_code_core_promotion_count": promotion, "period": period}


def org_issue_core_promotion_count_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """组织 Issue 核心开发者（含管理者）晋升数量。"""
    from_date, to_date = get_period_range(end_date, period)
    prev_start, prev_end = get_previous_period_range(end_date, period)
    _, issue_map_t = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                                  from_date, to_date, org_only=True)
    _, issue_map_t1 = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                                   prev_start, prev_end, org_only=True)
    core_t = _get_core_contributor_set_from_maps({}, issue_map_t, dimension="issue", core_ratio=0.5)
    core_t1 = _get_core_contributor_set_from_maps({}, issue_map_t1, dimension="issue", core_ratio=0.5)
    non_core_t1 = set(issue_map_t1.keys()) - core_t1
    promotion = len(core_t & non_core_t1)
    return {"org_issue_core_promotion_count": promotion, "period": period}


def individual_code_core_promotion_count_by_period(client, contributors_enriched_index, end_date, repo_list,
                                                   period="month"):
    """个人代码核心开发者（含管理者）晋升数量。"""
    from_date, to_date = get_period_range(end_date, period)
    prev_start, prev_end = get_previous_period_range(end_date, period)
    code_map_t, _ = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                                 from_date, to_date, org_only=False)
    code_map_t1, _ = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                                  prev_start, prev_end, org_only=False)
    core_t = _get_core_contributor_set_from_maps(code_map_t, {}, dimension="code", core_ratio=0.5)
    core_t1 = _get_core_contributor_set_from_maps(code_map_t1, {}, dimension="code", core_ratio=0.5)
    non_core_t1 = set(code_map_t1.keys()) - core_t1
    promotion = len(core_t & non_core_t1)
    return {"individual_code_core_promotion_count": promotion, "period": period}


def individual_issue_core_promotion_count_by_period(client, contributors_enriched_index, end_date, repo_list,
                                                    period="month"):
    """个人 Issue 核心开发者（含管理者）晋升数量。"""
    from_date, to_date = get_period_range(end_date, period)
    prev_start, prev_end = get_previous_period_range(end_date, period)
    _, issue_map_t = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                                  from_date, to_date, org_only=False)
    _, issue_map_t1 = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                                   prev_start, prev_end, org_only=False)
    core_t = _get_core_contributor_set_from_maps({}, issue_map_t, dimension="issue", core_ratio=0.5)
    core_t1 = _get_core_contributor_set_from_maps({}, issue_map_t1, dimension="issue", core_ratio=0.5)
    non_core_t1 = set(issue_map_t1.keys()) - core_t1
    promotion = len(core_t & non_core_t1)
    return {"individual_issue_core_promotion_count": promotion, "period": period}


def _core_retention_churn_loss(client, contributors_enriched_index, repo_list, end_date, period, org_only, dimension):
    """计算核心开发者留存率、淡出率、流失率。dimension: 'code' or 'issue'。"""
    from_date, to_date = get_period_range(end_date, period)
    prev_start, prev_end = get_previous_period_range(end_date, period)
    if dimension == "code":
        code_t, _ = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                                 from_date, to_date, org_only=org_only)
        code_t1, _ = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                                  prev_start, prev_end, org_only=org_only)
        core_t = _get_core_contributor_set_from_maps(code_t, {}, dimension="code", core_ratio=0.5)
        core_t1 = _get_core_contributor_set_from_maps(code_t1, {}, dimension="code", core_ratio=0.5)
        active_t = set(code_t.keys())
    else:
        _, issue_t = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                                  from_date, to_date, org_only=org_only)
        _, issue_t1 = _get_contributor_code_and_issue_contribution(client, contributors_enriched_index, repo_list,
                                                                   prev_start, prev_end, org_only=org_only)
        core_t = _get_core_contributor_set_from_maps({}, issue_t, dimension="issue", core_ratio=0.5)
        core_t1 = _get_core_contributor_set_from_maps({}, issue_t1, dimension="issue", core_ratio=0.5)
        active_t = set(issue_t.keys())
    if not core_t1:
        return None, None, None
    retained = len(core_t1 & core_t)
    downgraded = len(core_t1 & (active_t - core_t))  # T-1 核心且 T 有活动但非核心
    left = len(core_t1 - active_t)  # T-1 核心且 T 无活动
    retention = retained / len(core_t1) if core_t1 else None
    churn = downgraded / len(core_t1) if core_t1 else None
    loss = left / len(core_t1) if core_t1 else None
    return retention, churn, loss


def org_code_core_retention_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """组织代码核心开发者（含管理者）留存率：(T与T-1均为核心) / (T-1核心总数)。"""
    retention, _, _ = _core_retention_churn_loss(client, contributors_enriched_index, repo_list, end_date, period,
                                                 org_only=True, dimension="code")
    return {"org_code_core_retention": retention, "period": period}


def org_issue_core_retention_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """组织 Issue 核心开发者（含管理者）留存率。"""
    retention, _, _ = _core_retention_churn_loss(client, contributors_enriched_index, repo_list, end_date, period,
                                                 org_only=True, dimension="issue")
    return {"org_issue_core_retention": retention, "period": period}


def individual_code_core_retention_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """个人代码核心开发者（含管理者）留存率。"""
    retention, _, _ = _core_retention_churn_loss(client, contributors_enriched_index, repo_list, end_date, period,
                                                 org_only=False, dimension="code")
    return {"individual_code_core_retention": retention, "period": period}


def individual_issue_core_retention_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """个人 Issue 核心开发者（含管理者）留存率。"""
    retention, _, _ = _core_retention_churn_loss(client, contributors_enriched_index, repo_list, end_date, period,
                                                 org_only=False, dimension="issue")
    return {"individual_issue_core_retention": retention, "period": period}


def org_code_core_churn_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """组织代码核心开发者（含管理者）淡出率：(T-1核心且T为常客/访客) / (T-1核心总数)。"""
    _, churn, _ = _core_retention_churn_loss(client, contributors_enriched_index, repo_list, end_date, period,
                                             org_only=True, dimension="code")
    return {"org_code_core_churn": churn, "period": period}


def org_issue_core_churn_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """组织 Issue 核心开发者（含管理者）淡出率。"""
    _, churn, _ = _core_retention_churn_loss(client, contributors_enriched_index, repo_list, end_date, period,
                                             org_only=True, dimension="issue")
    return {"org_issue_core_churn": churn, "period": period}


def individual_code_core_churn_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """个人代码核心开发者（含管理者）淡出率。"""
    _, churn, _ = _core_retention_churn_loss(client, contributors_enriched_index, repo_list, end_date, period,
                                             org_only=False, dimension="code")
    return {"individual_code_core_churn": churn, "period": period}


def individual_issue_core_churn_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """个人 Issue 核心开发者（含管理者）淡出率。"""
    _, churn, _ = _core_retention_churn_loss(client, contributors_enriched_index, repo_list, end_date, period,
                                             org_only=False, dimension="issue")
    return {"individual_issue_core_churn": churn, "period": period}


def org_code_core_loss_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """组织代码核心开发者（含管理者）流失率：(T-1核心且T无记录) / (T-1核心总数)。"""
    _, _, loss = _core_retention_churn_loss(client, contributors_enriched_index, repo_list, end_date, period,
                                            org_only=True, dimension="code")
    return {"org_code_core_loss": loss, "period": period}


def org_issue_core_loss_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """组织 Issue 核心开发者（含管理者）流失率。"""
    _, _, loss = _core_retention_churn_loss(client, contributors_enriched_index, repo_list, end_date, period,
                                            org_only=True, dimension="issue")
    return {"org_issue_core_loss": loss, "period": period}


def individual_code_core_loss_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """个人代码核心开发者（含管理者）流失率。"""
    _, _, loss = _core_retention_churn_loss(client, contributors_enriched_index, repo_list, end_date, period,
                                            org_only=False, dimension="code")
    return {"individual_code_core_loss": loss, "period": period}


def individual_issue_core_loss_by_period(client, contributors_enriched_index, end_date, repo_list, period="month"):
    """个人 Issue 核心开发者（含管理者）流失率。"""
    _, _, loss = _core_retention_churn_loss(client, contributors_enriched_index, repo_list, end_date, period,
                                            org_only=False, dimension="issue")
    return {"individual_issue_core_loss": loss, "period": period}
