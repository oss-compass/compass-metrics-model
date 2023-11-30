from urllib.parse import urlparse
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch import helpers as elasticsearch_helpers
from opensearchpy import OpenSearch
from opensearchpy import helpers as opensearchpy_helpers


def get_client(url):
    """ Get default client by url """
    return get_elasticsearch_client(url)

def get_helpers():
    """ Collection of simple helper functions that abstract some specifics of the raw API """
    return elasticsearch_helpers


def get_elasticsearch_client(elastic_url):
    """ Get elasticsearch client by url """
    is_https = urlparse(elastic_url).scheme == 'https'
    client = Elasticsearch(
        elastic_url, 
        use_ssl=is_https, 
        verify_certs=False, 
        connection_class=RequestsHttpConnection,
        timeout=100, 
        max_retries=10, 
        retry_on_timeout=True
    )
    return client


def get_opensearch_client(url):
    """ Get opensearch client by url """
    parsed_url = urlparse(url)
    client = OpenSearch(
        hosts=[{'host': parsed_url.hostname, 'port': parsed_url.port}],
        http_compress=True,
        http_auth=(parsed_url.username, parsed_url.password),
        use_ssl= parsed_url.scheme == 'https',
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False
    )
    return client

def get_all_index_data(client, index, body):
    """ Get all index data """
    result_list = []
    page_size = body["size"]
    scroll_id_list = set()
    taskList = client.search(index=index, body=body, scroll="1m", size=page_size)
    scrollTotalSize = taskList["hits"]["total"]['value']
    scroll_id = taskList["_scroll_id"]
    for i in range(0, int(scrollTotalSize/page_size) + 1):
        if i == 0:
            taskHits = taskList["hits"]["hits"]
        else:
            scrollRes = client.scroll(scroll_id=scroll_id, scroll='1m')
            scroll_id = scrollRes["_scroll_id"]
            taskHits = scrollRes['hits']['hits']
        scroll_id_list.add(scroll_id)
        result_list = result_list + taskHits
    if len(scroll_id_list) > 0:
        client.clear_scroll(scroll_id=','.join(scroll_id_list))
    return result_list