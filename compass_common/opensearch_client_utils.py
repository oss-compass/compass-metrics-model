from urllib.parse import urlparse
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch import helpers as elasticsearch_helpers
from opensearchpy import OpenSearch
from opensearchpy import helpers as opensearchpy_helpers


def get_client(url):
    """ Get default client by url """
    return get_opensearch_client(url)

def get_helpers():
    """ Collection of simple helper functions that abstract some specifics of the raw API """
    return opensearchpy_helpers


def get_elasticsearch_client(elastic_url):
    """ Get elasticsearch client by url """
    is_https = urlparse(elastic_url).scheme == 'https'
    return Elasticsearch(elastic_url, use_ssl=is_https, verify_certs=False, connection_class=RequestsHttpConnection)


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