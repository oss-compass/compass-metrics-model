""" Set of issue related metrics """

from compass_metrics.db_dsl import get_uuid_count_query, get_updated_issues_count_query
from datetime import timedelta
from compass_common.datetime import get_time_diff_days
from compass_common.algorithm_utils import get_medium
from compass_common.opensearch_utils import get_all_index_data


def issue_first_reponse(client, issue_index, date, repos_list):
    query_issue_first_reponse_avg = get_uuid_count_query(
        "avg", repos_list, "time_to_first_attention_without_bot", "grimoire_creation_date", size=0, from_date=date-timedelta(days=90), to_date=date)
    query_issue_first_reponse_avg["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})

    issue_first_reponse = client.search(index=issue_index, body=query_issue_first_reponse_avg)
    if issue_first_reponse["hits"]["total"]["value"] == 0:
        return { "issue_first_reponse_avg": None, "issue_first_reponse_mid": None }
    issue_first_reponse_avg = issue_first_reponse['aggregations']["count_of_uuid"]['value']

    query_issue_first_reponse_mid = get_uuid_count_query(
        "percentiles", repos_list, "time_to_first_attention_without_bot", "grimoire_creation_date", size=0, from_date=date-timedelta(days=90), to_date=date)
    query_issue_first_reponse_mid["aggs"]["count_of_uuid"]["percentiles"]["percents"] = [
        50]
    query_issue_first_reponse_mid["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
    issue_first_reponse_mid = client.search(index=issue_index, body=query_issue_first_reponse_mid)[
        'aggregations']["count_of_uuid"]['values']['50.0']

    result = {
        "issue_first_reponse_avg": issue_first_reponse_avg,
        "issue_first_reponse_mid": issue_first_reponse_mid
    }
    return result


def bug_issue_open_time(client, issue_index, date, repos_list):
    query_issue_opens = get_uuid_count_query("avg", repos_list, "time_to_first_attention_without_bot",
                                                    "grimoire_creation_date", size=1000, from_date=date-timedelta(days=90), to_date=date)
    query_issue_opens["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false" }})
    bug_query = {
        "bool": {
            "should": [{
                "script": {
                    "script": "if (doc.containsKey('labels') && doc['labels'].size()>0) { for (int i = 0; i < doc['labels'].length; ++i){ if(doc['labels'][i].toLowerCase().indexOf('bug')!=-1|| doc['labels'][i].toLowerCase().indexOf('缺陷')!=-1){return true;}}}"
                }
            },
                {
                "script": {
                    "script": "if (doc.containsKey('issue_type') && doc['issue_type'].size()>0) { for (int i = 0; i < doc['issue_type'].length; ++i){ if(doc['issue_type'][i].toLowerCase().indexOf('bug')!=-1 || doc['issue_type'][i].toLowerCase().indexOf('缺陷')!=-1){return true;}}}"
                }
            }],
            "minimum_should_match": 1
        }
    }
    query_issue_opens["query"]["bool"]["must"].append(bug_query)
    issue_opens_items = get_all_index_data(client, issue_index, query_issue_opens)
    if len(issue_opens_items) == 0:
        return { "bug_issue_open_time_avg": None, "bug_issue_open_time_mid": None }
    issue_open_time_repo = []
    date_str = date.isoformat()
    for item in issue_opens_items:
        if 'state' in item['_source']:
            if item['_source']['closed_at'] and item['_source']['state'] in ['closed', 'rejected'] and item['_source']['closed_at'] < date_str:
                issue_open_time_repo.append(get_time_diff_days(
                    item['_source']['created_at'], item['_source']['closed_at']))
            else:
                issue_open_time_repo.append(get_time_diff_days(
                    item['_source']['created_at'],date_str))
    issue_open_time_repo_avg = sum(issue_open_time_repo)/len(issue_open_time_repo)
    issue_open_time_repo_mid = get_medium(issue_open_time_repo)
    result = {
        "bug_issue_open_time_avg": issue_open_time_repo_avg,
        "bug_issue_open_time_mid": issue_open_time_repo_mid
    }
    return result


def comment_frequency(client, issue_index, date, repo_list, from_date=None):
    """ Determine the average number of comments per issue created in the last 90 days. """
    if from_date is None:
        from_date = (date-timedelta(days=90))
    query_issue_comments_count = get_uuid_count_query(
        "sum", repo_list, "num_of_comments_without_bot", date_field='grimoire_creation_date', size=0,
        from_date=from_date, to_date=date)
    query_issue_comments_count["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
    issue = client.search(index=issue_index, body=query_issue_comments_count)
    try:
        comment_count = float(issue['aggregations']["count_of_uuid"]['value'] / issue["hits"]["total"]["value"])
    except ZeroDivisionError:
        comment_count = None
    result = {
        'comment_frequency': float(round(comment_count, 4)) if comment_count is not None else None
    }
    return result


def closed_issues_count(client, issue_index, date, repo_list):
    """ Determine the number of issues closed in the last 90 days. """
    query_issue_closed = get_uuid_count_query(
        "cardinality", repo_list, "uuid", from_date=(date-timedelta(days=90)), to_date=date)
    query_issue_closed["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false" }})
    query_issue_closed["query"]["bool"]["must_not"] = [
                        {"term": {"state": "open"}},
                        {"term": {"state": "progressing"}}
                    ]
    issue_closed = client.search(index=issue_index, body=query_issue_closed)[
        'aggregations']["count_of_uuid"]['value']
    result = {
        'closed_issues_count': issue_closed
    }
    return result


