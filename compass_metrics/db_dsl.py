""" Functions to handle some database statements """

from compass_common.datetime import datetime_utcnow, str_to_datetime


def get_updated_since_query(repos_list, date_field="grimoire_creation_date", operation="max", to_date=datetime_utcnow()):
    """ Query statement to get the code commit data of the repository """
    query = {
        "size": 0,
        "aggs": {
            "group_by_origin": {
                "terms": {
                    "field": "origin",
                    "size": 10000
                },
                "aggs": {
                    date_field: {
                        operation: {
                            "field": date_field
                        }
                    }
                }
            }
        },
        "query": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "origin": repos_list
                        }
                    }
                ],
                "filter": [
                    {
                        "range": {
                            date_field: {
                                "lt": to_date.strftime("%Y-%m-%d")
                            }
                        }
                    }
                ]
            }
        }
    }
    return query

def get_release_index_mapping():
    """ Defining field mappings for release index """
    mapping = {
        "mappings": {
            "properties": {
                "author_login": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "author_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "body": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "grimoire_creation_date": {
                    "type": "date"
                },
                "id": {
                    "type": "long"
                },
                "name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "prerelease": {
                    "type": "boolean"
                },
                "tag": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "tag_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "target_commitish": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "uuid": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
    return mapping


def get_repo_message_query(repo_url):
    """ Query statement to get the latest message data of the repo """
    query = {
        "query": {
            "match": {
                "tag": repo_url
            }
        },
        "sort": [
            {
                "metadata__updated_on": {"order": "desc"}
            }
        ]
    }
    return query


def get_recent_releases_uuid_count(repo_list, from_date=str_to_datetime("1970-01-01"), to_date=datetime_utcnow()):
    """ Query statement to get the count of releases in a certain time frame """
    query = {
        "size": 0,
        "aggs": {
            "count_of_uuid": {
                "cardinality": {
                    "field": 'uuid.keyword'
                }
            }
        },
        "query": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "tag.keyword": repo_list
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "grimoire_creation_date": {
                            "gte": from_date.strftime("%Y-%m-%d"),
                            "lt": to_date.strftime("%Y-%m-%d")
                        }
                    }
                }
            }
        }
    }
    return query


def get_contributor_query(repo_list, date_field_list, from_date, to_date, page_size=100):
    """ Query statement to get the contributors who have contributed in the from_date,to_date time period. """
    query = {
        "size": page_size,
        "query": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "repo_name.keyword": repo_list
                        }
                    }
                ]
            }
        }
    }
    if len(date_field_list) > 0:
        query["query"]["bool"]["should"] = [{
                "range": {
                    date_field: {
                        "gte": from_date.strftime("%Y-%m-%d"),
                        "lt": to_date.strftime("%Y-%m-%d")
                    }
                }
            } for date_field in date_field_list]
        query["query"]["bool"]["minimum_should_match"] = 1
    return query


def get_uuid_count_query(option, repo_list, field, date_field="grimoire_creation_date", size=0,
                         from_date=str_to_datetime("1970-01-01"), to_date=datetime_utcnow(), repo_field="tag"):
    """ Counting the number of records according to conditions """
    query = {
        "size": size,
        "track_total_hits": "true",
        "aggs": {
            "count_of_uuid": {
                option: {
                    "field": field
                }
            }
        },
        "query": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            repo_field: repo_list
                        }
                    }
                ],
                "filter": [
                    {
                        "range": {
                            date_field: {
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


def get_pr_closed_uuid_count(option, repos_list, field, from_date=str_to_datetime("1970-01-01"), to_date=datetime_utcnow()):
    query = {
        "size": 0,
        "track_total_hits": True,
        "aggs": {
            "count_of_uuid": {
                option: {
                    "field": field
                }
            }
        },
        "query": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "tag": repos_list
                        }
                    },
                    {
                    "match_phrase": {
                        "pull_request": "true"
                    }
                }
                ],
                "must_not": [
                    {"term": {"state": "open"}},
                    {"term": {"state": "progressing"}}
                ],
                "filter": {
                    "range": {
                        "closed_at": {
                            "gte": from_date.strftime("%Y-%m-%d"),
                            "lt": to_date.strftime("%Y-%m-%d")
                        }
                    }
                }
            }
        }
    }

    return query


