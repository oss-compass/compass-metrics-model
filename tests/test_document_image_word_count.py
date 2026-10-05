"""Image alt text should not survive the image-removal stage as prose."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


class DocumentImageWordCountTests(unittest.TestCase):
    def document(self, content):
        with tempfile.TemporaryDirectory() as directory:
            utils = types.ModuleType('compass_metrics.document_metric.utils')
            utils.TMP_PATH = utils.JSON_REPOPATH = directory
            for name in ['clone_repo', 'save_json', 'load_json']:
                setattr(utils, name, Mock())
            path = Path(__file__).resolve().parents[1] / 'compass_metrics/document_metric/doc_quarty.py'
            spec = importlib.util.spec_from_file_location('document_image_words_under_test', path)
            module = importlib.util.module_from_spec(spec)
            with patch.dict(sys.modules, {utils.__name__: utils}):
                spec.loader.exec_module(module)
            file = Path(directory, 'README.md')
            file.write_text(content)
            return module.DocQuarty(str(file))

    def test_image_only_document_has_no_prose_words(self):
        document = self.document('![build status badge](badge.svg)')
        self.assertEqual(document.words, 0)
        self.assertEqual(document.pic_number['images'], 1)

    def test_images_are_removed_but_link_labels_are_preserved(self):
        document = self.document('Read [the guide](guide.md). ![architecture diagram](diagram.png)')
        self.assertEqual(document.words, 3)
        self.assertEqual(document.pic_number['images'], 1)

    def test_multiple_images_do_not_inflate_neighboring_prose(self):
        document = self.document('First ![one image](a.png) then ![another image](b.png) last')
        self.assertEqual(document.words, 3)
        self.assertEqual(document.pic_number['images'], 2)

    def test_regular_markdown_and_empty_alt_text_keep_their_behavior(self):
        document = self.document('# **Project**\nRead [documentation](guide.md) ![](logo.svg)')
        self.assertEqual(document.words, 3)


if __name__ == '__main__':
    unittest.main()
