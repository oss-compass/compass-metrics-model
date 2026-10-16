from unittest.mock import Mock, patch

from compass_common.opensearch_utils import free_scroll


def test_clear_scroll_failure_is_logged_without_hiding_the_original_result():
    client = Mock()
    client.clear_scroll.side_effect = RuntimeError("transport closed")

    with patch("compass_common.opensearch_utils.logger.debug") as debug:
        free_scroll(client, "scroll-123")

    debug.assert_called_once()
    assert debug.call_args.args[1:] == ("scroll-123", client.clear_scroll.side_effect)
