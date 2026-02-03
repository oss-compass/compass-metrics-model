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

# =========================
# v2: 按周期（月 / 季度 / 年）的一组新 PR 指标
# - 所有返回值统一携带 period，不返回 period_from / period_to
# - “周期-2”按当前周期的前一个完整周期计算
# =========================
#



from datetime import datetime


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
    return start_date, end_date


def get_previous_period_range(end_date: datetime, period: str):
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


def build_base_pr_query(agg_type, repos_list, field, date_field, from_date, to_date):
    query = get_uuid_count_query(agg_type, repos_list, field, date_field, size=0, from_date=from_date, to_date=to_date)
    query["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true"}})
    return query


def pr_new_unresponsive_ratio_by_period(client, pr_index, end_date, repos_list, period="month"):
    """
    新建PR周期内未响应占比：
    周期-2 创建并未响应的PR数量（分子） / 周期-2 创建的PR总数（分母）。
    """
    """
        计算新建PR在周期内的未响应占比。
        """
    # 1. 获取时间范围 (返回的是 datetime 对象)
    from_date, to_date = get_previous_period_range(end_date, period)

    # 2. 直接转换时间戳 (因为 to_date 已经是 datetime 对象，无需 parse)
    to_date_millis = int(to_date.timestamp() * 1000)

    # 3. 查询分母：该周期内创建的总 PR 数
    total_query = build_base_pr_query("cardinality", repos_list, "uuid", "grimoire_creation_date", from_date, to_date)
    total_query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000

    try:
        total = client.search(index=pr_index, body=total_query)["aggregations"]["count_of_uuid"]["value"]
    except Exception as e:
        print(f"[Error] Failed to query total PRs: {e}")
        total = 0

    # 4. 查询分子：该周期内创建 且 在周期结束前 未响应 的 PR 数
    unresp_query = build_base_pr_query("cardinality", repos_list, "uuid", "grimoire_creation_date", from_date, to_date)
    unresp_query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000

    # Script Logic:
    # 排除掉 (return false) 那些在 endDate 之前已经 合并 或 响应 的数据
    script_source = """
            long endDate = params.endDate;

            // 检查 A: 是否在周期结束前已合并
            if (doc.containsKey('merged_at') && doc['merged_at'].size() > 0) {
                long mergedTime = doc['merged_at'].value.toInstant().toEpochMilli();
                if (mergedTime <= endDate) {
                    return false; 
                }
            }

            // 检查 B: 是否在周期结束前已有响应
            if (doc.containsKey('time_to_merge_request_response') && doc['time_to_merge_request_response'].size() > 0) {
                double daysToResp = doc['time_to_merge_request_response'].value;

                if (doc.containsKey('grimoire_creation_date') && doc['grimoire_creation_date'].size() > 0) {
                    long createTime = doc['grimoire_creation_date'].value.toInstant().toEpochMilli();
                    long respTime = createTime + (long)(daysToResp * 86400 * 1000);

                    if (respTime <= endDate) {
                        return false;
                    }
                }
            }

            return true;
        """

    if "bool" not in unresp_query["query"]:
        unresp_query["query"]["bool"] = {}
    if "filter" not in unresp_query["query"]["bool"]:
        unresp_query["query"]["bool"]["filter"] = []

    unresp_query["query"]["bool"]["filter"].append({
        "script": {
            "script": {
                "source": script_source,
                "lang": "painless",
                "params": {
                    "endDate": to_date_millis
                }
            }
        }
    })

    try:
        unresp = client.search(index=pr_index, body=unresp_query)["aggregations"]["count_of_uuid"]["value"]
    except Exception as e:
        print(f"[Error] Failed to query unresponsive PRs: {e}")
        unresp = 0

    return {
        "pr_new_unresponsive_ratio": (unresp / total) if total > 0 else 0,
        "pr_new_unresponsive_count": unresp,
        "pr_new_total_count": total,
        "period": period,
    }



