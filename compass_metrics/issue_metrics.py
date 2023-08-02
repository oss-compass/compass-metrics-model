""" Set of issue related metrics """

from compass_metrics.db_dsl import get_uuid_count_query
from compass_common.datetime import get_time_diff_months
from datetime import timedelta


def comment_frequency(client, issue_index, date, repo_list):
    """ Determine the average number of comments per issue created in the last 90 days. """
    query_issue_comments_count = get_uuid_count_query(
        "sum", repo_list, "num_of_comments_without_bot", date_field='grimoire_creation_date', size=0,
        from_date=(date - timedelta(days=90)), to_date=date)
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


def updated_issues_count(client, issue_index, date, repo_list):
    """ Determine the number of issues updated in the last 90 days. """
    query_issue_updated_since = get_uuid_count_query("cardinality", repo_list, "uuid",
                                                     date_field='metadata__updated_on', size=0,
                                                     from_date=(date-timedelta(days=90)), to_date=date)
    query_issue_updated_since["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false" }})
    issues_count = client.search(index=issue_index, body=query_issue_updated_since)[
        'aggregations']["count_of_uuid"]['value']
    result = {
        'updated_issues_count': issues_count
    }
    return result





