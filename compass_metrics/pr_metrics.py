""" Set of pr related metrics """

from compass_metrics.db_dsl import get_uuid_count_query
from compass_common.datetime import get_time_diff_months
from datetime import timedelta


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





