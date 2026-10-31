"""Tests for count_documents_from_Readme link parsing.

Covers the `<a href ...>` extraction path, which previously crashed with an
IndexError whenever the href attribute used single quotes, had spaces around
`=`, or was missing entirely (e.g. `<a href>`). These forms are common in
real README files.
"""

from compass_metrics.document_metric.doc_num import count_documents_from_Readme


def test_double_quoted_href_is_counted():
    count, links = count_documents_from_Readme(
        '<a href="https://example.com/a">x</a>'
    )
    assert count == 1
    assert links[0]["path"] == "https://example.com/a"


def test_single_quoted_href_is_counted():
    """Single-quoted hrefs are common; the old split('href=\"')[1] raised."""
    count, links = count_documents_from_Readme(
        "<a href='https://example.com/b'>x</a>"
    )
    assert count == 1
    assert links[0]["path"] == "https://example.com/b"


def test_href_with_spaces_around_equals_is_counted():
    """`<a href = \"...\">` must not raise IndexError."""
    count, links = count_documents_from_Readme(
        '<a href = "https://example.com/c">x</a>'
    )
    assert count == 1
    assert links[0]["path"] == "https://example.com/c"


def test_trailing_paren_is_stripped():
    count, links = count_documents_from_Readme(
        '<a href="https://example.com/d)">x</a>'
    )
    assert count == 1
    assert links[0]["path"] == "https://example.com/d"


def test_video_link_is_excluded():
    count, links = count_documents_from_Readme(
        '<a href="https://youtube.com/watch?v=1">x</a>'
    )
    assert count == 0
    assert links == []


def test_malformed_anchor_without_href_does_not_crash():
    """`<a href>` (no value) must be skipped, not raise IndexError."""
    count, links = count_documents_from_Readme("<a href>broken</a>")
    assert count == 0
    assert links == []


def test_plain_text_http_link_still_counted():
    count, links = count_documents_from_Readme("see https://plain.com/x here")
    assert count == 1
    assert links[0]["path"] == "https://plain.com/x"
