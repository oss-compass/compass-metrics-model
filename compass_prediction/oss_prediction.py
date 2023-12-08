from OssPrediction.api import predict
from compass_common.datetime import datetime_utcnow
from datetime import timedelta, datetime

import pandas as pd
import warnings
import logging

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)

def get_model_data(client, index_name, repo, model_name):

    def get_query(repo, model_name, from_date, to_date, size=500):
        query = {
            "size": 0,
            "aggs": {
                "group_by_creation_date": {
                    "terms": {
                        "field": "grimoire_creation_date",
                        "size": size
                    },
                    "aggs": {
                        "top_enriched_on": {
                            "top_hits": {
                                "size": 1,
                                "sort": [
                                    {
                                        "metadata__enriched_on": {
                                            "order": "desc"
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            },
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_phrase": {
                                "level.keyword": "repo"
                            }
                        },
                        {
                            "match_phrase": {
                                "label.keyword": repo
                            }
                        },
                        {
                            "match_phrase": {
                                "model_name.keyword": model_name
                            }
                        }
                    ],
                    "filter": [
                        {
                            "range": {
                                "grimoire_creation_date": {
                                    "gte": from_date.strftime("%Y-%m-%d"),
                                    "lt": to_date.strftime("%Y-%m-%d")
                                }
                            }
                        }
                    ]
                }
            }
        }
        return query

    to_date = datetime_utcnow()
    from_date = to_date - timedelta(days=1095)
    query = get_query(repo, model_name, from_date, to_date)
    buckets = client.search(index=index_name, body=query)['aggregations']['group_by_creation_date']['buckets']
    result_list = [item['top_enriched_on']['hits']['hits'][0]['_source'] for item in buckets]
    return result_list

    
def get_organizations_activity_metrics_model(client, model_index, repo):
    return get_model_data(client, model_index, repo, "Organizations Activity")

def get_collaboration_development_index_metrics_model(client, model_index, repo):
    return get_model_data(client, model_index, repo, "Code_Quality_Guarantee")

def get_community_service_and_support_metrics_model(client, model_index, repo):
    return get_model_data(client, model_index, repo, "Community Support and Service")

def get_activity_metrics_model(client, model_index, repo):
    return get_model_data(client, model_index, repo, "Activity")


def prediction_activity(repo, model_data_list):
    """ Predict open source project activity """
    data_list = []
    for model_data in model_data_list:
        df = pd.json_normalize(model_data)
        data_list.append(df)
    data_list = [data_list]
    repo_name_list = [repo]
    model_list = ['XGBoost', 'AdaBoost', 'RandomForest']
    select = "small"
    ans = predict(data_list=data_list, repo_name_list=repo_name_list,
            model_list=model_list, select=select)
    active_ratio = None  
    if len(ans) > 0:
        active_ratio = list(ans.values())[0]['probability'][0][1]
    return {"active": active_ratio}


def prediction_activity_start(repo, client, activity_index, development_index, community_index, organizations_activity_index):
    logger.info(f"{repo} start prediction")
    start_time = datetime.now()
    model_data_list = []
    model_data_list.append(get_activity_metrics_model(client, activity_index, repo))
    model_data_list.append(get_collaboration_development_index_metrics_model(client, development_index, repo))
    model_data_list.append(get_community_service_and_support_metrics_model(client, community_index, repo))
    model_data_list.append(get_organizations_activity_metrics_model(client, organizations_activity_index, repo))
    prediction_result = prediction_activity(repo, model_data_list)
    logger.info(f"{repo} finish prediction  active: {prediction_result['active']}  time: {str(datetime.now() - start_time)}")
    return prediction_result