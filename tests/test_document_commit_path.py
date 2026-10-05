"""Exercise the document-cache path passed to commit-time lookup."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


class DocumentCommitPathTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        utils = types.ModuleType('compass_metrics.document_metric.utils')
        for name in ['GITHUB_TOKEN', 'GITEE_TOKEN']:
            setattr(utils, name, 'test-' + name)
        utils.TMP_PATH = utils.JSON_REPOPATH = directory.name
        for name in ['load_json', 'check_github_gitee', 'clone_repo', 'save_json']:
            setattr(utils, name, Mock())
        modules = {utils.__name__: utils, 'requests': types.SimpleNamespace(get=Mock()),
                   'git': types.SimpleNamespace(Repo=Mock())}
        path = Path(__file__).resolve().parents[1] / 'compass_metrics/document_metric/doc_chinese_support.py'
        spec = importlib.util.spec_from_file_location('document_commit_path_under_test', path)
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, modules):
            spec.loader.exec_module(self.module)
        self.module.requests.get.return_value = types.SimpleNamespace(
            status_code=200, json=lambda: [{'commit': {'committer': {'date': '2025-01-02T00:00:00Z'}}}])

    def test_versioned_checkout_path_preserves_repo_name_in_document(self):
        result = self.module.get_file_commit_time(
            'https://github.com/org/demo', 'demo-v1.2/docs/demo guide & notes.md', platform='github')
        self.assertEqual(result, '2025-01-02T00:00:00Z')
        self.module.requests.get.assert_called_once_with(
            'https://api.github.com/repos/org/demo/commits', headers=self.module.GITHUB_HEADERS,
            params={'path': 'docs/demo guide & notes.md'})

    def test_default_platform_uses_github_headers(self):
        self.module.get_file_commit_time('https://github.com/org/demo', 'demo-v1/README.md')
        self.assertEqual(self.module.requests.get.call_args.kwargs['headers'], self.module.GITHUB_HEADERS)
        self.assertEqual(self.module.requests.get.call_args.kwargs['params'], {'path': 'README.md'})

    def test_gitee_uses_its_own_commit_endpoint(self):
        self.module.get_file_commit_time('https://gitee.com/org/demo', 'demo-v1/docs/中文.md', platform='gitee')
        self.module.requests.get.assert_called_once_with(
            'https://gitee.com/api/v5/repos/org/demo/commits', headers=self.module.GITEE_HEADERS,
            params={'path': 'docs/中文.md'})

    def test_no_commits_returns_none(self):
        self.module.requests.get.return_value.json = lambda: []
        self.assertIsNone(self.module.get_file_commit_time('https://github.com/org/demo', 'demo-v1/README.md'))

    def test_failed_request_returns_none(self):
        self.module.requests.get.return_value.status_code = 404
        self.assertIsNone(self.module.get_file_commit_time('https://github.com/org/demo', 'demo-v1/README.md'))

    def test_root_document_without_checkout_prefix_is_preserved(self):
        self.module.get_file_commit_time('https://github.com/org/demo', 'README.md')
        self.assertEqual(self.module.requests.get.call_args.kwargs['params'], {'path': 'README.md'})

    def test_find_zh_files_passes_cache_document_path_to_lookup(self):
        document = Path(self.module.REPOPATH, 'demo-v1', 'docs', 'demo.md')
        document.parent.mkdir(parents=True)
        document.write_text('中文文档测试')
        self.module.load_json.return_value = {'folder_document_details': [
            {'name': 'demo.md', 'path': 'demo-v1/docs/demo.md'}]}
        self.module.check_github_gitee.return_value = 'github'
        result = self.module.find_zh_files('cache.json', 'https://github.com/org/demo')
        self.assertEqual(result['zh_files_number'], 1)
        self.assertEqual(result['zh_files_details'][0]['commit_time'], '2025-01-02T00:00:00Z')
        self.assertEqual(self.module.requests.get.call_args.kwargs['params'], {'path': 'docs/demo.md'})


if __name__ == '__main__':
    unittest.main()
