from compass_common.opensearch_utils import get_opensearch_client


def test_opensearch_client_uses_url_default_ports():
    https = get_opensearch_client("https://example.org")
    http = get_opensearch_client("http://example.org")
    explicit = get_opensearch_client("https://example.org:9200")

    assert https.transport.connection_pool.get_connection().port == 443
    assert http.transport.connection_pool.get_connection().port == 80
    assert explicit.transport.connection_pool.get_connection().port == 9200


def test_opensearch_client_keeps_explicit_credentials():
    client = get_opensearch_client("https://user:pass@example.org:9200")
    connection = client.transport.connection_pool.get_connection()
    assert connection.port == 9200
    assert "authorization" in connection.headers
