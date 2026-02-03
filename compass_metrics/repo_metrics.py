""" Set of repo related metrics """

from compass_metrics.db_dsl import get_recent_releases_uuid_count, get_contributor_query
from datetime import timedelta
from compass_common.dict_utils import deep_get


def recent_releases_count(client, release_index, date, repo_list):
    """ Determine the number of releases in the last year. """
    query_recent_releases_count = get_recent_releases_uuid_count(
        repo_list, from_date=(date-timedelta(days=365)), to_date=date)
    releases_count = client.search(index=release_index, body=query_recent_releases_count)[
        'aggregations']["count_of_uuid"]['value']
    return {"recent_releases_count": releases_count}


def branch_protection(client, repo_index, repo_list):
    """ Does the project use Branch Protection ? """
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            "tag": repo_list[0]
                        }
                    }
                ]
            }
        },
        "sort": [
            {
                "metadata__updated_on": {
                    "order": "desc"
                }
            }
        ],
        "size": 1
    }
    hits = client.search(index=repo_index, body=query)["hits"]["hits"]
    main_branch = {}
    release_branch = []
    if len(hits) > 0:
        branches = deep_get(hits[0], ["_source", "branches"], [])
        releases = deep_get(hits[0], ["_source", "releases"], [])
        release_name_list = [release["tag_name"].replace("v", "") for release in releases] 
        
        for branch in branches:
            if branch["name"] in ["master", "main"]:
                main_branch = {
                    "name": branch["name"],
                    "protected":  branch["protected"]
                }
            if any(name in branch["name"] for name in release_name_list):
                release_branch.append({
                    "name": branch["name"],
                    "protected": branch["protected"]
                })
    score = 0
    main_protected = main_branch.get("protected", False) if main_branch else False

    release_protected = all(item.get("protected", False) for item in release_branch) if release_branch else False

    if not main_branch and not release_branch:
        score = None  
    
    if main_branch and not release_branch:
        if main_protected:
            score = 10 
        else:
            score = 0
    if main_branch and release_branch:
        if main_protected and release_protected:
            score = 10  
        elif main_protected or release_protected:
            score = 5   
        else:
            score = 0  
    
    result_data = {
        "branch_protection": score,
        "branch_protection_detail": {
            "main_branch": main_branch,
            "release_branch": release_branch
        }
    }
    return result_data



def get_activity_repo_list(client, contributors_index, date, repos_list, from_date=None, date_field_list=None):
    if from_date is None:
        from_date = date - timedelta(days=180)
    if date_field_list is None:
        date_field_list = ["code_author_date_list", "issue_creation_date_list", "issue_comments_date_list", 
                            "pr_creation_date_list", "pr_comments_date_list"]
    query = get_contributor_query(repos_list, date_field_list, from_date, date, 0)
    query["aggs"] = {
        "repo_count": {
            "terms": {
                "field": "repo_name.keyword",
                "size": 10000
            }
        }
    }
    buckets = client.search(index=contributors_index, body=query)["aggregations"]["repo_count"]["buckets"]
    repo_list = [item["key"] for item in buckets]
    return repo_list