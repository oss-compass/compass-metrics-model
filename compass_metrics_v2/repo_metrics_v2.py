""" Set of pr related metrics """

from compass_metrics.db_dsl import (get_uuid_count_query,
                                    get_pr_closed_uuid_count,
                                    get_pr_message_count,
                                    get_pr_linked_issue_count)
from datetime import timedelta
from compass_common.datetime import get_time_diff_days
from compass_common.datetime import str_to_datetime
from compass_common.dict_utils import deep_get
from compass_common.algorithm_utils import get_medium
from compass_common.opensearch_utils import get_all_index_data
from dateutil.relativedelta import relativedelta

""" Repo metrics v2: popularity (stars / forks) with period deltas """

from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from compass_metrics.db_dsl import get_uuid_count_query


# def get_period_range(end_date: datetime, period: str):
#     """
#     返回本周期的起止时间（起始为周期第一天 00:00:00，结束为 end_date）。
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
#     return start_date, end_date

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


def cumulative_count(client, index, repos_list, to_date, field="uuid", date_field="grimoire_creation_date"):
    """累计总数：从 2000-01-01 到 to_date（lt）"""
    query = get_uuid_count_query(
        "cardinality",
        repos_list,
        field,
        date_field=date_field,
        size=0,
        from_date=datetime(2000, 1, 1),
        to_date=to_date,
    )
    query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000

    return client.search(index=index, body=query)["aggregations"]["count_of_uuid"]["value"]


def repo_stars_by_period(client, star_index, end_date, repos_list, period="month"):
    """
    项目关注度（Stars）：周期内新增 Star 数与当前累计 Star 总数。

    - 新增：本周期 Star 总数 - 上周期 Star 总数
    - 累计：本周期 Star 总数（截止 end_date）
    """
    _, end_date = get_period_range(end_date, period)  # 保留周期校验
    prev_start, prev_end = get_previous_period_range(end_date, period)


    # 上周期累计（截止上周期末）
    prev_total = cumulative_count(client, star_index, repos_list, prev_end, field="uuid")
    # 本周期累计（截止当前周期末）
    current_total = cumulative_count(client, star_index, repos_list, end_date, field="uuid")

    added = current_total - prev_total if current_total is not None and prev_total is not None else None

    return {
        "stars_added": added,
        "stars_total": current_total,
        "period": period,
    }


def repo_forks_by_period(client, fork_index, end_date, repos_list, period="month"):
    """
    Forks：周期内新增 Fork 数与当前累计 Fork 总数。

    - 新增：本周期 Fork 总数 - 上周期 Fork 总数
    - 累计：本周期 Fork 总数（截止 end_date）
    """
    _, end_date = get_period_range(end_date, period)  # 保留周期校验
    prev_start, prev_end = get_previous_period_range(end_date, period)

    prev_total = cumulative_count(client, fork_index, repos_list, prev_end, field="uuid")
    current_total = cumulative_count(client, fork_index, repos_list, end_date, field="uuid")

    added = current_total - prev_total if current_total is not None and prev_total is not None else None

    return {
        "forks_added": added,
        "forks_total": current_total,
        "period": period,
    }


