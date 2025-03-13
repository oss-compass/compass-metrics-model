from datetime import timedelta
from itertools import groupby
import pandas as pd
from dateutil.relativedelta import relativedelta
import datetime
from compass_metrics.contributor_metrics import contributor_count,org_contributor_count
from compass_common.opensearch_utils import get_client
from opensearchpy import OpenSearch
import json
CLIENT = "http://admin:admin@159.138.38.244:9200"
def get_vul_levels_metrics(repo_name):
    '''get security metrics(security level and vulnerablity published time) for a given repo'''
    client = OpenSearch(CLIENT)

    query = {
        "size": 500,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "project_url": repo_name
                        }
                    }
                ]
            }
        }
    }

    response = client.search(body=query, index="compass_metric_model_opencheck")
    if response['hits']['total']['value'] == 0:
        return ValueError("No security metrics found for this repo")
    
    hits = response['hits']['hits']
    security = [hit['_source']['security'] for hit in hits][0]

    vul_levels = []

    for pkg in security:
        for i in range(len(pkg["vulnerabilities"])):
            vul_level = {
                "package_name": pkg["package_name"],
                "package_version": pkg["package_version"],
                "vulnerabilities": pkg["vulnerabilities"][i]["aliases"],
                "severity" : pkg["vulnerabilities"][i]["severity"]
            }
            vul_levels.append(vul_level)
    return vul_levels

# def get_timeliness_is_high_metrics(repo_name):
#     '''get security metrics(security level and vulnerablity published time) for a given repo'''
#     client = OpenSearch(CLIENT)

#     query = {
#         "size": 500,
#         "query": {
#             "bool": {
#                 "must": [
#                     {
#                         "match": {
#                             "project_url": repo_name
#                         }
#                     }
#                 ]
#             }
#         }
#     }

#     response = client.search(body=query, index="compass_metric_model_opencheck")

#     if response['hits']['total']['value'] == 0:
#         return ValueError("No security metrics found for this repo")
    
#     hits = response['hits']['hits']
#     security = [hit['_source']['security'] for hit in hits][0]


#     vul_timeless = []

#     for pkg in security:
#         for i in range(len(pkg["vulnerabilities"])):
#             vul_time = {
#                 "package_name": pkg["package_name"],
#                 "package_version": pkg["package_version"],
#                 "vulnerabilities": pkg["vulnerabilities"][i]["aliases"],
#                 "isfixed": len(pkg["vulnerabilities"][i]["fixed_version"]) > 0,
#                 "fixed_version" : pkg["vulnerabilities"][i]["fixed_version"],
#                 "published_time" : pkg["vulnerabilities"][i]["published"]
#             }
#             vul_timeless.append(vul_time)
#     return vul_timeless
    

if __name__ == '__main__':
    repo_list = "https://gitee.com/openharmony-sig/rntpc_react-native-map-linking"
    # print(get_security_metrics(repo_list))
    with open("漏洞等级.json", "w") as f:
        json.dump(get_vul_levels_metrics(repo_list), f,indent=4)
    # with open("漏洞修复时间.json", "w") as f:
    #     json.dump(get_timeliness_is_high_metrics(repo_list), f,indent=4)
    # print(get_vul_levels_metrics(repo_list))
    # print(get_timeliness_is_high_metrics(repo_list))