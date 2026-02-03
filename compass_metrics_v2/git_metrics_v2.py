""" Set of git related metrics """

from compass_metrics.db_dsl import (get_updated_since_query,
                                    get_uuid_count_query,
                                    get_message_list_query,
                                    get_pr_query_by_commit_hash)
from compass_metrics.contributor_metrics import get_contributor_list
from compass_metrics.repo_metrics import get_activity_repo_list
from compass_common.datetime import (get_time_diff_months,
                                     check_times_has_overlap,
                                     get_oldest_date,
                                     get_latest_date,
                                     get_date_list)
from compass_common.list_utils import split_list                                     
from datetime import timedelta
from compass_common.opensearch_utils import get_all_index_data
import numpy as np
import math
import datetime
from dateutil.relativedelta import relativedelta


def created_since(client, git_index, date, repo_list):
    """ Determine how long a repository has existed since it was created (in months). """
    created_since_list = []
    repos_git_list = [repo + ".git" for repo in repo_list]
    query_first_commit_since = get_updated_since_query(
        repos_git_list, date_field='grimoire_creation_date', to_date=date, operation="min")
    buckets = client.search(
        index=git_index, body=query_first_commit_since)['aggregations']['group_by_origin']['buckets']
    if buckets:
        for bucket in buckets:
            created_since_list.append(get_time_diff_months(bucket['grimoire_creation_date']['value_as_string'], str(date)))

    result = {
        "created_since": round(sum(created_since_list), 4) if created_since_list else None
    }
    return result


def updated_since(client, git_index, contributors_index, date, repo_list, level):
    """ Determine the average time per repository since the repository was last updated (in months). """
    active_repo_list = repo_list
    if level in ["community", "project"]:
        repo_name_list = get_activity_repo_list(client, contributors_index, date, repo_list)
        if len(repo_name_list) > 0:
            active_repo_list = repo_name_list
    updated_since_list = []
    active_repo_git_list = [repo + ".git" for repo in active_repo_list]
    query_updated_since = get_updated_since_query(
        active_repo_git_list, date_field='metadata__updated_on', to_date=date)
    buckets = client.search(
        index=git_index, body=query_updated_since)['aggregations']['group_by_origin']['buckets']
    if buckets:
        for bucket in buckets:
            updated_since_list.append(get_time_diff_months(bucket['metadata__updated_on']['value_as_string'], str(date)))
    result = {
        "updated_since": float(round(sum(updated_since_list) / len(updated_since_list), 4)) if len(updated_since_list) > 0 else 0
    }
    return result


def commit_frequency(client, contributors_index, date, repo_list):
    """ Determine the average number of commits per week in the past 90 days. """
    from_date = date - timedelta(days=90)
    to_date = date
    commit_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                   "code_author_date_list")
    result = {
        'commit_frequency': get_commit_count(from_date, to_date, commit_contributor_list)/12.85,
        'commit_frequency_bot': get_commit_count(from_date, to_date, commit_contributor_list, is_bot=True)/12.85,
        'commit_frequency_without_bot': get_commit_count(from_date, to_date, commit_contributor_list, is_bot=False)/12.85
    }
    return result

def commit_frequency_last_year(client, contributors_index, date, repo_list):
    """ Determine the average number of commits per week in the past 365 days. """
    from_date = date - timedelta(days=365)
    to_date = date
    commit_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                   "code_author_date_list")
    result = {
        'commit_frequency_last_year': get_commit_count(from_date, to_date, commit_contributor_list)/52.14,
        # 'commit_frequency_last_year_bot': get_commit_count(from_date, to_date, commit_contributor_list, is_bot=True)/52.14,
        # 'commit_frequency_last_year_without_bot': get_commit_count(from_date, to_date, commit_contributor_list, is_bot=False)/52.14
    }
    return result


