""" Set of repo related metrics """

from compass_metrics.db_dsl import get_recent_releases_uuid_count, get_contributor_query
from datetime import timedelta


def recent_releases_count(client, release_index, date, repo_list):
    """ Determine the number of releases in the last year. """
    query_recent_releases_count = get_recent_releases_uuid_count(
        repo_list, from_date=(date-timedelta(days=365)), to_date=date)
    releases_count = client.search(index=release_index, body=query_recent_releases_count)[
        'aggregations']["count_of_uuid"]['value']
    return {"recent_releases_count": releases_count}


def get_activity_repo_list(client, contributors_index, date, repos_list, from_date=None, date_field_list=None):
    if from_date is None:
        from_date = date - timedelta(days=180)
    if date_field_list is None:
        date_field_list = ["code_author_date_list", "issue_creation_date_list", "issue_comments_date_list", 
                            "pr_creation_date_list", "pr_comments_date_list"]
    query = get_contributor_query(repos_list, date_field_list, from_date, date, 0)
    query["aggs"] = {
        "repo_count": {
            "terms": {
                "field": "repo_name.keyword",
                "size": 10000
            }
        }
    }
    buckets = client.search(index=contributors_index, body=query)["aggregations"]["repo_count"]["buckets"]
    repo_list = [item["key"] for item in buckets]
    return repo_list