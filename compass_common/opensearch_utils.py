from urllib.parse import urlparse
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch import helpers as elasticsearch_helpers
from opensearchpy import OpenSearch
from opensearchpy import helpers as opensearchpy_helpers
import logging
import time
import urllib3

logger = logging.getLogger(__name__)
urllib3.disable_warnings()

client = None

def get_client(url):
    """ Get default client by url """
    global client
    if client:
        return client
    client = get_elasticsearch_client(url)
    return client

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
    scroll_wait = 900  #wait for 15 minutes
    page_size = body["size"]
    scroll_id = None
    page = get_items(client=client, index=index, body=body, size=page_size, scroll_id=scroll_id)
    if page and 'too_many_scrolls' in page:
        sec = scroll_wait
        while sec > 0:
            logger.debug("Too many scrolls open, waiting up to {} seconds".format(sec))
            time.sleep(1)
            sec -= 1
            page = get_items(client=client, index=index, body=body, size=page_size, scroll_id=scroll_id)
            if not page:
                logger.debug("Waiting for scroll terminated")
                break
            if 'too_many_scrolls' not in page:
                logger.debug("Scroll acquired after {} seconds".format(scroll_wait - sec))
                break

    if not page:
        return result_list
    
    scroll_id = page["_scroll_id"]
    total = page['hits']['total']
    scroll_size = total['value'] if isinstance(total, dict) else total

    if scroll_size == 0:
        free_scroll(client, scroll_id)
        return result_list

    while scroll_size > 0:

        result_list = result_list + page['hits']['hits']
        page = get_items(client=client, index=index, body=body, size=page_size, scroll_id=scroll_id)
        if not page:
            break

        scroll_size = len(page['hits']['hits'])
    free_scroll(client, scroll_id)
    return result_list


def get_generator(client, index, body):
    scroll_wait = 900  #wait for 15 minutes
    page_size = body["size"]
    scroll_id = None
    page = get_items(client=client, index=index, body=body, size=page_size, scroll_id=scroll_id)
    if page and 'too_many_scrolls' in page:
        sec = scroll_wait
        while sec > 0:
            logger.debug("Too many scrolls open, waiting up to {} seconds".format(sec))
            time.sleep(1)
            sec -= 1
            page = get_items(client=client, index=index, body=body, size=page_size, scroll_id=scroll_id)
            if not page:
                logger.debug("Waiting for scroll terminated")
                break
            if 'too_many_scrolls' not in page:
                logger.debug("Scroll acquired after {} seconds".format(scroll_wait - sec))
                break

    if not page:
        return []
    
    scroll_id = page["_scroll_id"]
    total = page['hits']['total']
    scroll_size = total['value'] if isinstance(total, dict) else total

    if scroll_size == 0:
        free_scroll(client, scroll_id)
        return []

    while scroll_size > 0:

        for item in page['hits']['hits']:
            yield item
        page = get_items(client=client, index=index, body=body, size=page_size, scroll_id=scroll_id)
        if not page:
            break

        scroll_size = len(page['hits']['hits'])
    free_scroll(client, scroll_id)

def get_items(client, index, body, size, scroll_id=None, scroll="5m"):
    page = None
    try:
        if scroll_id is None:
            page = client.search(index=index, body=body, scroll=scroll, size=size)
        else:
            page = client.scroll(scroll_id=scroll_id, scroll=scroll)
    except Exception as e:
        if too_many_scrolls(e.info):
            return {'too_many_scrolls': True}
    return page

def too_many_scrolls(res):
    """Check if result conatins 'too many scroll contexts' error"""
    r = res
    return (
        r
        and 'status' in r
        and 'error' in r
        and 'root_cause' in r['error']
        and len(r['error']['root_cause']) > 0
        and 'reason' in r['error']['root_cause'][0]
        and 'Trying to create too many scroll contexts' in r['error']['root_cause'][0]['reason']
    )


def free_scroll(client, scroll_id=None):
    """ Free scroll after use"""
    if not scroll_id:
        return
    try:
        client.clear_scroll(scroll_id=scroll_id)
    except Exception as e:
        logger.debug("Error releasing scroll: {}".scroll_id)