# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline regression tests for pagination failure and scroll ownership."""
import importlib.util
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import Mock, call, patch


# Load the real helper code without requiring installed search clients. These
# import-only stubs are scoped to this load and never replace pagination logic.
stubs = {}
for name, attrs in {
    'elasticsearch': ['Elasticsearch', 'RequestsHttpConnection', 'helpers'],
    'opensearchpy': ['OpenSearch', 'helpers'],
    'urllib3': ['disable_warnings'],
}.items():
    module = ModuleType(name)
    for attr in attrs:
        setattr(module, attr, Mock())
    stubs[name] = module
spec = importlib.util.spec_from_file_location(
    'pagination_under_test',
    Path(__file__).resolve().parents[1] / 'compass_common' / 'opensearch_utils.py',
)
utils = importlib.util.module_from_spec(spec)
with patch.dict(sys.modules, stubs):
    spec.loader.exec_module(utils)


class QueryError(Exception):
    def __init__(self, info=None):
        super().__init__('query failed')
        self.info = info


def failure(reason='query failed'):
    return QueryError({'status': 500, 'error': {'root_cause': [{'reason': reason}]}})


def page(scroll_id='first', hits=None, total=2):
    return {'_scroll_id': scroll_id,
            'hits': {'total': {'value': total}, 'hits': [] if hits is None else hits}}


class PaginationTests(unittest.TestCase):
    def consume(self, client, generator):
        helper = utils.get_generator if generator else utils.get_all_index_data
        return list(helper(client, 'index', {'size': 1}))

    def test_initial_failure_preserves_exception(self):
        for generator in (False, True):
            for error in (failure(), ValueError('no info'), QueryError('bad response'),
                          QueryError({'error': 'unavailable'}),
                          QueryError({'error': {'root_cause': [None]}})):
                with self.subTest(generator=generator, error=repr(error.info) if hasattr(error, 'info') else str(error)):
                    client = Mock()
                    client.search.side_effect = error
                    with self.assertRaises(type(error)) as raised:
                        self.consume(client, generator)
                    self.assertIs(raised.exception, error)
                    client.search.assert_called_once()
                    client.clear_scroll.assert_not_called()

    def test_later_failure_never_completes_successfully(self):
        for generator in (False, True):
            for cleanup_fails in (False, True):
                with self.subTest(generator=generator, cleanup_fails=cleanup_fails):
                    client = Mock()
                    client.search.return_value = page(hits=[{'_id': 'one'}])
                    error = failure()
                    client.scroll.side_effect = error
                    if cleanup_fails:
                        client.clear_scroll.side_effect = RuntimeError('cleanup failed')
                    with self.assertRaises(QueryError) as raised:
                        self.consume(client, generator)
                    self.assertIs(raised.exception, error)
                    client.clear_scroll.assert_called_once_with(scroll_id='first')

    def test_empty_results_release_scroll(self):
        for generator in (False, True):
            for total in (0, {'value': 0}):
                client = Mock()
                client.search.return_value = page(total=0)
                client.search.return_value['hits']['total'] = total
                self.assertEqual(self.consume(client, generator), [])
                client.scroll.assert_not_called()
                client.clear_scroll.assert_called_once_with(scroll_id='first')

    def test_success_uses_latest_scroll_id(self):
        for generator in (False, True):
            client = Mock()
            client.search.return_value = page(hits=[{'_id': 'one'}])
            client.scroll.side_effect = [page('second', [{'_id': 'two'}]), page('last')]
            self.assertEqual(self.consume(client, generator), [{'_id': 'one'}, {'_id': 'two'}])
            self.assertEqual(client.scroll.call_args_list,
                             [call(scroll_id='first', scroll='5m'), call(scroll_id='second', scroll='5m')])
            client.clear_scroll.assert_called_once_with(scroll_id='last')

    def test_retry_exhaustion_and_cleanup(self):
        for generator in (False, True):
            for initial in (False, True):
                with self.subTest(generator=generator, initial=initial):
                    client = Mock()
                    error = failure('Trying to create too many scroll contexts')
                    operation = client.search if initial else client.scroll
                    operation.side_effect = error
                    if not initial:
                        client.search.return_value = page(hits=[{'_id': 'one'}])
                    with patch.object(utils.time, 'sleep') as sleep:
                        with self.assertRaisesRegex(RuntimeError, 'Scroll context limit retries exhausted') as raised:
                            self.consume(client, generator)
                    self.assertIs(raised.exception.__cause__, error)
                    self.assertEqual(operation.call_count, 901)
                    self.assertEqual(sleep.call_count, 900)
                    if initial:
                        client.clear_scroll.assert_not_called()
                    else:
                        client.clear_scroll.assert_called_once_with(scroll_id='first')

    def test_retry_recovery_and_nonretryable_failure(self):
        for generator in (False, True):
            for recover in (False, True):
                client = Mock()
                error = failure()
                client.search.side_effect = [failure('Trying to create too many scroll contexts'),
                                             page(total=0) if recover else error]
                with patch.object(utils.time, 'sleep') as sleep:
                    if recover:
                        self.assertEqual(self.consume(client, generator), [])
                        client.clear_scroll.assert_called_once_with(scroll_id='first')
                    else:
                        with self.assertRaises(QueryError) as raised:
                            self.consume(client, generator)
                        self.assertIs(raised.exception, error)
                        client.clear_scroll.assert_not_called()
                sleep.assert_called_once_with(1)
                self.assertEqual(client.search.call_count, 2)

    def test_generator_close_releases_context_once(self):
        client = Mock()
        client.search.return_value = page(hits=[{'_id': 'one'}, {'_id': 'two'}])
        items = utils.get_generator(client, 'index', {'size': 2})
        self.assertEqual(next(items), {'_id': 'one'})
        items.close()
        items.close()
        client.clear_scroll.assert_called_once_with(scroll_id='first')
        client.scroll.assert_not_called()

    def test_malformed_page_releases_latest_context(self):
        for generator in (False, True):
            client = Mock()
            client.search.return_value = page(hits=[{'_id': 'one'}])
            client.scroll.return_value = {'_scroll_id': 'second'}
            with self.assertRaises(KeyError):
                self.consume(client, generator)
            client.clear_scroll.assert_called_once_with(scroll_id='second')

    def test_cleanup_failure_does_not_fail_successful_query(self):
        client = Mock()
        client.search.return_value = page(total=0)
        client.clear_scroll.side_effect = RuntimeError('cleanup failed')
        self.assertEqual(self.consume(client, False), [])
        utils.free_scroll(client, None)
        client.clear_scroll.assert_called_once_with(scroll_id='first')


if __name__ == '__main__':
    unittest.main()