def get_pr_message_count(repos_list, field, date_field="grimoire_creation_date", size=0, filter_field=None, from_date=str_to_datetime("1970-01-01"), to_date=datetime_utcnow()):
    query = {
        "size": size,
        "track_total_hits": True,
        "aggs": {
            "count_of_uuid": {
                "cardinality": {
                    "field": field
                }
            }
        },
        "query": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "tag": repos_list
                        }
                    },
                    {
                        "match_phrase": {
                            "pull_request": "true"
                        }
                    }
                ],
                "filter": [
                    {
                        "range":
                        {
                            filter_field: {
                                "gte": 1
                            }
                        }},
                    {
                        "range":
                        {
                            date_field: {
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


def get_pr_linked_issue_count(repo, from_date=str_to_datetime("1970-01-01"), to_date=datetime_utcnow()):
    query = {
        "size": 0,
        "track_total_hits": True,
        "aggs": {
            "count_of_uuid": {
                "cardinality": {
                    "script": "if(doc.containsKey('pull_id')) {return doc['pull_id']} else {return doc['id']}"
                }
            }
        },
        "query": {
            "bool": {
                "should": [
                    {
                        "range": {
                            "linked_issues_count": {
                                "gte": 1
                            }
                        }
                    },
                    {
                        "script": {
                            "script": {
                                "source": "if (doc.containsKey('body') && doc['body'].size()>0 &&doc['body'].value.indexOf(params.issue) != -1){return true}",
                                "lang": "painless",
                                "params": {
                                    "issue": repo +'/issue'
                                }
                            }
                        }
                    }
                ],
                "minimum_should_match": 1,
                "must": [
                    {
                        "term": {
                            "tag": repo
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


def get_message_list_query(field="tag", field_values=[], date_field="grimoire_creation_date", size=0,
                         from_date=str_to_datetime("1970-01-01"), to_date=datetime_utcnow()):
    """ Getting a list of message data according to conditions """
    query = {
        "size": size,
        "query": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            field: field_values
                        }
                    }
                ],
                "filter": [
                    {
                        "range": {
                            date_field: {
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


def get_updated_issues_count_query(repo_list, from_date=str_to_datetime("1970-01-01"), to_date=datetime_utcnow()):
    """ Query statement for counting the number of issue updates according to conditions """
    query = {
        "size": 0,
        "track_total_hits": "true",
        "aggs": {
            "count_of_uuid": {
                "cardinality": {
                    "field": "issue_id"
                }
            }
        },
        "query": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "tag": repo_list
                        }
                    },
                    {
                        "bool": {
                            "should": [
                                {
                                    "range": {
                                        "issue_updated_at": {
                                            "gte": from_date.strftime("%Y-%m-%d"),
                                            "lt": to_date.strftime("%Y-%m-%d")
                                        }
                                    }
                                },
                                {
                                    "range": {
                                        "comment_updated_at": {
                                            "gte": from_date.strftime("%Y-%m-%d"),
                                            "lt": to_date.strftime("%Y-%m-%d")
                                        }
                                    }
                                }
                            ],
                            "minimum_should_match": 1
                        }
                    },
                    {
                        "match_phrase": {
                            "issue_pull_request": "false"
                        }
                    }
                ]
            }
        }
    }
    return query


def get_pr_query_by_commit_hash(repo_list, hash_list):
    return {
        "size": 10000,
        "query": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "origin": repo_list
                        }
                    }
                ],
                "should": [
                    {
                        "terms": {
                            "merge_commit_sha": hash_list
                        }
                    },
                    {
                        "terms": {
                            "commits_data": hash_list
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        }
    }


def get_base_index_mapping():
    """ Get Elasticsearch mapping. """
    mapping = {
        "mappings": {
            "properties": {
                "uuid": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "grimoire_creation_date" : {
                    "type" : "date"
                }
            }
        }
    }
    return mapping
def get_license_query(repo_list, page_size, date):
    """ Query statement to get the license information including license_list, osi_license_list, and non_osi_licenses. """
    query = {
        "size": page_size,
        "sort": [
            {
                "grimoire_creation_date": {
                    "order": "desc"
                }
            }
        ],
        "query": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "project_url.keyword": repo_list
                        }
                    },
                    {
                        "exists": {
                            "field": "license.license_list"
                        }
                    },
                    {
                        "range": {
                            "grimoire_creation_date": {
                                "lte": date  # grimoire_creation_date小于或等于指定日期
                            }
                        }
                    }
                ]
            }
        },
        "_source": [
            "license.license_list",
            "license.osi_license_list",
            "license.non_osi_licenses"
        ]
    }

    return query


def get_security_query(repo_list, page_size, date):
    query = {
        "size": page_size,
        "sort": [
            {
                "grimoire_creation_date": {
                    "order": "desc"  # 按时间降序排序
                }
            }
        ],
        "query": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "project_url.keyword": repo_list
                        }
                    },
                    {
                        "exists": {
                            "field": "security"  # 确保security字段存在
                        }
                    },
                    {
                        "range": {
                            "grimoire_creation_date": {
                                "lte": date  # grimoire_creation_date小于或等于指定日期
                            }
                        }
                    }
                ]
            }
        },
        "_source": [
            "security",  # 只返回security相关字段
            "grimoire_creation_date"  # 返回时间字段用于排序
        ]
    }
    return query