def pr_new_first_response_time_by_period(client, pr_index, end_date, repos_list, period="month"):
    """
    新建PR周期内首次响应时间（平均值/中位数）：
    输入：周期-2 内所有 [首次响应时间 - PR创建时间] 的集合。
    """
    from_date, to_date = get_previous_period_range(end_date, period)

    avg_query = build_base_pr_query("avg", repos_list, "time_to_first_attention_without_bot", "grimoire_creation_date",
                                    from_date, to_date)
    avg_query["query"]["bool"]["must"].append({"range": {"time_to_first_attention_without_bot": {"gte": 0}}})
    # print(avg_query)
    avg_res = client.search(index=pr_index, body=avg_query)
    if avg_res["hits"]["total"]["value"] == 0:
        return {
            "pr_new_first_response_avg": None,
            "pr_new_first_response_mid": None,
            "period": period,
        }
    avg_value = avg_res["aggregations"]["count_of_uuid"]["value"]

    mid_query = build_base_pr_query("percentiles", repos_list, "time_to_first_attention_without_bot",
                                     "grimoire_creation_date", from_date, to_date)
    mid_query["aggs"]["count_of_uuid"]["percentiles"]["percents"] = [50]
    mid_query["query"]["bool"]["must"].append({"range": {"time_to_first_attention_without_bot": {"gte": 0}}})
    mid_value = client.search(index=pr_index, body=mid_query)["aggregations"]["count_of_uuid"]["values"]["50.0"]

    return {
        "pr_new_first_response_avg": avg_value,
        "pr_new_first_response_mid": mid_value,
        "period": period,
    }