def org_count(client, contributors_index, date, repo_list):
    """ Number of organizations to which active code contributors belong in the past 90 days """
    from_date = date - timedelta(days=90)
    to_date = date
    commit_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                   "code_author_date_list")
    org_name_set = set()
    for contributor in commit_contributor_list:
        for org in contributor["org_change_date_list"]:
            if org.get("org_name") is not None and check_times_has_overlap(
                    org["first_date"], org["last_date"], from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d")):
                org_name_set.add(org.get("org_name"))
    result = {
        'org_count': len(org_name_set)
    }
    return result

def org_count_all(client, contributors_index, date, repo_list):
    """ Number of organizations to which active code contributors belong """
    from_date = datetime.date(2000, 1, 1)
    to_date = date
    commit_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                   "code_author_date_list")
    org_name_set = set()
    for contributor in commit_contributor_list:
        for org in contributor["org_change_date_list"]:
            if org.get("org_name") is not None and check_times_has_overlap(
                    org["first_date"], org["last_date"], from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d")):
                org_name_set.add(org.get("org_name"))
    result = {
        'org_count_all': len(org_name_set)
    }
    return result


def org_commit_frequency(client, contributors_index, date, repo_list):
    """ Determine the average number of commits with organization affiliation per week in the past 90 days. """
    from_date = date - timedelta(days=90)
    to_date = date
    commit_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                   "code_author_date_list")
    from_date_str = from_date.strftime("%Y-%m-%d")
    to_date_str = to_date.strftime("%Y-%m-%d")
    total_commit_count = 0
    org_commit_count = 0
    org_commit_bot_count = 0
    org_commit_without_bot_count = 0
    org_commit_detail_dict = {}

    for contributor in commit_contributor_list:
        commit_date_list = [x for x in sorted(contributor["code_author_date_list"]) if from_date_str <= x < to_date_str]
        total_commit_count += len(commit_date_list)
        for commit_date in commit_date_list:
            for org in contributor["org_change_date_list"]:
                if org["org_name"] is not None and org["first_date"] <= commit_date < org["last_date"]:
                    org_commit_count += 1
                    if contributor["is_bot"]:
                        org_commit_bot_count += 1
                    else:
                        org_commit_without_bot_count += 1
                    break

            org_name_set = set()
            for org in contributor["org_change_date_list"]:
                org_name = org.get("org_name") if org.get("org_name") else org.get("domain")
                if org_name in org_name_set:
                    continue
                org_name_set.add(org_name)
                is_org = True if org.get("org_name") else False
                count = org_commit_detail_dict.get(org_name, {}).get("org_commit", 0)
                if org["first_date"] <= commit_date < org["last_date"]:
                    count += 1
                org_commit_detail_dict[org_name] = {
                    "org_name": org_name,
                    "is_org": is_org,
                    "org_commit": count
                }

    org_commit_frequency_list = []
    for x in org_commit_detail_dict.values():
        if x["org_commit"] == 0:
            continue
        if x["is_org"]:
            org_commit_percentage_by_org = 0 if org_commit_count == 0 else x["org_commit"] / org_commit_count
        else:
            org_commit_percentage_by_org = 0 if (total_commit_count - org_commit_count) == 0 else \
                x["org_commit"] / (total_commit_count - org_commit_count)
        x["org_commit_percentage_by_org"] = round(org_commit_percentage_by_org, 4)
        x["org_commit_percentage_by_total"] = 0 if total_commit_count == 0 else round(x["org_commit"] / total_commit_count, 4)
        org_commit_frequency_list.append(x)
    org_commit_frequency_list = sorted(org_commit_frequency_list, key=lambda x: x["org_commit"], reverse=True)
    result = {
        'org_commit_frequency': round(org_commit_count/12.85, 4),
        'org_commit_frequency_bot': round(org_commit_bot_count/12.85, 4),
        'org_commit_frequency_without_bot': round(org_commit_without_bot_count/12.85, 4),
        'org_commit_frequency_list': org_commit_frequency_list
    }
    return result


