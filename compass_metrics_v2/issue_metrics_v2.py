""" Set of issue related metrics """

from compass_metrics.db_dsl import get_uuid_count_query, get_updated_issues_count_query
from datetime import timedelta
from compass_common.datetime import get_time_diff_days
from compass_common.algorithm_utils import get_medium
from compass_common.opensearch_utils import get_all_index_data
from dateutil.relativedelta import relativedelta

# =========================
# v2: 按周期（月 / 季度 / 年）的一组新 Issue 指标
# =========================

from datetime import datetime, timedelta

from compass_common.algorithm_utils import get_medium
from compass_common.datetime import get_time_diff_days
from compass_common.opensearch_utils import get_all_index_data


# def get_period_range(end_date: datetime, period: str):
#     """
#     根据周期类型（月、季度、年）计算本周期的开始时间。
#
#     - month: 当月第一天 00:00:00 到 end_date
#     - quarter: 当季度第一天 00:00:00 到 end_date
#     - year: 当年第一天 00:00:00 到 end_date
#     """
#     if period not in ("month", "quarter", "year"):
#         raise ValueError("period must be one of: month, quarter, year")
#
#     if period == "month":
#         start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#     elif period == "year":
#         start_date = end_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
#     else:  # quarter
#         month = ((end_date.month - 1) // 3) * 3 + 1
#         start_date = end_date.replace(month=month, day=1, hour=0, minute=0, second=0, microsecond=0)

    # return start_date, end_date