def pr_new_handle_time_by_period(client, pr_index, end_date, repos_list, period="month"):
    """
    新建PR周期内处理时长（平均值/中位数，单位：天）：
    输入：周期-2 新建PR处理时长 = 关闭/合并时间 - 创建时间 或者 本周期开始时间 - 创建时间（未结束）。
    """
    # from_date, to_date = get_previous_period_range(end_date, period)
    # current_start, _ = get_period_range(end_date, period)
    #
    # query = get_uuid_count_query("avg", repos_list, "uuid", "grimoire_creation_date", size=1000, from_date=from_date,
    #                              to_date=to_date)
    # query["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true"}})
    #
    # print(query)
    # items = get_all_index_data(client, pr_index, query)
    # if not items:
    #     return {"pr_new_handle_time_avg": None, "pr_new_handle_time_mid": None, "period": period}
    #
    # days_list = []
    # cutoff_str = current_start.isoformat()
    # for item in items:
    #     src = item.get("_source", {})
    #     created_at = src.get("created_at")
    #     if not created_at:
    #         continue
    #
    #     state = src.get("state")
    #     merged_at = src.get("merged_at")
    #     closed_at = src.get("closed_at")
    #     updated_at = src.get("updated_at")
    #
    #     end_point = None
    #     if merged_at and state == "merged" and merged_at < cutoff_str:
    #         end_point = merged_at
    #     elif (closed_at or updated_at) and state == "closed":
    #         # gitee/github 可能使用 closed_at 或 updated_at
    #         candidate = closed_at or updated_at
    #         if candidate and candidate < cutoff_str:
    #             end_point = candidate
    #
    #     if end_point is None:
    #         end_point = cutoff_str
    #
    #     d = get_time_diff_days(created_at, end_point)
    #     if d is not None and d >= 0:
    #         days_list.append(d)
    #
    # if not days_list:
    #     return {"pr_new_handle_time_avg": None, "pr_new_handle_time_mid": None, "period": period}
    """
        新建PR周期内处理时长（平均值/中位数，单位：天）：
        【无风险版特点】：
        1. 仅使用标准库 (datetime)，无需 dateutil。
        2. ES 查询聚合参数修正为 "cardinality"，防止 "avg" 报错。
        3. 时间解析采用截断法，兼容带毫秒/不带毫秒、带时区/不带时区的时间字符串。
        """

    # 1. 获取周期时间范围
    from_date, to_date = get_previous_period_range(end_date, period)

    # 【安全措施】强制去除 to_date 的时区信息
    # 这样后续计算 (finish - start) 时，两者都是 naive time，不会报错。
    if to_date.tzinfo is not None:
        to_date = to_date.replace(tzinfo=None)

    # 2. 构建查询
    # 【核心修复】：将原本的 "avg" 改为 "cardinality"。
    # 原因：get_uuid_count_query 内部会构建聚合查询，"avg" 不能用于 uuid (字符串)，会导致 400 报错。
    # 这里改成 "cardinality" (计数) 只是为了让查询语法合法，我们的目标数据在 items 列表中。
    query = get_uuid_count_query("cardinality", repos_list, "uuid", "grimoire_creation_date", size=10000,
                                 from_date=from_date, to_date=to_date)
    query["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true"}})

    # 获取数据列表
    items = get_all_index_data(client, pr_index, query)

    # 如果没数据，直接返回
    if not items:
        return {"pr_new_handle_time_avg": None, "pr_new_handle_time_mid": None, "period": period}

    days_list = []

    # 【内部函数】最稳健的时间解析逻辑
    def safe_parse_time(time_str):
        if not time_str or not isinstance(time_str, str):
            return None
        try:
            # 截取前 19 位： "2023-10-12T10:00:00"
            # 这样可以忽略后面的 .123456 (毫秒) 或者 Z/+08:00 (时区)
            # 虽然丢弃了时区，但只要所有时间都这样处理，相对差值是准确的。
            clean_str = time_str[:19]
            return datetime.strptime(clean_str, "%Y-%m-%dT%H:%M:%S")
        except Exception:
            return None

    for item in items:
        src = item.get("_source", {})
        c_str = src.get("grimoire_creation_date") or src.get("created_at")
        created_dt = safe_parse_time(c_str)

        if not created_dt:
            continue
        state = src.get("state")
        merged_at_str = src.get("merged_at")
        closed_at_str = src.get("closed_at")
        updated_at_str = src.get("updated_at")

        finish_dt = None

        # 1. 如果已合并，取合并时间
        if state == "merged" and merged_at_str:
            finish_dt = safe_parse_time(merged_at_str)
        # 2. 如果已关闭(但未合并)，取关闭时间
        elif state == "closed":
            # 优先用 closed_at，没有则用 updated_at
            candidate = closed_at_str or updated_at_str
            finish_dt = safe_parse_time(candidate)
        calc_end_dt = to_date  # 默认为周期截止时间

        # 如果 PR 确实结束了，并且结束时间在周期截止之前，那么使用实际结束时间
        if finish_dt is not None and finish_dt < to_date:
            calc_end_dt = finish_dt

        # --- D. 计算时长 ---
        # 两个无时区的 datetime 相减，得到 timedelta
        delta = calc_end_dt - created_dt
        days = delta.total_seconds() / 86400.0

        # 过滤掉异常数据 (比如结束时间早于创建时间)
        if days >= 0:
            days_list.append(days)

    if not days_list:
        return {"pr_new_handle_time_avg": None, "pr_new_handle_time_mid": None, "period": period}

    return {
        "pr_new_handle_time_avg": sum(days_list) / len(days_list),
        "pr_new_handle_time_mid": get_medium(days_list),
        "period": period,
    }





