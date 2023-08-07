""" Set of pr related metrics """

from compass_metrics.db_dsl import (get_uuid_count_query, 
                                    get_pr_closed_uuid_count, 
                                    get_pr_message_count,
                                    get_pr_linked_issue_count)
from datetime import timedelta
from compass_common.datetime import get_time_diff_days
from compass_common.datetime import str_to_datetime
from compass_common.algorithm_utils import get_medium


def pr_open_time(client, pr_index, date, repos_list):
    query_pr_opens = get_uuid_count_query("avg", repos_list, "time_to_first_attention_without_bot",
                                                "grimoire_creation_date", size=10000, from_date=date-timedelta(days=90), to_date=date)
    query_pr_opens["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true"}})
    pr_opens_items = client.search(
        index=pr_index, body=query_pr_opens)['hits']['hits']
    if len(pr_opens_items) == 0:
        return None, None
    pr_open_time_repo = []
    for item in pr_opens_items:
        if 'state' in item['_source']:
            if item['_source']['state'] == 'merged' and item['_source']['merged_at'] and str_to_datetime(item['_source']['merged_at']) < date:
                pr_open_time_repo.append(get_time_diff_days(
                    item['_source']['created_at'], item['_source']['merged_at']))
            if item['_source']['state'] == 'closed' and str_to_datetime(item['_source']['closed_at'] or item['_source']['updated_at']) < date:
                pr_open_time_repo.append(get_time_diff_days(
                    item['_source']['created_at'], item['_source']['closed_at'] or item['_source']['updated_at']))
            else:
                pr_open_time_repo.append(get_time_diff_days(
                    item['_source']['created_at'], str(date)))
    if len(pr_open_time_repo) == 0:
        return None, None
    pr_open_time_repo_avg = float(sum(pr_open_time_repo)/len(pr_open_time_repo))
    pr_open_time_repo_mid = get_medium(pr_open_time_repo)

    result = {
        "pr_open_time_repo_avg": pr_open_time_repo_avg,
        "pr_open_time_repo_mid": pr_open_time_repo_mid
    }

    return result


def code_review_count(client, pr_index, date, repo_list):
    query_pr_comments_count = get_uuid_count_query(
        "sum", repo_list, "num_review_comments_without_bot", size=0, from_date=(date - timedelta(days=90)),
        to_date=date)
    query_pr_comments_count["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true"}})
    prs = client.search(index=pr_index, body=query_pr_comments_count)
    try:
        comment_count = prs['aggregations']["count_of_uuid"]['value'] / prs["hits"]["total"]["value"]
    except ZeroDivisionError:
        comment_count = None
    result = {
        'code_review_count': round(comment_count, 4) if comment_count is not None else None
    }
    return result


def closed_pr_count(client, pr_index, date, repos_list):
    query_pr_closed = get_pr_closed_uuid_count(
        "cardinality", repos_list, "uuid", from_date=(date-timedelta(days=90)), to_date=date)
    pr_closed = client.search(index=pr_index, body=query_pr_closed)[
        'aggregations']["count_of_uuid"]['value']

    result = {
        "pr_closed": pr_closed
    }

    return result


def code_review_ratio(client, pr_index, date, repos_list):
    query_pr_count = get_uuid_count_query(
        "cardinality", repos_list, "uuid", size=0, from_date=(date-timedelta(days=90)), to_date=date)
    pr_count = client.search(index=pr_index, body=query_pr_count)[
        'aggregations']["count_of_uuid"]['value']
    query_pr_body = get_pr_message_count(repos_list, "uuid", "grimoire_creation_date", size=0, 
                                         filter_field="num_review_comments_without_bot", from_date=(date-timedelta(days=90)), to_date=date)
    prs = client.search(index=pr_index, body=query_pr_body)[
        'aggregations']["count_of_uuid"]['value']
    try:
        return prs/pr_count, pr_count
    except ZeroDivisionError:
        return None, 0


def code_merge_ratio(client, pr_index, date, repos_list):
    query_pr_body = get_uuid_count_query("cardinality", repos_list, "uuid", "grimoire_creation_date", size=0, from_date=(date-timedelta(days=90)), to_date=date)
    query_pr_body["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true"}})
    query_pr_body["query"]["bool"]["must"].append({"match_phrase": {"merged": "true"}})
    pr_merged_count = client.search(index=pr_index, body=query_pr_body)[
        'aggregations']["count_of_uuid"]['value']
    query_pr_body["query"]["bool"]["must"].append({
                        "script": {
                            "script": "if(doc['merged_by_data_name'].size() > 0 && doc['author_name'].size() > 0 && doc['merged_by_data_name'].value !=  doc['author_name'].value){return true}"
                        }
                    })
    prs = client.search(index=pr_index, body=query_pr_body)[
        'aggregations']["count_of_uuid"]['value']

    try:
        result = {
            "prs/pr_merged_count": prs/pr_merged_count, 
            "pr_merged_count": pr_merged_count
        }
        return result
    except ZeroDivisionError:
        result = {
            "prs/pr_merged_count": None, 
            "pr_merged_count": 0
        }
        return result


def pr_issue_linked(client, pr_index, pr_comments_index, date, repos_list):
    pr_linked_issue = 0
    for repo in repos_list:
        query_pr_linked_issue = get_pr_linked_issue_count(
            repo, from_date=date-timedelta(days=90), to_date=date)
        pr_linked_issue += client.search(index=(pr_index, pr_comments_index), body=query_pr_linked_issue)[
            'aggregations']["count_of_uuid"]['value']
    query_pr_count = get_uuid_count_query(
        "cardinality", repos_list, "uuid", size=0, from_date=(date-timedelta(days=90)), to_date=date)
    query_pr_count["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true"}})
    pr_count = client.search(index=pr_index,
                             body=query_pr_count)[
        'aggregations']["count_of_uuid"]['value']
    try:
        result = {
            "pr_issue_linked_ratio": pr_linked_issue/pr_count
        }
        return result
    except ZeroDivisionError:
        result = {
            "pr_issue_linked_ratio": None
        }
        return result