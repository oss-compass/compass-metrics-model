""" Functions to handle some database statements """

from compass_common.datetime import datetime_utcnow, str_to_datetime


def get_updated_since_query(repo_list, date_field="grimoire_creation_date", order="desc", to_date=datetime_utcnow()):
    """ Query statement to get the code commit data of the repository """
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "tag": [repo + ".git" for repo in repo_list]
                        }
                    }
                ],
                "filter": {
                    "range": {
                        date_field: {
                            "lt": to_date.strftime("%Y-%m-%d")
                        }
                    }
                }
            }
        },
        "sort": [
            {
                date_field: {"order": order}
            }
        ]
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


def get_contributor_query(repo, date_field, from_date, to_date, page_size=100, search_after=[]):
    """ Query statement to get the contributors who have contributed in the from_date,to_date time period. """
    query = {
        "size": page_size,
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            "repo_name.keyword": repo
                        }
                    }
                ],
                "filter": [
                    {
                        "range": {
                            date_field: {
                                "gte": from_date.strftime("%Y-%m-%d"),
                                "lte": to_date.strftime("%Y-%m-%d")
                            }
                        }
                    }
                ]
            }
        },
        "sort": [
            {
                "_id": {
                    "order": "asc"
                }
            }
        ]
    }
    if len(search_after) > 0:
        query['search_after'] = search_after
    return query


def get_uuid_count_query(option, repo_list, field, date_field="grimoire_creation_date", size=0,
                         from_date=str_to_datetime("1970-01-01"), to_date=datetime_utcnow()):
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
                        "bool": {
                            "should": [
                                {
                                    "simple_query_string": {
                                        "query": i + "*",
                                        "fields": ["tag"]
                                    }
                                } for i in repo_list
                            ],
                            "minimum_should_match": 1,
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
                "must": [{
                    "bool": {
                        "should": [{
                            "simple_query_string": {
                                "query": i,
                                "fields": ["tag"]
                            }}for i in repos_list],
                        "minimum_should_match": 1
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
                        "bool": {
                            "should": [{
                                "simple_query_string": {
                                    "query": i,
                                    "fields": ["tag"]
                                }}for i in repos_list],
                            "minimum_should_match": 1
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
                        "bool": {
                            "should": [
                                {
                                    "simple_query_string": {
                                        "query": repo,
                                        "fields": [
                                            "tag"
                                        ]
                                    }
                                }
                            ],
                            "minimum_should_match": 1
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
                         from_date=str_to_datetime("1970-01-01"), to_date=datetime_utcnow(), search_after=[]):
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
        },
        "sort": [
            {
                "_id": {
                    "order": "asc"
                }
            }
        ]
    }
    if len(search_after) > 0:
        query['search_after'] = search_after
    return query