def pr_merge_ratio_by_period(client, pr_index, end_date, repos_list, period="month"):
    """
    PR 合并率：
    周期-2 创建且状态为 Merged 的PR数（分子） / 周期-2 创建的总PR数（分母）。
    """
    from_date, to_date = get_previous_period_range(end_date, period)

    total_query = build_base_pr_query("cardinality", repos_list, "uuid", "grimoire_creation_date", from_date, to_date)
    total_query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    total = client.search(index=pr_index, body=total_query)["aggregations"]["count_of_uuid"]["value"]

    merged_query = build_base_pr_query("cardinality", repos_list, "uuid", "grimoire_creation_date", from_date, to_date)
    merged_query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    merged_query["query"]["bool"]["must"].append({"match_phrase": {"state": "merged"}})
    merged = client.search(index=pr_index, body=merged_query)["aggregations"]["count_of_uuid"]["value"]

    return {
        "pr_merge_ratio": (merged / total) if total > 0 else None,
        "pr_merged_count": merged,
        "pr_total_count": total,
        "period": period,
    }


def pr_issue_linked_ratio_by_period(client, pr_index, pr_comments_index, end_date, repos_list, period="month"):
    """
    PR/Issue 关联率：
    周期-2 关联 issue 的 PR 数（分子） / 周期-2 总 PR 数（分母）。
    """
    from_date, to_date = get_previous_period_range(end_date, period)

    total_query = build_base_pr_query("cardinality", repos_list, "uuid", "grimoire_creation_date", from_date, to_date)
    total_query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    total = client.search(index=pr_index, body=total_query)["aggregations"]["count_of_uuid"]["value"]

    linked = 0
    for repo in repos_list:
        query = get_pr_linked_issue_count(repo, from_date=from_date, to_date=to_date)
        linked += client.search(index=(pr_index, pr_comments_index), body=query)["aggregations"]["count_of_uuid"][
            "value"]

    return {
        "pr_issue_linked_ratio": (linked / total) if total > 0 else None,
        "pr_issue_linked_count": linked,
        "pr_total_count": total,
        "period": period,
    }


def pr_review_participation_ratio_by_period(client, pr_index, end_date, repos_list, period="month"):
    """
    PR 评审参与率：
    周期-2 有非作者 Review 记录的 PR 数（分子） / 周期-2 总 PR 数（分母）。

    近似：num_review_comments_without_bot > 0 或 assignees_accept_count > 0 视为有评审参与。
    """
    from_date, to_date = get_previous_period_range(end_date, period)

    total_query = build_base_pr_query("cardinality", repos_list, "uuid", "grimoire_creation_date", from_date, to_date)
    total_query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    total = client.search(index=pr_index, body=total_query)["aggregations"]["count_of_uuid"]["value"]

    review_query = build_base_pr_query("cardinality", repos_list, "uuid", "grimoire_creation_date", from_date, to_date)
    review_query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    review_query["query"]["bool"]["should"] = [
        {"range": {"num_review_comments_without_bot": {"gt": 0}}},
        {"range": {"assignees_accept_count": {"gt": 0}}},
    ]
    review_query["query"]["bool"]["minimum_should_match"] = 1
    review_count = client.search(index=pr_index, body=review_query)["aggregations"]["count_of_uuid"]["value"]

    return {
        "pr_review_participation_ratio": (review_count / total) if total > 0 else None,
        "pr_with_review_count": review_count,
        "pr_total_count": total,
        "period": period,
    }


def pr_non_author_merge_ratio_by_period(client, pr_index, end_date, repos_list, period="month"):
    """
    异人合并比率：
    周期-2 (Merger != Author) 的 PR 数（分子） / 周期-2 总已合并 PR 数（分母）。
    """
    from_date, to_date = get_previous_period_range(end_date, period)

    merged_query = build_base_pr_query("cardinality", repos_list, "uuid", "grimoire_creation_date", from_date, to_date)
    merged_query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    merged_query["query"]["bool"]["must"].append({"match_phrase": {"merged": "true"}})
    merged_total = client.search(index=pr_index, body=merged_query)["aggregations"]["count_of_uuid"]["value"]

    non_author_query = build_base_pr_query("cardinality", repos_list, "uuid", "grimoire_creation_date", from_date,
                                           to_date)
    non_author_query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    non_author_query["query"]["bool"]["must"].append({"match_phrase": {"merged": "true"}})
    non_author_query["query"]["bool"]["must"].append({
        "script": {
            "script": "if(doc['merged_by_data_name'].size() > 0 && doc['author_name'].size() > 0 && doc['merged_by_data_name'].value != doc['author_name'].value){return true}"
        }
    })
    non_author = client.search(index=pr_index, body=non_author_query)["aggregations"]["count_of_uuid"]["value"]

    return {
        "pr_non_author_merge_ratio": (non_author / merged_total) if merged_total > 0 else None,
        "pr_non_author_merged_count": non_author,
        "pr_merged_total_count": merged_total,
        "period": period,
    }