def updated_issues_count(client, issue_comments_index, date, repo_list):
    """ Determine the number of issues updated in the last 90 days. """
    updated_issues_count_query = get_updated_issues_count_query(repo_list, date-timedelta(days=90), date)
    issues_count = client.search(index=issue_comments_index, body=updated_issues_count_query)[
        'aggregations']["count_of_uuid"]['value']
    result = {
        'updated_issues_count': issues_count
    }
    return result


def issue_count(client, issue_index, date, repo_list, from_date=None):
    """ The number of issue created in the last 90 days. """
    if from_date is None:
        from_date = (date-timedelta(days=90))
    query = get_uuid_count_query(
        "cardinality", repo_list, "uuid", size=0, from_date=from_date, to_date=date)
    query["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
    query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    count = client.search(index=issue_index, body=query)['aggregations']["count_of_uuid"]['value']
    result = {
        "issue_count": count
    }
    return result


def issue_unresponsive_count(client, issue_index, date, repo_list, from_date=None):
    """Defines the number of new issues created in the last 90 days that are still open and have no comments."""
    if from_date is None:
        from_date = (date-timedelta(days=90))
    query = get_uuid_count_query(
        "cardinality", repo_list, "uuid", size=0, from_date=from_date, to_date=date)
    query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    query["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
    query["query"]["bool"]["must"].append({"match_phrase": {"num_of_comments_without_bot": 0}})
    query["query"]["bool"]["must"].append({"terms": {"state": ["open", "progressing"]}})
    unresponsive_count = client.search(index=issue_index, body=query)['aggregations']["count_of_uuid"]['value']
    result = {
        "issue_unresponsive_count": unresponsive_count
    }
    return result


def issue_unresponsive_ratio(client, issue_index, date, repo_list, from_date=None):
    """Measures the ratio between the total number of issue and the total number
    of unresponsive issue in the last 90 days."""
    if from_date is None:
        from_date = (date-timedelta(days=90))
    count = issue_unresponsive_count(client, issue_index, date, repo_list, from_date)["issue_unresponsive_count"]
    total_count = issue_count(client, issue_index, date, repo_list, from_date)["issue_count"]

    result = {
        "issue_unresponsive_ratio": count/total_count if count > 0 else None
    }
    return result


def issue_completion_ratio(client, issue_index, date, repo_list, from_date=None):
    """Measures the ratio between the total number of issue and the total number
    of closed issue in the last 90 days."""
    if from_date is None:
        from_date = (date-timedelta(days=90))
    count = create_close_issue_count(client, issue_index, date, repo_list, from_date)["create_close_issue_count"]
    total_count = issue_count(client, issue_index, date, repo_list, from_date)["issue_count"]

    result = {
        "issue_completion_ratio": count/total_count if count > 0 else None
    }
    return result


def create_close_issue_count(client, issue_index, date, repo_list, from_date=None):
    """The number of issue created in the last 90 days and it has been closed or rejected"""
    if from_date is None:
        from_date = (date-timedelta(days=90))
    query = get_uuid_count_query(
        "cardinality", repo_list, "uuid", size=0, from_date=from_date, to_date=date)
    query["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
    query["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    query["query"]["bool"]["filter"].append({
                                    "range": {
                                        "closed_at": {
                                            "gte": from_date.strftime("%Y-%m-%d"),
                                            "lt": date.strftime("%Y-%m-%d")
                                        }
                                    }
                                })
    issue_closed_count = client.search(index=issue_index, body=query)['aggregations']["count_of_uuid"]['value']
    result = {
        "create_close_issue_count": issue_closed_count
    }
    return result


def issue_state_distribution(client, issue_index, date, repo_list, from_date=None):
    """Define the distribution of the states of new issues in the last 90 days
    github issue states are 'open' and 'closed',
    gitee issue states are 'open', 'progressing', 'rejected' and 'closed'
    """
    if from_date is None:
        from_date = (date-timedelta(days=90))
    query = get_uuid_count_query(
        "terms", repo_list, "state", size=0, from_date=from_date, to_date=date)
    query["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
    buckets = client.search(index=issue_index, body=query)['aggregations']["count_of_uuid"]['buckets']
    total_issue_count = sum([bucket["doc_count"] for bucket in buckets])
    if total_issue_count == 0:
        return {"issue_state_distribution": None}
    state_distribution = {}
    for bucket in buckets:
        state_distribution[bucket["key"]] = {"count": bucket["doc_count"], "ratio": bucket["doc_count"] / total_issue_count}
    result = {
        "issue_state_distribution": state_distribution
    }
    return result


def issue_comment_distribution(client, issue_index, date, repo_list, from_date=None):
    """Define the distribution of the comment of new issues in the last 90 days"""
    if from_date is None:
        from_date = (date-timedelta(days=90))
    query = get_uuid_count_query(
        "terms", repo_list, "num_of_comments_without_bot", size=0, from_date=from_date, to_date=date)
    query["aggs"]["count_of_uuid"]["terms"]["size"] = 1000
    query["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
    buckets = client.search(index=issue_index, body=query)['aggregations']["count_of_uuid"]['buckets']
    total_issue_count = sum([bucket["doc_count"] for bucket in buckets])
    if total_issue_count == 0:
        return {"issue_comment_distribution": None}
    commet_distribution = {}
    for bucket in buckets:
        commet_distribution[bucket["key"]] = {"count": bucket["doc_count"], "ratio": bucket["doc_count"] / total_issue_count}
    result = {
        "issue_comment_distribution": commet_distribution
    }
    return result
    