"""Tests for count_documents_from_folder error handling.

The per-file read is wrapped in a try/except that previously used a bare
`except:`. It is now narrowed to the failures that can actually happen here
(OSError while opening, UnicodeDecodeError while decoding a non-UTF-8 file),
so genuine bugs are no longer swallowed — while unreadable members are still
skipped as before.
"""

from compass_metrics.document_metric.doc_num import count_documents_from_folder


def test_invalid_utf8_member_is_skipped(tmp_path):
    """A non-UTF-8 file raises UnicodeDecodeError and is skipped, not counted."""
    (tmp_path / "good.txt").write_text("hello", encoding="utf-8")
    (tmp_path / "bad.txt").write_bytes(b"\xff\xfe\x00\x01not utf-8")

    count, details = count_documents_from_folder(str(tmp_path))

    names = {d["name"] for d in details}
    assert "good.txt" in names
    assert "bad.txt" not in names
    assert count == 1


def test_only_matching_extensions_counted(tmp_path):
    (tmp_path / "a.md").write_text("# doc", encoding="utf-8")
    (tmp_path / "b.py").write_text("print(1)", encoding="utf-8")
    (tmp_path / "c.txt").write_text("text", encoding="utf-8")

    count, details = count_documents_from_folder(str(tmp_path), extensions=[".md", ".txt"])

    names = {d["name"] for d in details}
    assert names == {"a.md", "c.txt"}
    assert count == 2
