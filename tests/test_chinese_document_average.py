"""Exercise the real aggregation with deterministic repository metric results."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch


class ChineseDocumentAverageTests(unittest.TestCase):
    def aggregate(self, counts):
        repos = ['https://github.com/example/repo{}'.format(i) for i in range(len(counts))]
        results = {
            repo: {'zh_files_number': count, 'zh_files_details': [{'name': 'README.zh.md'}]}
            for repo, count in zip(repos, counts)
        }
        modules = {}
        for name, function in [
            ('doc_quarty', 'doc_quarty_all'),
            ('doc_chinese_support', 'doc_chinexe_support_git'),
            ('doc_num', 'get_documentation_links_from_repo'),
            ('organizational_contribution', 'organizational_contribution'),
        ]:
            module = types.ModuleType('compass_metrics.document_metric.' + name)
            setattr(module, function, Mock())
            modules[module.__name__] = module
        chinese = modules['compass_metrics.document_metric.doc_chinese_support'].doc_chinexe_support_git
        chinese.side_effect = lambda repo, version: results[repo]
        path = Path(__file__).resolve().parents[1] / 'compass_metrics/document_metric/__init__.py'
        spec = importlib.util.spec_from_file_location('industry_support_under_test', path)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, modules):
            spec.loader.exec_module(module)
        result = module.Industry_Support(None, repos, 'v1').get_zh_files_number()
        self.assertEqual(result['zh_files_details'], [
            {'repo_url': repo, 'zh_files_details': results[repo]} for repo in repos
        ])
        self.assertIsInstance(result['zh_files_number'], int)
        return result['zh_files_number']

    def test_identical_repository_counts_keep_the_same_average(self):
        self.assertEqual(self.aggregate([1, 1]), 1)
        self.assertEqual(self.aggregate([2, 2, 2]), 2)

    def test_truncates_only_the_final_average(self):
        self.assertEqual(self.aggregate([1, 2]), 1)
        self.assertEqual(self.aggregate([1, 3]), 2)

    def test_single_repository_and_empty_input(self):
        self.assertEqual(self.aggregate([7]), 7)
        self.assertEqual(self.aggregate([]), 0)
        self.assertEqual(self.aggregate([0, 0]), 0)


if __name__ == '__main__':
    unittest.main()
