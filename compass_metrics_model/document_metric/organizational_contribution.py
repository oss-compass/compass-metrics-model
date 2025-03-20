'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2025-03-04 18:01:38
LastEditors: zyx
LastEditTime: 2025-03-20 16:35:05
'''
from datetime import timedelta
from itertools import groupby
import pandas as pd
from dateutil.relativedelta import relativedelta
import datetime
import json
from compass_metrics.contributor_metrics import contributor_count,org_contributor_count
from compass_common.opensearch_utils import get_client
from opensearchpy import OpenSearch
CLIENT = ""

DATE = datetime.datetime(2022,12,20)
def organizational_contribution(client,repo_name):
    # CLIENT = ""
    client = OpenSearch(client)
        
    query = {
        "size": 10000,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "repo_name": repo_name
                        }
                    }
                ]
            }
        }
    }
    
    response = client.search(body=query, index="github-contributors_org_repo_enriched")
    hits = response['hits']['hits']
    persion = 0 
    organization = 0 

    for hit in hits:
        for contribution in hit['_source']["contribution_type_list"]:
            if contribution["contribution_type"] == "code_author" and hit['_source']['ecological_type']=="individual participant":
                persion += 1
            if contribution["contribution_type"] == "code_author" and hit['_source']['ecological_type']=="organization participant":
                organization += 1
    
    return {"get_org_contribution":organization,"personal": persion, "organization": organization}

    
def Organizational_contribution(opensearch, date, repo_list):
# object: 
# {
# 'organization': int, 
# 'personal': int
# }
    client = get_client(CLIENT)
    organization = org_contributor_count(client=client, contributors_index="github-contributors_org_repo", date=date, repo_list = repo_list)["org_contributor_count"]
    contributor = contributor_count(client=client, contributors_index="github-contributors_org_repo", date=date, repo_list = repo_list)["contributor_count"]
    personal = contributor - organization
    return {"get_org_contribution":organization,"organization": organization, "personal": personal}

if __name__ == '__main__':
    repo_name = "https://github.com/mathjax/MathJax"
    # print(Organizational_contribution(CLIENT, DATE,["https://github.com/mathjax/MathJax"]))

    # # repo_name = repo_list[0]
    # print(get_ecological_types(repo_name))
    # with open("组织贡献者.json", "w") as f:
    #     json.dump(get_ecological_types(repo_name), f,indent=4)