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
from compass_metrics.document_metric.utils import save_json,JSON_REPOPATH,load_json
import os

def get_github_versions(repo_url,version):
    api_url = repo_url.replace("github.com", "api.github.com/repos") + "/releases"
    repo_name_releases = repo_url.split("/")[-1] + "-" + version + "-releases.json"
    repo_name_tags = repo_url.split("/")[-1] + "-"+ version + "-tags.json"

    
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {get_github_token()}'
    }
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        releases = response.json()
        # 如果本地存在版本信息，则直接读取
        if repo_name_releases in os.listdir(JSON_REPOPATH):
            versions = load_json(repo_name_releases)
            
        else:
            versions = {}
            while 'next' in response.links.keys():
                next_url = response.links['next']['url']
                response = requests.get(next_url, headers=headers)
                if response.status_code == 200:
                    releases += response.json()
                else:
                    break

            # 处理每个版本的发布时间和版本号
            for release in releases:
                if release["published_at"] not in versions.keys():
                    versions[release["published_at"]] = [release["tag_name"]]
                else:
                    versions[release["published_at"]].append(release["tag_name"])


            #对版本进行排序
            versions = sorted(versions.items(), key=lambda x: x[0])

            # with open(os.path.join(JSON_REPOPATH, repo_name_releases), "w") as f:
            save_json(versions, os.path.join(JSON_REPOPATH, repo_name_releases))

        #时间初始化
        start_time = datetime.datetime(2020,1,1,0,0,0).strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        flag = False

        for i in range(len(versions)):
            if version in versions[i][1]:
                end_time = versions[i][0]
                start_time = versions[i-1][0]
                flag = True
                break
       

        if len(versions) == 0 or not flag: #针对tags做查询
            api_url = repo_url.replace("github.com", "api.github.com/repos") + "/tags"
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                if repo_name_tags in os.listdir(JSON_REPOPATH):
                    tags = load_json(repo_name_tags)

                else:#没有重新处理
                    tags = response.json()
                    versions = {}
                    #获取所有的版本信息
                    while 'next' in response.links.keys():
                        next_url = response.links['next']['url']
                        response = requests.get(next_url, headers=headers)
                        if response.status_code == 200:
                            tags += response.json()
                        else:
                            break

                    #对每个tag进行处理
                    for tag in tags:#通过二次发送获取commit
                        api_tags_url = tag["commit"]["url"]
                        response = requests.get(api_tags_url, headers=headers)
                        if response.status_code == 200:
                            commit_date = response.json()["commit"]["committer"]["date"]
                        else:
                            continue
                        
                        if commit_date not in versions.keys():
                            versions[commit_date] = [tag["name"]]
                        else:
                            versions[commit_date].append(tag["name"])
                    
                    versions = sorted(versions.items(), key=lambda x: x[0])
                    save_json(versions, os.path.join(JSON_REPOPATH, repo_name_tags))

                start_time = datetime.datetime(2020,1,1,0,0,0).strftime("%Y-%m-%dT%H:%M:%SZ")
                end_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                for i in range(len(versions)):
                    if version in versions[i][1]:
                        end_time = versions[i][0]
                        start_time = versions[i-1][0]
                
                return start_time,end_time
            else:
                raise Exception(f"Failed to get tags. Status code: {response.status_code}")
        return start_time,end_time

def get_gitee_versions(repo_url,version):
    api_url = repo_url.replace("gitee.com", "gitee.com/api/v5/repos") + "/releases"
    repo_name_releases = repo_url.split("/")[-1] + "-" + version + "-releases.json"
    repo_name_tags = repo_url.split("/")[-1] + "-"+ version + "-tags.json"

    
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {get_github_token()}'
    }
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        releases = response.json()
        # 如果本地存在版本信息，则直接读取
        if repo_name_releases in os.listdir(JSON_REPOPATH):
            versions = load_json(repo_name_releases)
            
        else:
            versions = {}
            while 'next' in response.links.keys():
                next_url = response.links['next']['url']
                response = requests.get(next_url, headers=headers)
                if response.status_code == 200:
                    releases += response.json()
                else:
                    break

            # 处理每个版本的发布时间和版本号
            for release in releases:
                if release["published_at"] not in versions.keys():
                    versions[release["published_at"]] = [release["tag_name"]]
                else:
                    versions[release["published_at"]].append(release["tag_name"])


            #对版本进行排序
            versions = sorted(versions.items(), key=lambda x: x[0])

            # with open(os.path.join(JSON_REPOPATH, repo_name_releases), "w") as f:
            save_json(versions, os.path.join(JSON_REPOPATH, repo_name_releases))

        #时间初始化
        start_time = datetime.datetime(2020,1,1,0,0,0).strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        flag = False

        for i in range(len(versions)):
            if version in versions[i][1]:
                end_time = versions[i][0]
                start_time = versions[i-1][0]
                flag = True
                break
       

        if len(versions) == 0 or not flag: #针对tags做查询
            api_url = repo_url.replace("gitee.com", "gitee.com/api/v5/repos") + "/tags"
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                if repo_name_tags in os.listdir(JSON_REPOPATH):
                    tags = load_json(repo_name_tags)

                else:#没有重新处理
                    tags = response.json()
                    versions = {}
                    #获取所有的版本信息
                    while 'next' in response.links.keys():
                        next_url = response.links['next']['url']
                        response = requests.get(next_url, headers=headers)
                        if response.status_code == 200:
                            tags += response.json()
                        else:
                            break

                    #对每个tag进行处理
                    for tag in tags:#通过二次发送获取commit
                        api_tags_url = tag["commit"]["url"]
                        response = requests.get(api_tags_url, headers=headers)
                        if response.status_code == 200:
                            commit_date = response.json()["commit"]["committer"]["date"]
                        else:
                            continue
                        
                        if commit_date not in versions.keys():
                            versions[commit_date] = [tag["name"]]
                        else:
                            versions[commit_date].append(tag["name"])
                    
                    versions = sorted(versions.items(), key=lambda x: x[0])
                    save_json(versions, os.path.join(JSON_REPOPATH, repo_name_tags))

                start_time = datetime.datetime(2020,1,1,0,0,0).strftime("%Y-%m-%dT%H:%M:%SZ")
                end_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                for i in range(len(versions)):
                    if version in versions[i][1]:
                        end_time = versions[i][0]
                        start_time = versions[i-1][0]
                
                return start_time,end_time
            else:
                raise Exception(f"Failed to get tags. Status code: {response.status_code}")
        return start_time,end_time

    

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