def org_contribution_last(client, contributors_index, date, repo_list):
    """ Total contribution time of all organizations to the community in the past 90 days (weeks). """
    from_date = date - timedelta(days=90)
    to_date = date
    commit_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                   "code_author_date_list")
    contribution_last = 0
    repo_contributor_group_dict = {}
    for contributor in commit_contributor_list:
        repo_contributor_list = repo_contributor_group_dict.get(contributor["repo_name"], [])
        repo_contributor_list.append(contributor)
        repo_contributor_group_dict[contributor["repo_name"]] = repo_contributor_list

    date_list = get_date_list(begin_date=str(from_date), end_date=str(to_date), freq='7D')
    for repo, repo_contributor_list in repo_contributor_group_dict.items():
        for day in date_list:
            org_name_set = set()
            from_day = (day - timedelta(days=7)).strftime("%Y-%m-%d")
            to_day = day.strftime("%Y-%m-%d")
            for contributor in repo_contributor_list:
                for org in contributor["org_change_date_list"]:
                    if org.get("org_name") is not None and check_times_has_overlap(org["first_date"], org["last_date"],
                                                                                   from_day, to_day):
                        for commit_date in contributor["code_author_date_list"]:
                            if from_day <= commit_date <= to_day:
                                org_name_set.add(org.get("org_name"))
                                break
            contribution_last += len(org_name_set)
    result = {
        "org_contribution_last": contribution_last
    }
    return result


def is_maintained(client, git_index, contributors_index, date, repos_list, level):
    is_maintained_list = []
    git_repos_list = [repo_url+'.git' for repo_url in repos_list]
    if level == "repo":
        date_list_maintained = get_date_list(begin_date=str(
            date-timedelta(days=90)), end_date=str(date), freq='7D')
        for day in date_list_maintained:
            query_git_commit_i = get_uuid_count_query(
                "cardinality", git_repos_list, "hash", size=0, from_date=day-timedelta(days=7), to_date=day)
            commit_frequency_i = client.search(index=git_index, body=query_git_commit_i)[
                'aggregations']["count_of_uuid"]['value']
            if commit_frequency_i > 0:
                is_maintained_list.append("True")
            else:
                is_maintained_list.append("False")

    elif level in ["project", "community"]:
        active_repo_list = get_activity_repo_list(client, contributors_index, date, repos_list, from_date=date-timedelta(days=30), \
                    date_field_list=["code_author_date_list"])
        for repo in repos_list:
            if repo in active_repo_list:
                is_maintained_list.append("True")
            else:
                is_maintained_list.append("False")

    try:
        is_maintained = is_maintained_list.count("True") / len(is_maintained_list)
    except ZeroDivisionError:
        is_maintained = 0
    result = {
        'is_maintained': round(is_maintained, 4)
    }
    return result


def maintained(client, git_index, issue_index, date, repos_list):
    """ Is the project at least 90 days old, and maintained? """
    git_repos_list = [repo_url+'.git' for repo_url in repos_list]
    commit_query = get_uuid_count_query("cardinality", git_repos_list, "hash", size=0, from_date=date-timedelta(days=90), to_date=date)
    commit_count = client.search(index=git_index, body=commit_query)['aggregations']["count_of_uuid"]['value']
    
    issue_query = get_uuid_count_query("cardinality", repos_list, "uuid", size=0, from_date=date-timedelta(days=90), to_date=date)
    issue_count = client.search(index=issue_index, body=issue_query)['aggregations']["count_of_uuid"]['value']
    
    score = min(int((commit_count + issue_count) * 10 / 13), 10)
    
    result = {
        "maintained": score,
        "maintained_detail": {
            "commit_count": commit_count,
            "issue_count": issue_count
        }
    }
    return result



def commit_pr_linked_ratio(client, contributors_index, git_index, pr_index, date, repos_list):
    """ Determine the percentage of new code commit link pull request in the last 90 days """
    code_commit_count = commit_count(client, contributors_index, date, repos_list)["commit_count"]
    code_commit_pr_linked_count = commit_pr_linked_count(client, git_index, pr_index, date, repos_list)["commit_pr_linked_count"]

    result = {
        'commit_pr_linked_ratio': code_commit_pr_linked_count/code_commit_count if code_commit_count > 0 else None
    }
    return result


