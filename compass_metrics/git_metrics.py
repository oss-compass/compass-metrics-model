""" Set of git related metrics """

from compass_metrics.db_dsl import (get_updated_since_query,
                                    get_uuid_count_query)
from compass_metrics.contributor_metrics import get_contributor_list
from compass_common.datetime import (get_time_diff_months, 
                                    check_times_has_overlap, 
                                    get_oldest_date, 
                                    get_latest_date,
                                    get_date_list)
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


def org_commit_frequency(client, contributors_index, date, repo_list):
    """ Determine the average number of commits with organization affiliation per week in the past 90 days. """
    from_date = date - timedelta(days=90)
    to_date = date
    commit_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                   "code_commit_date_list")
    from_date_str = from_date.strftime("%Y-%m-%d")
    to_date_str = to_date.strftime("%Y-%m-%d")
    total_commit_count = 0
    org_commit_count = 0
    org_commit_bot_count = 0
    org_commit_without_bot_count = 0
    org_commit_detail_dict = {}

    for contributor in commit_contributor_list:
        commit_date_list = [x for x in sorted(contributor["code_commit_date_list"]) if from_date_str <= x < to_date_str]
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
                                                   "code_commit_date_list")
    contribution_last = 0
    repo_contributor_group_dict = {}
    for contributor in commit_contributor_list:
        repo_contributor_list = repo_contributor_group_dict.get(contributor["repo_name"], [])
        repo_contributor_list.append(contributor)
        repo_contributor_group_dict[contributor["repo_name"]] = repo_contributor_list

    date_list = get_date_list(begin_date_str=str(from_date), end_date_str=str(to_date), freq='7D')
    for repo, repo_contributor_list in repo_contributor_group_dict.items():
        for day in date_list:
            org_name_set = set()
            from_day = (day - timedelta(days=7)).strftime("%Y-%m-%d")
            to_day = day.strftime("%Y-%m-%d")
            for contributor in repo_contributor_list:
                for org in contributor["org_change_date_list"]:
                    if org.get("org_name") is not None and check_times_has_overlap(org["first_date"], org["last_date"],
                                                                                   from_day, to_day):
                        for commit_date in contributor["code_commit_date_list"]:
                            if from_day <= commit_date <= to_day:
                                org_name_set.add(org.get("org_name"))
                                break
            contribution_last += len(org_name_set)
    result = {
        "org_contribution_last": contribution_last
    }
    return result


def is_maintained(client, git_index, date, repos_list, level):
    is_maintained_list = []
    if level == "repo":
        date_list_maintained = get_date_list(begin_date=str(
            date-timedelta(days=90)), end_date=str(date), freq='7D')
        for day in date_list_maintained:
            query_git_commit_i = get_uuid_count_query(
                "cardinality", repos_list, "hash", size=0, from_date=day-timedelta(days=7), to_date=day)
            commit_frequency_i = client.search(index=git_index, body=query_git_commit_i)[
                'aggregations']["count_of_uuid"]['value']
            if commit_frequency_i > 0:
                is_maintained_list.append("True")
            else:
                is_maintained_list.append("False")

    elif level in ["project", "community"]:
        for repo in repos_list:
            query_git_commit_i = get_uuid_count_query("cardinality",[repo+'.git'], "hash",from_date=date-timedelta(days=30), to_date=date)
            commit_frequency_i = client.search(index=git_index, body=query_git_commit_i)['aggregations']["count_of_uuid"]['value']
            if commit_frequency_i > 0:
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


def git_pr_linked_ratio(client, git_index, pr_index, date, repos_list):
    commit_frequency = get_uuid_count_query("cardinality", repos_list, "hash", "grimoire_creation_date", size=10000, from_date=date - timedelta(days=90), to_date=date)
    commits_without_merge_pr = {
        "bool": {
            "should": [{"script": {
                "script": "if (doc.containsKey('message') && doc['message'].size()>0 &&doc['message'].value.indexOf('Merge pull request') == -1){return true}"
            }
            }],
            "minimum_should_match": 1}
    }
    commit_frequency["query"]["bool"]["must"].append(commits_without_merge_pr)
    commit_message = client.search(index=git_index, body=commit_frequency)
    commit_message_dict = {}
    commit_count = commit_message['aggregations']["count_of_uuid"]['value']
    commit_pr_cout = 0
    commit_all_message = [commit_message_i['_source']['hash']  for commit_message_i in commit_message['hits']['hits']]

    for commit_message_i in set(commit_all_message):
        commit_hash = commit_message_i
        if commit_hash in commit_message_dict:
            commit_pr_cout += commit_message_dict[commit_hash]
        else:
            pr_message = get_uuid_count_query("cardinality", repos_list, "uuid", "grimoire_creation_date", size=0)
            commit_hash_query = { "bool": {"should": [ {"match_phrase": {"commits_data": commit_hash} }],
                                    "minimum_should_match": 1
                                }
                            }
            pr_message["query"]["bool"]["must"].append(commit_hash_query)
            prs = client.search(index=pr_index, body=pr_message)
            if prs['aggregations']["count_of_uuid"]['value']>0:
                commit_message_dict[commit_hash] = 1
                commit_pr_cout += 1
            else:
                commit_message_dict[commit_hash] = 0
    if commit_count>0:
        # return len(commit_all_message), commit_pr_cout, commit_pr_cout/len(commit_all_message)
        git_pr_linked_ratio = commit_pr_cout/len(commit_all_message)
    else:
        # return 0, None, None
        git_pr_linked_ratio = None

    result = {
        'git_pr_linked_ratio': git_pr_linked_ratio
    }
    return result


def LOC_frequency(client, git_index, date, repos_list, field='lines_changed'):
    query_LOC_frequency = get_uuid_count_query(
        'sum', repos_list, field, 'grimoire_creation_date', size=0, from_date=date-timedelta(days=90), to_date=date)
    LOC_frequency = client.search(index=git_index, body=query_LOC_frequency)[
        'aggregations']['count_of_uuid']['value']
    result = {
        'LOC_frequency': LOC_frequency/12.85
    }
    return result
