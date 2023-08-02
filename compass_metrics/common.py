""" Stores common functions, which are called by other metrics function. """

from compass_metrics.db_dsl import get_contributor_query

def get_contributor_list(client, contributors_index, from_date, to_date, repo_list, date_field):
    """ Get the contributors who have contributed in the from_date,to_date time period. """
    result_list = []
    for repo in repo_list:
        search_after = []
        while True:
            query = get_contributor_query(repo, date_field, from_date, to_date, 500, search_after)
            contributor_list = client.search(index=contributors_index, body=query)["hits"]["hits"]
            if len(contributor_list) == 0:
                break
            search_after = contributor_list[len(contributor_list) - 1]["sort"]
            result_list = result_list + [contributor["_source"] for contributor in contributor_list]
    return result_list