def pr_avg_interactions_by_period(client, pr_index, end_date, repos_list, period="month"):
    """
    PR 平均交互数：
    周期-2 新建 PR 的评论总数（分子） / 周期-2 新建 PR 总数（分母）。

    近似：使用 num_review_comments_without_bot 的 sum 作为“评论总数”。
    """
    from_date, to_date = get_previous_period_range(end_date, period)

    total_query = build_base_pr_query("cardinality", repos_list, "uuid", "grimoire_creation_date", from_date, to_date)
    total_query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    total = client.search(index=pr_index, body=total_query)["aggregations"]["count_of_uuid"]["value"]

    sum_query = build_base_pr_query("sum", repos_list, "num_review_comments_without_bot", "grimoire_creation_date",
                                    from_date, to_date)
    res = client.search(index=pr_index, body=sum_query)
    comments_total = res["aggregations"]["count_of_uuid"]["value"] if res["hits"]["total"]["value"] > 0 else 0

    return {
        "pr_avg_interactions": (comments_total / total) if total > 0 else None,
        "pr_comments_total": comments_total,
        "pr_total_count": total,
        "period": period,
    }


def pr_review_time_by_size_by_period(client, pr_index, end_date, repos_list, period="month"):
    """
    分级代码审查时长（小时）：
    按代码变更行数（XS/S/M/L/XL）分组统计平均审查时间。

    说明：当前数据模型未发现“首次 Review 时间戳”，这里使用 time_to_first_attention_without_bot
    作为“首次审查/响应时长”的近似，并使用 lines_changed 分级。
    """
    from_date, to_date = get_previous_period_range(end_date, period)

    # 默认分级阈值（可按需调整）
    buckets = {
        "XS": {"lt": 10},
        "S": {"gte": 10, "lt": 30},
        "M": {"gte": 30, "lt": 100},
        "L": {"gte": 100, "lt": 500},
        "XL": {"gte": 500},
    }

    aggs = {}
    for k, r in buckets.items():
        aggs[k] = {
            "filter": {"range": {"lines_changed": r}},
            "aggs": {"avg_review_time": {"avg": {"field": "time_to_first_attention_without_bot"}}},
        }

    query = build_base_pr_query("cardinality", repos_list, "uuid", "grimoire_creation_date", from_date, to_date)
    query["size"] = 0
    query["aggs"] = aggs
    query["query"]["bool"]["must"].append({"range": {"time_to_first_attention_without_bot": {"gte": 0}}})

    res = client.search(index=pr_index, body=query).get("aggregations", {})
    result = {k: (deep_get(res, [k, "avg_review_time", "value"], None)) for k in buckets.keys()}

    return {"pr_review_time_by_size": result, "period": period}


def pr_comment_count_by_period(client, pr_index, end_date, repos_list, period="month"):
    """
    PR 评论数量：周期内产生的 PR 评论次数（次）。
    近似：sum(num_review_comments_without_bot)。
    """
    from_date, to_date = get_period_range(end_date, period)
    query = build_base_pr_query("sum", repos_list, "num_review_comments_without_bot", "grimoire_creation_date",
                                from_date, to_date)
    res = client.search(index=pr_index, body=query)
    total = res["aggregations"]["count_of_uuid"]["value"] if res["hits"]["total"]["value"] > 0 else 0
    return {"pr_comment_count": total, "period": period}