def commit_count(client, contributors_index, date, repo_list, from_date=None):
    """ Determine the number of commits in the past 90 days. """
    if from_date is None:
        from_date = date - timedelta(days=90)
    to_date = date
    commit_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                   "code_author_date_list")
    result = {
        'commit_count': get_commit_count(from_date, to_date, commit_contributor_list),
        'commit_count_bot': get_commit_count(from_date, to_date, commit_contributor_list, is_bot=True),
        'commit_count_without_bot': get_commit_count(from_date, to_date, commit_contributor_list, is_bot=False)
    }
    return result

def commit_count_quarterly(client, contributors_index, to_date, repo_list, from_date):
    commit_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                   "code_author_date_list")
    result = {
        'commit_count_quarterly': get_commit_count(from_date, to_date, commit_contributor_list),
        'commit_count_quarterly_bot': get_commit_count(from_date, to_date, commit_contributor_list, is_bot=True),
        'commit_count_quarterly_without_bot': get_commit_count(from_date, to_date, commit_contributor_list, is_bot=False)
    }
    return result

def commit_pr_linked_count(client, git_index, pr_index, date, repos_list):
    """ Determine the numbers of new code commit link pull request in the last 90 days. """
    def get_pr_list_by_commit_hash(hash_list):
        pr_hits = []
        hash_list_group = split_list(hash_list)
        for hash_l in hash_list_group:
            pr_hit = client.search(index=pr_index, body=get_pr_query_by_commit_hash(repos_list, hash_l))["hits"]["hits"]
            pr_hits = pr_hits + pr_hit
        return pr_hits
    
    repo_git_list = [repo+".git" for repo in repos_list]
    commit_message_list = get_message_list(client, git_index, date - timedelta(days=90), date, repo_git_list)
    commit_hash_set = {message["hash"] for message in commit_message_list}
    commit_hash_list = list(commit_hash_set)
    if len(commit_hash_list) == 0:
        return {'commit_pr_linked_count': 0}
    
    pr_all_message = get_pr_list_by_commit_hash(commit_hash_list)
    pr_commit_hash = set()
    for pr_item in pr_all_message:
        for commit_data in pr_item["_source"].get("commits_data", []):
            pr_commit_hash.add(commit_data)
        merge_commit_sha = pr_item["_source"].get("merge_commit_sha", None)
        if merge_commit_sha:
            pr_commit_hash.add(merge_commit_sha)
    linked_count = commit_hash_set & pr_commit_hash

    result = {
        'commit_pr_linked_count': len(linked_count)
    }
    return result


def lines_of_code_frequency(client, git_index, date, repos_list):
    """ Determine the average number of lines touched (lines added plus lines removed) per week in the past 90 """
    result = {
        "lines_of_code_frequency": LOC_frequency(client, git_index, date, repos_list, 'lines_changed')
    }
    return result


def lines_add_of_code_frequency(client, git_index, date, repos_list):
    """ Determine the average number of lines touched (lines added) per week in the past 90 """
    result = {
        "lines_add_of_code_frequency": LOC_frequency(client, git_index, date, repos_list, 'lines_added')
    }
    return result


def lines_remove_of_code_frequency(client, git_index, date, repos_list):
    """ Determine the average number of lines touched (lines removed) per week in the past 90 """
    result = {
        "lines_remove_of_code_frequency": LOC_frequency(client, git_index, date, repos_list, 'lines_removed')
    }
    return result


def get_commit_count(from_date, to_date, contributor_list, company=None, is_bot=None):
    from_date_str = from_date.strftime("%Y-%m-%d")
    to_date_str = to_date.strftime("%Y-%m-%d")
    commit_count = 0
    for contributor in contributor_list:
        if is_bot is None or contributor["is_bot"] == is_bot:
            if company is None:
                for commit_date in contributor["code_author_date_list"]:
                    if from_date_str <= commit_date <= to_date_str:
                        commit_count += 1
            else:
                for org in contributor["org_change_date_list"]:
                    if org.get("org_name") is not None and org.get("org_name") == company and \
                            check_times_has_overlap(org["first_date"], org["last_date"], from_date_str, to_date_str):
                        for commit_date in contributor["code_author_date_list"]:
                            if get_latest_date(from_date_str, org["first_date"]) <= commit_date < \
                                    get_oldest_date(org["last_date"], to_date_str):
                                commit_count += 1
    return commit_count


