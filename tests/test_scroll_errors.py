from unittest.mock import Mock

import pytest

from compass_common.opensearch_utils import get_items


def test_search_errors_other_than_scroll_limits_are_raised():
    client = Mock()
    client.search.side_effect = RuntimeError("connection lost")

    with pytest.raises(RuntimeError, match="connection lost"):
        get_items(client, "index", {"size": 10}, 10)


def test_scroll_limit_is_reported_for_retry():
    class ScrollLimitError(Exception):
        info = {
            "status": 500,
            "error": {"root_cause": [{"reason": "Trying to create too many scroll contexts"}]},
        }

    client = Mock()
    client.search.side_effect = ScrollLimitError()

    assert get_items(client, "index", {"size": 10}, 10) == {"too_many_scrolls": True}
