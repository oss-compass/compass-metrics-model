""" Set of pr related metrics """

from compass_metrics.db_dsl import get_uuid_count_query
from compass_metrics.db_dsl import get_pr_closed_uuid_count
from datetime import timedelta
from compass_common.datetime import get_time_diff_days
from compass_common.datetime import str_to_datetime
from compass_common.math_utils import get_medium


def pr_open_time(client, pr_index, date, repos_list):
    query_pr_opens = get_uuid_count_query(
        "avg", repos_list, "time_to_first_attention_without_bot", "grimoire_creation_date", size=10000,
        from_date=date-timedelta(days=90), to_date=date)
    query_pr_opens["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true"}})
    pr_opens_items = client.search(index=pr_index, body=query_pr_opens)['hits']['hits']
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
                pr_open_time_repo.append(get_time_diff_days(item['_source']['created_at'], str(date)))

    pr_open_time_repo_avg = float(sum(pr_open_time_repo)/len(pr_open_time_repo)) if len(pr_open_time_repo) > 0 else None
    pr_open_time_repo_mid = get_medium(pr_open_time_repo) if len(pr_open_time_repo) > 0 else None

    result = {
        "pr_open_time_avg": pr_open_time_repo_avg,
        "pr_open_time_mid": pr_open_time_repo_mid
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


def pr_time_to_first_response(client, pr_index, date, repos_list):
    """ Determine the amount of time between when a PR was created and when it received the first response from a human
    in the past 90 days. """
    query_pr_first_response_avg = get_uuid_count_query(
        "avg", repos_list, "time_to_first_attention_without_bot", "grimoire_creation_date", size=0,
        from_date=date - timedelta(days=90), to_date=date)
    query_pr_first_response_avg["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true"}})
    pr_first_response = client.search(index=pr_index, body=query_pr_first_response_avg)
    pr_first_response_avg = pr_first_response['aggregations']["count_of_uuid"]['value']

    query_pr_first_response_mid = get_uuid_count_query(
        "percentiles", repos_list, "time_to_first_attention_without_bot", "grimoire_creation_date", size=0,
        from_date=date - timedelta(days=90), to_date=date)
    query_pr_first_response_mid["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true"}})
    query_pr_first_response_mid["aggs"]["count_of_uuid"]["percentiles"]["percents"] = [
        50]
    pr_first_response_mid = client.search(index=pr_index, body=query_pr_first_response_mid)[
        'aggregations']["count_of_uuid"]['values']['50.0']

    result = {
        'pr_time_to_first_response_avg': round(pr_first_response_avg, 4) if pr_first_response_avg is not None else None,
        'pr_time_to_first_response_mid': round(pr_first_response_mid, 4) if pr_first_response_mid is not None else None,
    }
    return result


def change_request_closure_ratio(client, pr_index, date, repos_list):
    """Measures the ratio between the total number of open change requests and the total number
    of closed change requests from the beginning to now."""
    closure_ratio, closed_count, created_count = change_request_closure(
        client, pr_index, str_to_datetime("1970-01-01"), date, repos_list)
    result = {
        "change_request_closure_ratio": closure_ratio,
        "change_request_closed_count": closed_count,
        "change_request_created_count": created_count
    }
    return result


def change_request_closure_ratio_recently_period(client, pr_index, date, repos_list):
    """Measures the ratio between the total number of open change requests and the total number
    of closed change requests in the last 90 days."""
    closure_ratio, closed_count, created_count = change_request_closure(
        client, pr_index, date - timedelta(days=90), date, repos_list)
    result = {
        "change_request_closure_ratio_recently_period": closure_ratio,
        "change_request_closed_count_recently_period": closed_count,
        "change_request_created_count_recently_period": created_count
    }
    return result



def change_request_closure(client, pr_index, from_date, to_date, repos_list):
    """Measures the ratio between the total number of open change requests and the total number
        of closed change requests in the range from_date and to_date"""
    pr_total_dsl = get_uuid_count_query(
        "cardinality", repos_list, "uuid", size=0, from_date=from_date, to_date=to_date)
    pr_total_dsl["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true"}})
    pr_total_dsl["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
    pr_total_count = client.search(index=pr_index, body=pr_total_dsl)['aggregations']["count_of_uuid"]['value']

    pr_closed_dsl = pr_total_dsl
    pr_closed_dsl["query"]["bool"]["must"][0]["bool"]["filter"].append({
                                    "range": {
                                        "closed_at": {
                                            "gte": from_date.strftime("%Y-%m-%d"),
                                            "lt": to_date.strftime("%Y-%m-%d")
                                        }
                                    }
                                })
    pr_closed_count = client.search(index=pr_index, body=pr_closed_dsl)['aggregations']["count_of_uuid"]['value']
    try:
        return round(pr_closed_count / pr_total_count, 4), pr_closed_count, pr_total_count
    except ZeroDivisionError:
        return None, 0, 0