def LOC_frequency(client, git_index, date, repos_list, field='lines_changed'):
    """ Determine the average number of lines touched per week in the past 90 """
    git_repos_list = [repo_url+'.git' for repo_url in repos_list]
    query_LOC_frequency = get_uuid_count_query(
        'sum', git_repos_list, field, 'grimoire_creation_date', size=0, from_date=date-timedelta(days=90), to_date=date)
    loc_frequency = client.search(index=git_index, body=query_LOC_frequency)[
        'aggregations']['count_of_uuid']['value']
    return loc_frequency/12.85
    #



def get_message_list(client, index_name, from_date, to_date, repo_list):
    """ Getting a list of message data in the from_date,to_date time period. """
    result_list = []
    query = get_message_list_query(field_values=repo_list, size=500, from_date=from_date, to_date=to_date)
    message_list = get_all_index_data(client, index=index_name, body=query)
    if len(message_list) > 0:
        result_list = result_list + [message["_source"] for message in message_list]
    return result_list

def commit_count_year(client, contributors_index, date, repo_list, from_date=None):
    """ Determine the number of commits in the past 3 years. """
    if from_date is None:
        from_date = (date - relativedelta(years=3)).replace(month=1, day=1)
    to_date = date
    commit_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                   "code_author_date_list")
    result = {
        'commit_count_year': get_commit_count(from_date, to_date, commit_contributor_list),
        'commit_count_bot_year': get_commit_count(from_date, to_date, commit_contributor_list, is_bot=True),
        'commit_count_without_bot_year': get_commit_count(from_date, to_date, commit_contributor_list, is_bot=False)
    }
    return result


def lines_of_code_frequency_year(client, git_index, date, repos_list):
    """ Determine the  number of lines touched (lines added plus lines removed) per week in the past 3 years """
    result = {
        "lines_of_code_frequency_year": LOC_frequency_year(client, git_index, date, repos_list, 'lines_changed')
    }
    return result
#


def LOC_frequency_year(client, git_index, date, repos_list, field='lines_changed'):
    """ Determine the average number of lines touched per week in the past 3 years """
    git_repos_list = [repo_url + '.git' for repo_url in repos_list]
    query_LOC_frequency = get_uuid_count_query(
        'sum', git_repos_list, field, 'grimoire_creation_date', size=0,
        from_date=(date - relativedelta(years=3)).replace(month=1, day=1), to_date=date)
    loc_frequency = client.search(index=git_index, body=query_LOC_frequency)[
        'aggregations']['count_of_uuid']['value']
    return loc_frequency / 12.85


# =========================
# v2: 按周期（月 / 季度 / 年）的 Commit 指标
# =========================

from datetime import datetime


def _get_period_range(end_date: datetime, period: str):
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

def _get_period_range2(end_date: datetime, period: str):
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


def _git_repo_list(repos_list):
    return [repo + ".git" for repo in repos_list]


def commit_count_by_period(client, git_index, end_date, repos_list, period="month"):
    """
    代码提交次数：周期内新增的 Commit 总数。
    输出：commit_count（次），period。
    """
    from_date, to_date = _get_period_range(end_date, period)
    git_repos = _git_repo_list(repos_list)
    query = get_uuid_count_query(
        "cardinality", git_repos, "hash", "grimoire_creation_date", size=0, from_date=from_date, to_date=to_date
    )
    query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    total = client.search(index=git_index, body=query)["aggregations"]["count_of_uuid"]["value"]
    return {"commit_count": total, "period": period}


