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
    """Return all hits, or raise if any page fails; never return partial data."""
    items = get_generator(client, index, body)
    try:
        return list(items)
    finally:
        items.close()


def get_generator(client, index, body):
    """Yield hits and propagate page failures, even after earlier hits were yielded.

    Consumers must exhaust iteration to establish success, or close the generator
    when stopping early to release its scroll context.
    """
    page_size = body["size"]
    scroll_id = None
    try:
        page = get_items(client, index, body, page_size)
        while True:
            # Scroll IDs can change between pages; use the latest for requests
            # and cleanup, including when processing a response fails.
            scroll_id = page["_scroll_id"]
            hits = page['hits']['hits']
            if not hits:
                return
            for item in hits:
                yield item
            page = get_items(client, index, body, page_size, scroll_id=scroll_id)
    finally:
        free_scroll(client, scroll_id)


def get_items(client, index, body, size, scroll_id=None, scroll="5m"):
    """Fetch a page, retrying only the explicit scroll-context limit error."""
    scroll_wait = 900  # wait for up to 15 minutes
    for attempt in range(scroll_wait + 1):
        try:
            if scroll_id is None:
                return client.search(index=index, body=body, scroll=scroll, size=size)
            return client.scroll(scroll_id=scroll_id, scroll=scroll)
        except Exception as e:
            # Transport errors need not carry structured server error details.
            # Preserve the original failure instead of treating it as no data.
            if not too_many_scrolls(getattr(e, 'info', None)):
                raise
            if attempt == scroll_wait:
                raise RuntimeError("Scroll context limit retries exhausted after {} seconds".format(scroll_wait)) from e
            logger.debug("Too many scrolls open, waiting up to %s seconds", scroll_wait - attempt)
            time.sleep(1)


def too_many_scrolls(res):
    """Check if result conatins 'too many scroll contexts' error"""
    if not isinstance(res, dict) or not isinstance(res.get('error'), dict):
        return False
    causes = res['error'].get('root_cause')
    if not isinstance(causes, list) or not causes or not isinstance(causes[0], dict):
        return False
    reason = causes[0].get('reason')
    return isinstance(reason, str) and 'Trying to create too many scroll contexts' in reason


def free_scroll(client, scroll_id=None):
    """ Free scroll after use"""
    if not scroll_id:
        return
    try:
        client.clear_scroll(scroll_id=scroll_id)
    except Exception as e:
        logger.debug("Error releasing scroll %s: %s", scroll_id, e, exc_info=True)