def pr_comment_rank_by_period(client, pr_index, end_date, repos_list, period="month", top_n=10):
    """
    PR 评论排行：按 num_review_comments_without_bot 降序返回 top_n 条 PR 简要信息。
    """
    from_date, to_date = get_period_range(end_date, period)
    query = {
        "size": top_n,
        "query": {
            "bool": {
                "must": [
                    {"terms": {"tag": repos_list}},
                    {"match_phrase": {"pull_request": "true"}},
                ],
                "filter": [
                    {"range": {"grimoire_creation_date": {"gte": from_date.strftime("%Y-%m-%d"),
                                                          "lt": to_date.strftime("%Y-%m-%d")}}}
                ],
            }
        },
        "sort": [{"num_review_comments_without_bot": {"order": "desc"}}],
        "_source": ["uuid", "title", "html_url", "url", "num_review_comments_without_bot", "created_at", "state"],
    }
    hits = client.search(index=pr_index, body=query)["hits"]["hits"]
    rank = []
    for h in hits:
        s = h.get("_source", {})
        rank.append(
            {
                "uuid": s.get("uuid"),
                "title": s.get("title"),
                "html_url": s.get("html_url") or s.get("url"),
                "num_review_comments_without_bot": s.get("num_review_comments_without_bot"),
                "created_at": s.get("created_at"),
                "state": s.get("state"),
            }
        )
    return {"pr_comment_rank": rank, "period": period}


def pr_created_count_by_period(client, pr_index, end_date, repos_list, period="month"):
    """PR新建数量：本周期新建立 PR 数量。"""
    from_date, to_date = get_period_range(end_date, period)
    query = build_base_pr_query("cardinality", repos_list, "uuid", "grimoire_creation_date", from_date, to_date)
    query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    count = client.search(index=pr_index, body=query)["aggregations"]["count_of_uuid"]["value"]
    return {"pr_created_count": count, "period": period}


def pr_created_and_responded_count_by_period(client, pr_index, end_date, repos_list, period="month"):
    """PR新建并响应数量：本周期新建且本周期内已响应（近似：time_to_first_attention_without_bot >= 0）。"""
    from_date, to_date = get_period_range(end_date, period)
    query = build_base_pr_query("cardinality", repos_list, "uuid", "grimoire_creation_date", from_date, to_date)
    query["query"]["bool"]["must"].append({"range": {"time_to_first_attention_without_bot": {"gte": 0}}})
    query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    count = client.search(index=pr_index, body=query)["aggregations"]["count_of_uuid"]["value"]
    return {"pr_created_and_responded_count": count, "period": period}


def pr_closed_count_by_period(client, pr_index, end_date, repos_list, period="month"):
    """PR关闭数量：本周期总关闭 PR 数量（state != open）。"""
    from_date, to_date = get_period_range(end_date, period)
    query = build_base_pr_query("cardinality", repos_list, "uuid", "grimoire_creation_date", from_date, to_date)
    query["query"]["bool"]["must_not"] = [{"term": {"state": "open"}}]
    query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    count = client.search(index=pr_index, body=query)["aggregations"]["count_of_uuid"]["value"]
    return {"pr_closed_count": count, "period": period}


def pr_created_and_closed_count_by_period(client, pr_index, end_date, repos_list, period="month"):
    """PR新建并关闭数量：本周期新建且本周期关闭 PR 数量。"""
    from_date, to_date = get_period_range(end_date, period)
    query = build_base_pr_query("cardinality", repos_list, "uuid", "grimoire_creation_date", from_date, to_date)
    query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    query["query"]["bool"]["filter"].append(
        {"range": {"closed_at": {"gte": from_date.strftime("%Y-%m-%d"),
                                 "lt": (to_date + timedelta(days=1)).strftime("%Y-%m-%d")}}}
    )
    count = client.search(index=pr_index, body=query)["aggregations"]["count_of_uuid"]["value"]
    return {"pr_created_and_closed_count": count, "period": period}
