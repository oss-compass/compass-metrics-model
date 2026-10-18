"""pr_open_time must contribute exactly one sample per pull request.

The metric ``pr_open_time_avg``/``pr_open_time_mid`` is computed from one
duration per pull request: created -> merged, created -> closed, or
created -> analysis date for requests that are still open.

These tests need no search backend: the Elasticsearch iterator is replaced by
a plain list of hits.
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


def _hits(*sources):
    return [{"_source": source} for source in sources]


def test_merged_pull_request_is_sampled_once(monkeypatch):
    monkeypatch.setattr(pr_metrics, "get_all_index_data", lambda *args, **kwargs: _hits({
        "state": "merged",
        "created_at": "2024-01-01T00:00:00",
        "merged_at": "2024-02-01T00:00:00",
        "closed_at": "2024-04-01T00:00:00",
        "updated_at": "2024-05-01T00:00:00",
    }))

    result = pr_metrics.pr_open_time(None, "pr-index", ANALYSIS_DATE, ["repo"])

    # created -> merged is 31 days.  The later closed_at/updated_at
    # timestamps of an already merged request must not add a second sample.
    assert result["pr_open_time_avg"] == 31.0


def test_closed_pull_request_is_sampled_once(monkeypatch):
    monkeypatch.setattr(pr_metrics, "get_all_index_data", lambda *args, **kwargs: _hits({
        "state": "closed",
        "created_at": "2024-01-01T00:00:00",
        "closed_at": "2024-03-01T00:00:00",
        "updated_at": "2024-05-01T00:00:00",
    }))

    result = pr_metrics.pr_open_time(None, "pr-index", ANALYSIS_DATE, ["repo"])

    # created -> closed is 60 days, measured once, not twice.
    assert result["pr_open_time_avg"] == 60.0


def test_open_pull_request_without_closed_at_is_measured_to_the_analysis_date(monkeypatch):
    monkeypatch.setattr(pr_metrics, "get_all_index_data", lambda *args, **kwargs: _hits({
        "state": "open",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-05-01T00:00:00",
    }))

    result = pr_metrics.pr_open_time(None, "pr-index", ANALYSIS_DATE, ["repo"])

    # 2024-01-01 -> 2024-06-01 is 152 days; the missing closed_at must not
    # raise KeyError.
    assert result["pr_open_time_avg"] == 152.0
