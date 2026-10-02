from unittest.mock import Mock

from compass_common.opensearch_utils import get_generator


def test_closing_generator_releases_active_scroll():
    client = Mock()
    client.search.return_value = {
        "_scroll_id": "first", "hits": {"total": {"value": 2}, "hits": [{"id": 1}, {"id": 2}]}
    }
    rows = get_generator(client, "index", {"size": 2})

    assert next(rows) == {"id": 1}
    rows.close()

    client.clear_scroll.assert_called_once_with(scroll_id="first")
    client.scroll.assert_not_called()


def test_completed_generator_releases_latest_scroll_id():
    client = Mock()
    client.search.return_value = {
        "_scroll_id": "first", "hits": {"total": {"value": 1}, "hits": [{"id": 1}]}
    }
    client.scroll.return_value = {"_scroll_id": "second", "hits": {"hits": []}}

    assert list(get_generator(client, "index", {"size": 1})) == [{"id": 1}]
    client.clear_scroll.assert_called_once_with(scroll_id="second")
