"""Tests for search_readme_in_folder path handling.

search_readme_in_folder must resolve directory entries against the supplied
`path`, not against the process CWD. The previous `os.path.isfile(files)`
checked names relative to CWD, so whenever the caller ran from a different
working directory (the normal case for the metrics runner) the README was
never matched.
"""

import os
import tempfile

from compass_metrics.document_metric.doc_num import search_readme_in_folder


def test_readme_found_regardless_of_cwd(tmp_path):
    """README is found via `path` even when CWD differs from it."""
    (tmp_path / "README.md").write_text("HELLO_README", encoding="utf-8")
    (tmp_path / "src").mkdir()

    prev = os.getcwd()
    try:
        os.chdir(tempfile.gettempdir())  # CWD != path
        flag, content = search_readme_in_folder(str(tmp_path))
    finally:
        os.chdir(prev)

    assert flag is True
    assert content == "HELLO_README"


def test_directory_entries_are_skipped(tmp_path):
    """Subdirectories in the listing are skipped, files are considered."""
    (tmp_path / "readme.txt").write_text("LOWER", encoding="utf-8")
    (tmp_path / "subdir").mkdir()

    flag, content = search_readme_in_folder(str(tmp_path))
    assert flag is True
    assert content == "LOWER"


def test_missing_readme_returns_false(tmp_path):
    (tmp_path / "notreadme.txt").write_text("x", encoding="utf-8")
    flag, content = search_readme_in_folder(str(tmp_path))
    assert flag is False
    assert content == ""
