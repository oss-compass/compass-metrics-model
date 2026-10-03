from unittest.mock import Mock

from compass_contributor.bot import BotService


def bot_hit(name):
    return {"_source": {"community": None, "repo": None, "contributor": name}}


def test_bot_lookup_reads_beyond_first_search_page():
    service = object.__new__(BotService)
    service.bots_index = "bots"
    service.client = Mock()
    service.client.search.return_value = {
        "_scroll_id": "first",
        "hits": {"total": {"value": 2}, "hits": [bot_hit("first-bot")]},
    }
    service.client.scroll.side_effect = [
        {"_scroll_id": "second", "hits": {"hits": [bot_hit("second-bot")]}},
        {"_scroll_id": "third", "hits": {"hits": []}},
    ]

    result = service.get_dict_by_source("github")

    assert result["common"] == ["first-bot", "second-bot"]
    assert service.client.scroll.call_count == 2