def get_period_range(end_date: datetime, period: str):
    if period not in ("month", "quarter", "year"):
        raise ValueError("period must be one of: month, quarter, year")

    # 1. 确定 start_date (逻辑保持不变)
    if period == "month":
        start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == "year":
        start_date = end_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:  # quarter
        month = ((end_date.month - 1) // 3) * 3 + 1
        start_date = end_date.replace(month=month, day=1, hour=0, minute=0, second=0, microsecond=0)

    # 2. 修改 end_date 为该周期的最后一天
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
    获取“周期-2”的时间范围：即当前周期的前一个完整周期。
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
        prev_start = current_start - relativedelta(months=3)
        prev_start = prev_start.replace(day=1)
    return prev_start, prev_end


def build_base_issue_query(agg_type, repos_list, field, date_field, from_date, to_date):
    query = get_uuid_count_query(agg_type, repos_list, field, date_field, size=0, from_date=from_date, to_date=to_date)
    query["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
    return query


def issue_new_unresponsive_ratio_by_period(client, issue_index, end_date, repos_list, period="month"):
    """
    新建Issue周期内未响应占比。

    定义：当前周期新建Issue超过一个周期未响应的占比。
    这里按照业务描述，使用“周期-2”中新建的 Issue 作为计算对象：
      - 分子：周期-2 创建且未响应的 Issue 数量（使用 num_of_comments_without_bot == 0 近似，且状态为 open/progressing）。
      - 分母：周期-2 创建的 Issue 总数。
    """
    from_date, to_date = get_previous_period_range(end_date, period)

    # 分母：周期-2 Issue 创建总数
    total_query = get_uuid_count_query(
        "cardinality", repos_list, "uuid", size=0, from_date=from_date, to_date=to_date
    )
    total_query["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
    total_query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    total = client.search(index=issue_index, body=total_query)["aggregations"]["count_of_uuid"]["value"]

    # 分子：周期-2 未响应的 Issue 数量
    unresp_query = get_uuid_count_query(
        "cardinality", repos_list, "uuid", size=0, from_date=from_date, to_date=to_date
    )
    unresp_query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    unresp_query["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
    unresp_query["query"]["bool"]["must"].append({"match_phrase": {"num_of_comments_without_bot": 0}})
    unresp_query["query"]["bool"]["must"].append({"terms": {"state": ["open", "progressing"]}})
    unresp = client.search(index=issue_index, body=unresp_query)["aggregations"]["count_of_uuid"]["value"]

    return {
        "issue_new_unresponsive_ratio": (unresp / total) if total > 0 else None,
        "issue_new_unresponsive_count": unresp,
        "issue_new_total_count": total,
        "period": period,
    }


def issue_new_first_response_time_by_period(client, issue_index, end_date, repos_list, period="month"):
    """
    新建Issue周期内首次响应时间（平均值 / 中位数）。

    输入：周期-2 内新建且已经响应的 Issue，字段 time_to_first_attention_without_bot >= 0。
    """
    from_date, to_date = get_previous_period_range(end_date, period)

    # 平均值
    avg_query = build_base_issue_query(
        "avg", repos_list, "time_to_first_attention_without_bot", "grimoire_creation_date", from_date, to_date
    )
    avg_query["query"]["bool"]["must"].append({"range": {"time_to_first_attention_without_bot": {"gte": 0}}})
    avg_res = client.search(index=issue_index, body=avg_query)
    if avg_res["hits"]["total"]["value"] == 0:
        return {
            "issue_new_first_response_avg": None,
            "issue_new_first_response_mid": None,
            "period": period,
        }
    avg_value = avg_res["aggregations"]["count_of_uuid"]["value"]

    # 中位数
    mid_query = build_base_issue_query(
        "percentiles", repos_list, "time_to_first_attention_without_bot", "grimoire_creation_date", from_date, to_date
    )
    mid_query["aggs"]["count_of_uuid"]["percentiles"]["percents"] = [50]
    mid_query["query"]["bool"]["must"].append({"range": {"time_to_first_attention_without_bot": {"gte": 0}}})
    mid_value = client.search(index=issue_index, body=mid_query)["aggregations"]["count_of_uuid"]["values"]["50.0"]

    return {
        "issue_new_first_response_avg": avg_value,
        "issue_new_first_response_mid": mid_value,
        "period": period,
    }


def issue_new_handle_time_by_period(client, issue_index, end_date, repos_list, period="month"):
    """
    新建Issue周期内处理时长（平均值 / 中位数，单位：天）。

    定义与原有 time_to_close 一致：
      - 若 Issue 已关闭/拒绝且关闭时间在当前计算时间点之前：关闭时间 - 创建时间。
      - 否则：统计时刻（end_date）- 创建时间。
    这里的“新建 Issue”限定在“周期-2”内创建。
    """
    from_date, to_date = get_previous_period_range(end_date, period)

    query_close_time = get_uuid_count_query(
        "avg",
        repos_list,
        "time_to_close",
        "grimoire_creation_date",
        size=1000,
        from_date=from_date,
        to_date=to_date,
    )
    query_close_time["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})

    close_time_items = get_all_index_data(client, issue_index, query_close_time)
    if len(close_time_items) == 0:
        return {
            "issue_new_handle_time_avg": None,
            "issue_new_handle_time_mid": None,
            "period": period,
        }

    handle_days = []
    end_str = end_date.isoformat()
    for item in close_time_items:
        src = item.get("_source", {})
        if "state" not in src:
            continue
        created_at = src.get("created_at")
        if not created_at:
            continue
        closed_at = src.get("closed_at")
        state = src.get("state")
        if closed_at and state in ["closed", "rejected"] and closed_at < end_str and created_at < closed_at:
            days = get_time_diff_days(created_at, closed_at)
        else:
            days = get_time_diff_days(created_at, end_str)
        if days is not None and days >= 0:
            handle_days.append(days)

    if not handle_days:
        return {
            "issue_new_handle_time_avg": None,
            "issue_new_handle_time_mid": None,
            "period": period,
        }

    avg_days = sum(handle_days) / len(handle_days)
    mid_days = get_medium(handle_days)

    return {
        "issue_new_handle_time_avg": avg_days,
        "issue_new_handle_time_mid": mid_days,
        "period": period,
    }


def issue_new_count_by_period(client, issue_index, end_date, repos_list, period="month"):
    """
    新增Issue数 / Issue新建数量：本周期内创建的 Issue 总数。
    """
    from_date, to_date = get_period_range(end_date, period)
    query = get_uuid_count_query(
        "cardinality", repos_list, "uuid", size=0, from_date=from_date, to_date=to_date
    )
    query["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
    query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    count = client.search(index=issue_index, body=query)["aggregations"]["count_of_uuid"]["value"]
    return {
        "issue_new_count": count,
        "period": period,
    }


def issue_comment_activity_by_period(client, issue_index, end_date, repos_list, period="month"):
    """
    Issue 讨论活跃度：周期内 Issue 下的评论总数。

    使用字段 num_of_comments_without_bot 作为“非机器人评论数”的近似。
    """
    from_date, to_date = get_period_range(end_date, period)
    query_issue_comments_count = get_uuid_count_query(
        "sum",
        repos_list,
        "num_of_comments_without_bot",
        date_field="grimoire_creation_date",
        size=0,
        from_date=from_date,
        to_date=to_date,
    )
    query_issue_comments_count["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
    res = client.search(index=issue_index, body=query_issue_comments_count)
    total_comments = res["aggregations"]["count_of_uuid"]["value"] if res["hits"]["total"]["value"] > 0 else 0
    return {
        "issue_comment_activity": total_comments,
        "period": period,
    }


def issue_new_and_responded_count_by_period(client, issue_index, end_date, repos_list, period="month"):
    """
    Issue 新建并响应数量：本周期新建并且本周期响应的 Issue 数量。

    这里基于 time_to_first_attention_without_bot >= 0 近似“有响应”，
    由于索引中没有单独的首次响应时间戳，这里无法严格限定“响应时间落在周期内”，
    因此简化为：本周期内创建，且 time_to_first_attention_without_bot >= 0。
    """
    from_date, to_date = get_period_range(end_date, period)
    query = get_uuid_count_query(
        "cardinality", repos_list, "uuid", size=0, from_date=from_date, to_date=to_date
    )
    query["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
    query["query"]["bool"]["must"].append({"range": {"time_to_first_attention_without_bot": {"gte": 0}}})
    query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    count = client.search(index=issue_index, body=query)["aggregations"]["count_of_uuid"]["value"]
    return {
        "issue_new_and_responded_count": count,
        "period": period,
    }


def issue_closed_count_by_period(client, issue_index, end_date, repos_list, period="month"):
    """
    Issue 关闭数量：本周期总关闭 Issue 数量。
    """
    from_date, to_date = get_period_range(end_date, period)
    query = get_uuid_count_query(
        "cardinality", repos_list, "uuid", size=0, from_date=from_date, to_date=to_date
    )
    query["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
    query["query"]["bool"]["must_not"] = [
        {"term": {"state": "open"}},
        {"term": {"state": "progressing"}},
    ]
    closed = client.search(index=issue_index, body=query)["aggregations"]["count_of_uuid"]["value"]
    return {
        "issue_closed_count": closed,
        "period": period,
    }


def issue_new_and_closed_count_by_period(client, issue_index, end_date, repos_list, period="month"):
    """
    Issue 新建并关闭数量：本周期新建并且本周期关闭的 Issue 数量。
    """
    from_date, to_date = get_period_range(end_date, period)
    query = get_uuid_count_query(
        "cardinality", repos_list, "uuid", size=0, from_date=from_date, to_date=to_date
    )
    query["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
    query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    # 既要在本周期创建，又要在本周期关闭
    query["query"]["bool"]["filter"].append(
        {
            "range": {
                "closed_at": {
                    "gte": from_date.strftime("%Y-%m-%d"),
                    "lt": (to_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                }
            }
        }
    )
    count = client.search(index=issue_index, body=query)["aggregations"]["count_of_uuid"]["value"]
    return {
        "issue_new_and_closed_count": count,
        "period": period,
    }

#  bug_issue_open_time_avg: None, "bug_issue_open_time_mid": None
def bug_issue_open_time_by_period(client, issue_index, end_date, repos_list, period="month"):
    """
    Bug Issue 打开时间：本周期总打开 Bug Issue 数量。
    """
    from_date, to_date = get_period_range(end_date, period)
    query = get_uuid_count_query(
        "cardinality", repos_list, "uuid", size=0, from_date=from_date, to_date=to_date
    )
    query["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
    query["query"]["bool"]["must"].append({"match_phrase": {"labels": "bug"}})
    count = client.search(index=issue_index, body=query)["aggregations"]["count_of_uuid"]["value"]
    return {
        "bug_issue_open_time_count": count,
        "period": period,
    }
