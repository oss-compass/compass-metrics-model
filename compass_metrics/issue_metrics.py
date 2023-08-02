from compass_metrics.db_dsl import get_uuid_count_query
from datetime import timedelta


def issue_first_reponse(client, issue_index, date, repos_list):
    query_issue_first_reponse_avg = get_uuid_count_query(
        "avg", repos_list, "time_to_first_attention_without_bot", "grimoire_creation_date", size=0, from_date=date-timedelta(days=90), to_date=date)
    query_issue_first_reponse_avg["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})

    issue_first_reponse = client.search(index=issue_index, body=query_issue_first_reponse_avg)
    if issue_first_reponse["hits"]["total"]["value"] == 0:
        return None, None
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
