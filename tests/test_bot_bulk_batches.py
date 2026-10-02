from types import SimpleNamespace
from unittest.mock import Mock, patch

from compass_contributor.bot import BotService


def test_bulk_writes_exact_batches_without_empty_request():
    service = object.__new__(BotService)
    service.client = Mock()
    service.bots_index = "bots"
    bulk_helpers = Mock()
    bots = [SimpleNamespace(id=str(n), contributor=str(n)) for n in range(1001)]

    with patch("compass_contributor.bot.helpers", return_value=bulk_helpers):
        service.batch_save(bots)
        service.batch_save([])

    assert [len(call.kwargs["actions"]) for call in bulk_helpers.bulk.call_args_list] == [1000, 1]
