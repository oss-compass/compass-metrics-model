"""Regression tests for block-comment state and per-line counting."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


class MultilineCommentRatioTests(unittest.TestCase):
    def ratio(self, name, source):
        with tempfile.TemporaryDirectory() as directory:
            utils = types.ModuleType('compass_metrics.utils_code_readability')
            utils.TMP_PATH = utils.JSON_REPOPATH = directory
            for attribute in ['load_json', 'check_github_gitee', 'clone_repo', 'save_json']:
                setattr(utils, attribute, Mock())
            path = Path(__file__).resolve().parents[1] / 'compass_metrics/code_readability.py'
            spec = importlib.util.spec_from_file_location('comment_ratio_under_test', path)
            module = importlib.util.module_from_spec(spec)
            with patch.dict(sys.modules, {utils.__name__: utils}):
                spec.loader.exec_module(module)
            file = Path(directory, name)
            file.write_text(source)
            return module.calculate_comment_ratio(str(file), module.COMMENT_SYNTAX[module.detect_language(str(file))])

    def test_python_multiline_docstring_counts_its_body(self):
        self.assertEqual(self.ratio('demo.py', '"""Summary\nMore details\n"""\nx = 1\n'), (75, 3, 4))

    def test_python_hash_inside_docstring_is_counted_once(self):
        self.assertEqual(self.ratio('demo.py', '"""# summary\n# body\n"""\n'), (100, 3, 3))

    def test_python_inline_docstring_does_not_open_a_block(self):
        self.assertEqual(self.ratio('demo.py', '"""Summary"""\nx = 1\n'), (50, 1, 2))

    def test_c_line_comment_marker_inside_block_is_counted_once(self):
        self.assertEqual(self.ratio('demo.c', '/* // header\n// body\n*/\nint value;\n'), (75, 3, 4))

    def test_inline_c_block_and_line_comment_count_once(self):
        self.assertEqual(self.ratio('demo.c', '/* note */ // more\nint value;\n'), (50, 1, 2))

    def test_another_block_after_closing_one_can_continue_on_next_line(self):
        self.assertEqual(self.ratio('demo.c', '/* first */ /* second\nbody\n*/\nint value;\n'), (75, 3, 4))

    def test_shell_line_comments_and_empty_files(self):
        self.assertEqual(self.ratio('demo.sh', '# comment\necho hello\n'), (50, 1, 2))
        self.assertEqual(self.ratio('empty.py', ''), (0, 0, 0))


if __name__ == '__main__':
    unittest.main()
