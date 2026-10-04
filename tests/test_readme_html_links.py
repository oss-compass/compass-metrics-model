"""README link extraction without importing network/configuration helpers."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


def load_doc_num():
    utils = types.ModuleType('compass_metrics.document_metric.utils')
    utils.TMP_PATH = utils.JSON_REPOPATH = ''
    utils.save_json = utils.clone_repo = lambda *args: None
    path = Path(__file__).resolve().parents[1] / 'compass_metrics/document_metric/doc_num.py'
    spec = importlib.util.spec_from_file_location('readme_links_under_test', path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {utils.__name__: utils}):
        spec.loader.exec_module(module)
    return module


class ReadmeHtmlLinksTests(unittest.TestCase):
    def setUp(self):
        self.module = load_doc_num()

    def check_links(self, content, expected):
        count, links = self.module.count_documents_from_Readme(content)
        self.assertEqual(count, len(expected))
        self.assertEqual([link['path'] for link in links], expected)
        self.assertEqual([link['name'] for link in links], [
            url.replace('http://', '').replace('https://', '') for url in expected
        ])

    def test_single_quoted_anchor(self):
        self.check_links("<a href='https://example.org/guide'>Guide</a>", ['https://example.org/guide'])

    def test_multiple_anchors_and_markdown_on_one_line(self):
        self.check_links(
            '<a href="https://example.org/a">A</a> <a href="https://example.org/b">B</a> '
            '[C](https://example.org/c)',
            ['https://example.org/a', 'https://example.org/b', 'https://example.org/c'],
        )

    def test_multiline_anchor_attributes_and_entities(self):
        self.check_links(
            '<a class="docs"\n href="https://example.org/?a=1&amp;b=2">Docs</a>',
            ['https://example.org/?a=1&b=2'],
        )

    def test_anchor_url_label_is_not_counted_twice(self):
        self.check_links('<a href="https://example.org/a">https://example.org/a</a>', ['https://example.org/a'])

    def test_markdown_plain_urls_and_autolinks(self):
        self.check_links(
            '[Guide](https://example.org/a)\nhttps://example.org/b\n<https://example.org/c>',
            ['https://example.org/a', 'https://example.org/b', 'https://example.org/c'],
        )

    def test_media_links_and_missing_href(self):
        self.check_links(
            '<a href="https://youtube.com/watch?v=1">Video</a> '
            '<a name="section">Section</a> ![image](https://example.org/image.png)', [],
        )


if __name__ == '__main__':
    unittest.main()
