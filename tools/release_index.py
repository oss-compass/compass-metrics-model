from opensearchpy import OpenSearch
from opensearchpy import helpers
from perceval.backend import uuid
import json


def get_opensearch_client(opensearch_conn_infos):
    client = OpenSearch(
        hosts=[{"host": opensearch_conn_infos["HOST"],
                "port": opensearch_conn_infos["PORT"]}],
        http_compress=True,
        http_auth=(opensearch_conn_infos["USER"],
                   opensearch_conn_infos["PASSWD"]),
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False
    )
    return client


def opensearch_search(opensearch_client, index, query):
    results = opensearch_client.search(index=index,body=query)

    return results


def newest_message(repo_url):
    query = {"query": {
                    "match": {
                        "tag": repo_url
                    }},
                    "sort": 
                    [{
                        "metadata__updated_on": {"order": "desc"}
                    }]
            }
    return query


def add_release_message(opensearch_client, out_index, repo_url, releases,):
    all_bulk_data = []
    for item in releases:
        release_data = {"_index": out_index,
                        "_id": uuid(str(item["id"])),
                        "_source": {
                            "uuid": uuid(str(item["id"])),
                            "id": item["id"],
                            "tag": repo_url,
                            "tag_name": item["tag_name"],
                            "target_commitish": item["target_commitish"],
                            "prerelease": item["prerelease"],
                            "name": item["name"],
                            "body": item["body"],
                            "author_login": item["author"]["login"],
                            "author_name": item["author"]["name"],
                            "grimoire_creation_date": item["created_at"]}}
        all_bulk_data.append(release_data)
        if len(all_bulk_data) > 10:
            helpers.bulk(client=opensearch_client, actions=all_bulk_data)
            all_bulk_data = []
    helpers.bulk(client=opensearch_client, actions=all_bulk_data)
    all_bulk_data = []


if __name__ == "__main__":
    repo_url = "https://gitee.com/mindspore/mindspore"
    opensearch_conn_infos = json.load(open("opensearch_message.json"))
    opensearch_client = get_opensearch_client(opensearch_conn_infos)
    query = newest_message(opensearch_client, repo_url)
    items = opensearch_search(opensearch_client, "gitee_repo-enriched",query)["hits"]["hits"][0]["_source"]["releases"]
    add_release_message("repo_release_enriched", repo_url, items)
