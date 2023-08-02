from compass_metrics.db_dsl import get_uuid_count_query
from datetime import timedelta
from grimoire_elk.enriched.utils import get_time_diff_days
from grimoirelab_toolkit.datetime import (datetime_utcnow,
                                          str_to_datetime)
from compass_common.math_utils import get_medium


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


def bug_issue_open_time(client, issue_index, date, repos_list):
    query_issue_opens = get_uuid_count_query("avg", repos_list, "time_to_first_attention_without_bot",
                                                    "grimoire_creation_date", size=10000, from_date=date-timedelta(days=90), to_date=date)
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
    issue_opens_items = client.search(
        index=issue_index, body=query_issue_opens)['hits']['hits']
    if len(issue_opens_items) == 0:
        return None, None
    issue_open_time_repo = []
    for item in issue_opens_items:
        if 'state' in item['_source']:
            if item['_source']['closed_at'] and item['_source']['state'] in ['closed', 'rejected'] and str_to_datetime(item['_source']['closed_at']) < date:
                issue_open_time_repo.append(get_time_diff_days(
                    item['_source']['created_at'], item['_source']['closed_at']))
            else:
                issue_open_time_repo.append(get_time_diff_days(
                    item['_source']['created_at'], str(date)))
    issue_open_time_repo_avg = sum(issue_open_time_repo)/len(issue_open_time_repo)
    issue_open_time_repo_mid = get_medium(issue_open_time_repo)
    result = {
        "issue_open_time_repo_avg": issue_open_time_repo_avg,
        "issue_open_time_repo_mid": issue_open_time_repo_mid
    }
    return result