from unittest.mock import Mock

from compass_common import opensearch_utils


def test_clients_are_cached_by_connection_url(monkeypatch):
    factory = Mock(side_effect=lambda url: object())
    monkeypatch.setattr(opensearch_utils, "clients", {})
    monkeypatch.setattr(opensearch_utils, "get_elasticsearch_client", factory)

    first = opensearch_utils.get_client("https://first.example")
    second = opensearch_utils.get_client("https://second.example")

    assert first is opensearch_utils.get_client("https://first.example")
    assert first is not second
    assert factory.call_count == 2
