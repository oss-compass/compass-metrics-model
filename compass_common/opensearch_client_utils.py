from urllib.parse import urlparse
from elasticsearch import Elasticsearch, RequestsHttpConnection


def get_elasticsearch_client(elastic_url):
    """ Get opensearch client by url """
    is_https = urlparse(elastic_url).scheme == 'https'
    return Elasticsearch(elastic_url, use_ssl=is_https, verify_certs=False, connection_class=RequestsHttpConnection)
