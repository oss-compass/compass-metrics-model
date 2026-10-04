"""Folder counting uses real files; network/config helpers are isolated on import."""
import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def load_doc_num(tmp_path):
    utils = types.ModuleType('compass_metrics.document_metric.utils')
    utils.TMP_PATH = str(tmp_path)
    utils.JSON_REPOPATH = str(tmp_path)
    utils.clone_repo = lambda *args: None
    utils.save_json = lambda *args: None
    spec = importlib.util.spec_from_file_location(
        'doc_num_under_test', ROOT / 'compass_metrics/document_metric/doc_num.py'
    )
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {utils.__name__: utils}):
        spec.loader.exec_module(module)
    return module


class BinaryDocumentCountTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'example-v1'
        self.repo.mkdir()
        self.module = load_doc_num(self.root)

    def test_counts_pdf_and_word_documents_with_text_documents(self):
        shutil.copyfile(ROOT / 'quantifying_criticality_algorithm.pdf', self.repo / 'guide.pdf')
        with zipfile.ZipFile(self.repo / 'guide.docx', 'w', zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('[Content_Types].xml', '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
            archive.writestr('word/document.xml', '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body/></w:document>')
        (self.repo / 'README.md').write_text('# Example\n', encoding='utf-8')
        count, details = self.module.count_documents_from_folder(str(self.repo))
        self.assertEqual(count, 3)
        self.assertEqual(
            {item['path'] for item in details},
            {'example-v1/guide.pdf', 'example-v1/guide.docx', 'example-v1/README.md'},
        )

    def test_respects_custom_extensions_and_requirements_exclusion(self):
        (self.repo / 'requirements.txt').write_text('example==1\n')
        (self.repo / 'notes.txt').write_text('Notes')
        (self.repo / 'README.md').write_text('Readme')
        count, details = self.module.count_documents_from_folder(str(self.repo), ['.txt'])
        self.assertEqual(count, 1)
        self.assertEqual(details, [{'name': 'notes.txt', 'path': 'example-v1/notes.txt'}])

    def test_skips_files_that_cannot_be_opened(self):
        (self.repo / 'unreadable.md').write_text('Readme')
        with patch('builtins.open', side_effect=PermissionError('denied')):
            self.assertEqual(self.module.count_documents_from_folder(str(self.repo)), (0, []))


if __name__ == '__main__':
    unittest.main()
