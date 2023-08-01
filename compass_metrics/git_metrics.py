from compass_metrics.db_dsl import get_updated_since_query
from compass_common.datetime import get_time_diff_months


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



