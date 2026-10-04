from unittest.mock import Mock, call

from compass_common.opensearch_utils import get_all_index_data


def test_search_uses_each_new_scroll_id_and_releases_the_last_one():
    client = Mock()
    client.search.return_value = {
        '_scroll_id': 'first', 'hits': {'total': {'value': 2}, 'hits': [{'_source': {'id': 1}}]},
    }
    client.scroll.side_effect = [
        {'_scroll_id': 'second', 'hits': {'hits': [{'_source': {'id': 2}}]}},
        {'_scroll_id': 'third', 'hits': {'hits': []}},
    ]

    result = get_all_index_data(client, 'index', {'size': 1})

    assert [row['_source']['id'] for row in result] == [1, 2]
    assert client.scroll.call_args_list == [
        call(scroll_id='first', scroll='5m'), call(scroll_id='second', scroll='5m')
    ]
    client.clear_scroll.assert_called_once_with(scroll_id='third')
