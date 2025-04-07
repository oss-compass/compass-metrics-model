'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2025-03-04 18:01:38
LastEditors: zyx
LastEditTime: 2025-03-24 10:31:19
'''
from datetime import timedelta
import datetime
from compass_metrics.contributor_metrics import contributor_count,org_contributor_count
from compass_common.opensearch_utils import get_client
from opensearchpy import OpenSearch
import requests
from compass_metrics.document_metric.utils import get_gitee_token,get_github_token


def get_github_versions(repo_url,version):
    api_url = repo_url.replace("github.com", "api.github.com/repos") + "/releases"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {get_github_token()}'
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        releases = response.json()
        versions = [(release["tag_name"], release["published_at"]) for release in releases]
        versions.sort(key=lambda x: x[1])
        strart_time = None
        end_time = None

        for i in range(len(versions)):
            if versions[i][0] == version:
                start_time = versions[i][1]
                if i+1 < len(versions):
                    end_time = versions[i+1][1]
                else:
                    end_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                break

        return start_time,end_time
    else:
        return None

def get_gitee_versions(repo_url,version):
    api_url = repo_url.replace("gitee.com", "gitee.com/api/v5/repos") + "releases"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'token {get_gitee_token()}'
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        releases = response.json()
        versions = [(release["tag_name"], release["published_at"]) for release in releases]
        versions.sort(key=lambda x: x[1])

        for i in range(len(versions)):
            if versions[i][0] == version:
                start_time = versions[i][1]
                if i+1 < len(versions):
                    end_time = versions[i+1][1]
                else:
                    end_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                break

        return start_time,end_time
    else:
        return None
    

def organizational_contribution(client,repo_name,verision):
    # CLIENT = ""
    # client = OpenSearch(client)

    start_time, end_time = get_github_versions(repo_name,verision)


        
    query = {
        "size": 10000,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "repo_name": repo_name
                        }
                    },
                    {
                        "range": {
                            "grimoire_creation_date": {
                                "gte": start_time,  # 开始时间
                                "lte": end_time  # 结束时间
                            }
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
    
    return {"org_contribution":organization,"personal": persion, "organization": organization}

    
# def Organizational_contribution(opensearch, date, repo_list):
# # object: 
# # {
# # 'organization': int, 
# # 'personal': int
# # }
#     client = get_client(CLIENT)
#     organization = org_contributor_count(client=client, contributors_index="github-contributors_org_repo", date=date, repo_list = repo_list)["org_contributor_count"]
#     contributor = contributor_count(client=client, contributors_index="github-contributors_org_repo", date=date, repo_list = repo_list)["contributor_count"]
#     personal = contributor - organization
#     return {"org_contribution":organization,"organization": organization, "personal": personal}

if __name__ == '__main__':
    repo_name = "https://github.com/mathjax/MathJax"
    get_github_versions("https://github.com/kotest/kotest","v5.9.0")
    # print(Organizational_contribution(CLIENT, DATE,["https://github.com/mathjax/MathJax"]))

    # # repo_name = repo_list[0]
    # print(get_ecological_types(repo_name))
    # with open("组织贡献者.json", "w") as f:
    #     json.dump(get_ecological_types(repo_name), f,indent=4)