def lines_changed_by_period(client, git_index, end_date, repos_list, period="month"):
    """
    新增代码行数：周期内代码行变动总量。
    输出：lines_added, lines_removed, period。
    """
    from_date, to_date = _get_period_range(end_date, period)
    git_repos = _git_repo_list(repos_list)

    def _sum_field(field):
        q = get_uuid_count_query("sum", git_repos, field, "grimoire_creation_date", size=0, from_date=from_date, to_date=to_date)
        res = client.search(index=git_index, body=q)
        return res["aggregations"]["count_of_uuid"]["value"] if res["hits"]["total"]["value"] > 0 else 0

    added = _sum_field("lines_added")
    removed = _sum_field("lines_removed")
    return {"lines_added": added, "lines_removed": removed, "period": period}


def org_code_contribution_by_period(client, git_index, end_date, repos_list, period="month"):
    """
    组织代码贡献量：周期内组织贡献的代码行数（新增）。
    近似：author_org_name 存在且不为 Unknown 的提交，累加 lines_added。
    """
    from_date, to_date = _get_period_range(end_date, period)
    git_repos = _git_repo_list(repos_list)
    query = get_uuid_count_query(
        "sum", git_repos, "lines_added", "grimoire_creation_date", size=0, from_date=from_date, to_date=to_date
    )
    query["query"]["bool"]["must"].append({"exists": {"field": "author_org_name"}})
    query["query"]["bool"]["must_not"] = [
        {"match_phrase": {"author_org_name": "Unknown"}},
        {"match_phrase": {"author_org_name": ""}},
    ]
    res = client.search(index=git_index, body=query)
    org_added = res["aggregations"]["count_of_uuid"]["value"] if res["hits"]["total"]["value"] > 0 else 0
    return {"org_code_contribution_lines": org_added, "period": period}


def org_code_contribution_ratio_by_period(client, git_index, end_date, repos_list, period="month"):
    """
    组织代码贡献量占比：周期内组织贡献的新增代码行数 / 周期内总新增代码行数。
    """
    total = lines_changed_by_period(client, git_index, end_date, repos_list, period)["lines_added"]
    org_lines = org_code_contribution_by_period(client, git_index, end_date, repos_list, period)["org_code_contribution_lines"]
    return {
        "org_code_contribution_ratio": (org_lines / total) if total > 0 else None,
        "org_code_contribution_lines": org_lines,
        "total_lines_added": total,
        "period": period,
    }


def personal_code_contribution_by_period(client, git_index, end_date, repos_list, period="month"):
    """
    个人代码贡献量：周期内个人贡献者提交的代码行数（新增）。
    近似：author_org_name 缺失或 Unknown 的提交，累加 lines_added。
    """
    from_date, to_date = _get_period_range(end_date, period)
    git_repos = _git_repo_list(repos_list)
    query = get_uuid_count_query(
        "sum", git_repos, "lines_added", "grimoire_creation_date", size=0, from_date=from_date, to_date=to_date
    )
    query["query"]["bool"]["must_not"] = [
        {"exists": {"field": "author_org_name"}},
        {"match_phrase": {"author_org_name": "Unknown"}},
        {"match_phrase": {"author_org_name": ""}},
    ]
    res = client.search(index=git_index, body=query)
    personal_added = res["aggregations"]["count_of_uuid"]["value"] if res["hits"]["total"]["value"] > 0 else 0
    return {"personal_code_contribution_lines": personal_added, "period": period}


def personal_code_contribution_ratio_by_period(client, git_index, end_date, repos_list, period="month"):
    """
    个人代码贡献量占比：周期内个人贡献新增代码行数 / 周期内总新增代码行数。
    """
    total = lines_changed_by_period(client, git_index, end_date, repos_list, period)["lines_added"]
    personal_lines = personal_code_contribution_by_period(client, git_index, end_date, repos_list, period)["personal_code_contribution_lines"]
    return {
        "personal_code_contribution_ratio": (personal_lines / total) if total > 0 else None,
        "personal_code_contribution_lines": personal_lines,
        "total_lines_added": total,
        "period": period,
    }

# 