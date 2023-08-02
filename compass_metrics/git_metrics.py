""" Set of git related metrics """

from compass_metrics.db_dsl import get_updated_since_query
from compass_metrics.common import get_contributor_list
from compass_common.datetime import (get_time_diff_months, 
                                    check_times_has_overlap, 
                                    get_oldest_date, 
                                    get_latest_date)
from datetime import timedelta


def created_since(client, git_index, date, repo_list):
    """ Determine how long a repository has existed since it was created (in months). """
    created_since_list = []
    for repo in repo_list:
        query_first_commit_since = get_updated_since_query(
            [repo], date_field='grimoire_creation_date', to_date=date, order="asc")
        first_commit_since = client.search(index=git_index, body=query_first_commit_since)['hits']['hits']
        if len(first_commit_since) > 0:
            creation_since = first_commit_since[0]['_source']["grimoire_creation_date"]
            created_since_list.append(
                get_time_diff_months(creation_since, str(date)))

    result = {
        "created_since": round(sum(created_since_list), 4) if created_since_list else None
    }
    return result


def updated_since(client, git_index, date, repo_list):
    """ Determine the average time per repository since the repository was last updated (in months). """
    updated_since_list = []
    for repo in repo_list:
        query_updated_since = get_updated_since_query(
            [repo], date_field='metadata__updated_on', to_date=date)
        updated_since = client.search(index=git_index, body=query_updated_since)['hits']['hits']
        if updated_since:
            updated_since_list.append(get_time_diff_months(
                updated_since[0]['_source']["metadata__updated_on"], str(date)))
    result = {
        "updated_since": float(round(sum(updated_since_list) / len(updated_since_list), 4)) if updated_since_list else 0
    }
    return result


def commit_frequency(client, contributors_index, date, repo_list):
    """ Determine the average number of commits per week in the past 90 days. """
    def get_commit_frequency(from_date, to_date, contributor_list, company=None, is_bot=None):
        from_date_str = from_date.strftime("%Y-%m-%d")
        to_date_str = to_date.strftime("%Y-%m-%d")
        commit_count = 0
        for contributor in contributor_list:
            if is_bot is None or contributor["is_bot"] == is_bot:
                if company is None:
                    for commit_date in contributor["code_commit_date_list"]:
                        if from_date_str <= commit_date <= to_date_str:
                            commit_count += 1
                else:
                    for org in contributor["org_change_date_list"]:
                        if org.get("org_name") is not None and org.get("org_name") == company and \
                                check_times_has_overlap(org["first_date"], org["last_date"], from_date_str, to_date_str):
                            for commit_date in contributor["code_commit_date_list"]:
                                if get_latest_date(from_date_str, org["first_date"]) <= commit_date < \
                                        get_oldest_date(org["last_date"], to_date_str):
                                    commit_count += 1
        return commit_count/12.85

    from_date = date - timedelta(days=90)
    to_date = date
    commit_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                   "code_commit_date_list")
    result = {
        'commit_frequency': get_commit_frequency(from_date, to_date, commit_contributor_list),
        'commit_frequency_bot': get_commit_frequency(from_date, to_date, commit_contributor_list, is_bot=True),
        'commit_frequency_without_bot': get_commit_frequency(from_date, to_date, commit_contributor_list, is_bot=False)
    }
    return result


def org_count(client, contributors_index, date, repo_list):
    """ Number of organizations to which active code contributors belong in the past 90 days """
    from_date = date - timedelta(days=90)
    to_date = date
    commit_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                   "code_commit_date_list")
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


