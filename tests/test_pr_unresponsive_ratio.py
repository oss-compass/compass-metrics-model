"""pr_unresponsive_ratio must be 0.0 when no pull request is unresponsive.

The ratio is ``unresponsive / total``.  A repository that answers every pull
request has a ratio of zero, which is a perfectly valid observation; only a
window without any pull request at all has no observable ratio.
"""

import datetime
import sys
import types


def _install_search_stubs():
    """The metric modules import the search clients at module import time."""
    if "elasticsearch" in sys.modules:
        return

    class _Client:
        def __init__(self, *args, **kwargs):
            pass

    elasticsearch = types.ModuleType("elasticsearch")
    elasticsearch.Elasticsearch = _Client
    elasticsearch.RequestsHttpConnection = _Client
    helpers = types.ModuleType("elasticsearch.helpers")
    helpers.bulk = lambda *args, **kwargs: None
    elasticsearch.helpers = helpers
    exceptions = types.ModuleType("elasticsearch.exceptions")

    class NotFoundError(Exception):
        pass

    exceptions.NotFoundError = NotFoundError
    elasticsearch.exceptions = exceptions

    opensearchpy = types.ModuleType("opensearchpy")
    opensearchpy.OpenSearch = _Client
    os_helpers = types.ModuleType("opensearchpy.helpers")
    os_helpers.bulk = lambda *args, **kwargs: None
    os_helpers.scan = lambda *args, **kwargs: None
    opensearchpy.helpers = os_helpers

    sys.modules["elasticsearch"] = elasticsearch
    sys.modules["elasticsearch.helpers"] = helpers
    sys.modules["elasticsearch.exceptions"] = exceptions
    sys.modules["opensearchpy"] = opensearchpy
    sys.modules["opensearchpy.helpers"] = os_helpers


_install_search_stubs()

from compass_metrics import pr_metrics  # noqa: E402

ANALYSIS_DATE = datetime.datetime(2024, 6, 1)


def _counts(monkeypatch, unresponsive, total):
    monkeypatch.setattr(
        pr_metrics, "pr_unresponsive_count",
        lambda *args, **kwargs: {"pr_unresponsive_count": unresponsive})
    monkeypatch.setattr(
        pr_metrics, "pr_count",
        lambda *args, **kwargs: {"pr_count": total})


def test_no_unresponsive_pull_request_is_a_zero_ratio(monkeypatch):
    _counts(monkeypatch, unresponsive=0, total=40)

    result = pr_metrics.pr_unresponsive_ratio(None, "pr-index", ANALYSIS_DATE, ["repo"])

    assert result["pr_unresponsive_ratio"] == 0.0


def test_partially_unresponsive_pull_requests_are_a_fraction(monkeypatch):
    _counts(monkeypatch, unresponsive=10, total=40)

    result = pr_metrics.pr_unresponsive_ratio(None, "pr-index", ANALYSIS_DATE, ["repo"])

    assert result["pr_unresponsive_ratio"] == 0.25


def test_window_without_pull_requests_has_no_ratio(monkeypatch):
    _counts(monkeypatch, unresponsive=0, total=0)

    result = pr_metrics.pr_unresponsive_ratio(None, "pr-index", ANALYSIS_DATE, ["repo"])

    assert result["pr_unresponsive_ratio"] is None
