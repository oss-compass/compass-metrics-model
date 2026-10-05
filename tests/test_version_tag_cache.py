"""Tag-backed version windows must survive a JSON cache round trip."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


class VersionTagCacheTests(unittest.TestCase):
    def load_module(self, directory):
        modules = {}
        for name, attributes in {
            'compass_metrics.contributor_metrics': ['contributor_count', 'org_contributor_count'],
            'compass_common.opensearch_utils': ['get_client'],
            'opensearchpy': ['OpenSearch'],
            'requests': ['get'],
            'compass_metrics.document_metric.utils': ['get_github_token', 'get_gitee_token'],
        }.items():
            module = types.ModuleType(name)
            for attribute in attributes:
                setattr(module, attribute, Mock())
            modules[name] = module
        utils = modules['compass_metrics.document_metric.utils']
        utils.JSON_REPOPATH = directory
        utils.save_json = lambda data, path: Path(path).write_text(json.dumps(data))
        utils.load_json = lambda path: json.loads(Path(path).read_text())
        path = Path(__file__).resolve().parents[1] / 'compass_metrics/document_metric/organizational_contribution.py'
        spec = importlib.util.spec_from_file_location('version_tag_cache_under_test', path)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, modules):
            spec.loader.exec_module(module)
        return module

    def check_cache(self, platform, releases):
        with tempfile.TemporaryDirectory() as directory:
            module = self.load_module(directory)
            repo = f'https://{platform}.com/org/demo'
            dates = ['2023-01-01T00:00:00Z', '2023-02-01T00:00:00Z', '2023-03-01T00:00:00Z']

            def get(url, **kwargs):
                if url.endswith('/releases'):
                    data = releases
                elif url.endswith('/tags'):
                    data = [{'name': f'v{i + 1}', 'commit': {'url': f'{repo}/commits/{i}'}} for i in range(3)]
                else:
                    data = {'commit': {'committer': {'date': dates[int(url.rsplit('/', 1)[1])]}}}
                return types.SimpleNamespace(status_code=200, links={}, json=lambda: data)

            module.requests.get.side_effect = get
            lookup = getattr(module, f'get_{platform}_versions')
            expected = (dates[0], dates[1])
            self.assertEqual(lookup(repo, 'v2'), expected)
            self.assertTrue(Path(directory, 'demo-v2-tags.json').is_file())
            module.requests.get.reset_mock()
            self.assertEqual(lookup(repo, 'v2'), expected)
            self.assertFalse(any('/commits/' in call.args[0] for call in module.requests.get.call_args_list))

    def test_github_empty_releases_cache_round_trip(self):
        self.check_cache('github', [])

    def test_gitee_empty_releases_cache_round_trip(self):
        self.check_cache('gitee', [])

    def test_github_unrelated_release_cache_does_not_hide_tag_window(self):
        self.check_cache('github', [{'published_at': '2024-01-01T00:00:00Z', 'tag_name': 'other'}])

    def test_gitee_unrelated_release_cache_does_not_hide_tag_window(self):
        self.check_cache('gitee', [{'published_at': '2024-01-01T00:00:00Z', 'tag_name': 'other'}])


if __name__ == '__main__':
    unittest.main()
