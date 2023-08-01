from compass_common.datetime import datetime_utcnow, str_to_datetime


def get_updated_since_query(repo_list, date_field="grimoire_creation_date", order="desc", to_date=datetime_utcnow()):
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
