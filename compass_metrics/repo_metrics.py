from compass_metrics.db_dsl import get_recent_releases_uuid_count
from datetime import timedelta

def recent_releases_count(client, release_index, date, repo_list):
    """ Determine the number of releases in the last year. """
    query_recent_releases_count = get_recent_releases_uuid_count(
        repo_list, from_date=(date-timedelta(days=365)), to_date=date)
    releases_count = client.search(index=release_index, body=query_recent_releases_count)[
        'aggregations']["count_of_uuid"]['value']
    return {"recent_releases_count": releases_count}

