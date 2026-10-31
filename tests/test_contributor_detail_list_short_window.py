"""Regression tests for the contributor_detail_list() short time-window bug.

Covers GitHub issues #190, #192, #195 (duplicate reports of the same bug):
``get_regular_contributor`` raised ``UnboundLocalError: cannot access local
variable 'weeks'`` when the requested time window contained fewer than 4
Mondays, because ``weeks`` was only assigned inside an
``if len(date_list) >= 4`` guard but was referenced unconditionally by a
later loop.

The fix wraps that later loop in the same ``if len(date_list) >= 4`` guard
so it only runs for windows of >= 4 weeks. These tests verify both the v1
and v2 implementations no longer crash on a short window and still return a
valid result on a normal window, without needing a real ElasticSearch
client (``get_contributor_list`` is mocked).
"""
import sys
import types
from datetime import timedelta
from unittest.mock import patch

import datetime
import pytest

# Stub compass_common.opensearch_utils before importing the modules under
# test. The real module imports ``RequestsHttpConnection`` from
# ``elasticsearch``, which was removed in elasticsearch 9.x; that failure is
# unrelated to the bug under test. Since ``get_contributor_list`` is mocked,
# ``get_all_index_data`` is never actually called, so a no-op stub is enough
# to let the modules import cleanly.
_opensearch_stub = types.ModuleType("compass_common.opensearch_utils")
_opensearch_stub.get_all_index_data = lambda *args, **kwargs: []
sys.modules["compass_common.opensearch_utils"] = _opensearch_stub

from compass_metrics import contributor_metrics as cm_v1  # noqa: E402
from compass_metrics_v2 import contributor_metrics_v2 as cm_v2  # noqa: E402


FIXED_DATE = datetime.datetime(2026, 9, 1)


def _fake_contributor_records():
    """Return a small list of fake contributor records.

    Three contributors (alice: 3 records, bob: 2 records, carol: 1 record)
    so that ``contribution_weeks = len(list(group))`` is exercised with
    non-trivial group sizes. All records are non-bot and carry the keys that
    ``contributor_detail_list`` reads from each enriched contributor item.
    """

    def record(name, contribution, ecological_type="individual participant"):
        return {
            "contributor": name,
            "contribution": contribution,
            "contribution_without_observe": contribution,
            "ecological_type": ecological_type,
            "organization": "orgA",
            "contribution_type_list": [
                {"contribution_type": "commit", "contribution": contribution}
            ],
            "is_bot": False,
            "repo_name": "repo1",
        }

    return [
        record("alice", 33), record("alice", 33), record("alice", 33),
        record("bob", 15), record("bob", 15),
        record("carol", 5),
    ]


EXPECTED_DISTINCT = 3
EXPECTED_KEYS = {
    "contributor_detail_list", "core_count", "regular_count", "casual_count",
}


@pytest.mark.parametrize("module,mock_target", [
    (cm_v1, "compass_metrics.contributor_metrics.get_contributor_list"),
    (cm_v2, "compass_metrics_v2.contributor_metrics_v2.get_contributor_list"),
])
def test_short_window_does_not_raise(module, mock_target):
    """Window with fewer than 4 Mondays must not raise UnboundLocalError."""
    from_date = FIXED_DATE - timedelta(days=2)
    with patch(mock_target, return_value=_fake_contributor_records()):
        result = module.contributor_detail_list(
            client=None,
            contributors_enriched_index="index",
            date=FIXED_DATE,
            repo_list=["repo1"],
            from_date=from_date,
        )
    assert set(result.keys()) == EXPECTED_KEYS
    total = result["core_count"] + result["regular_count"] + result["casual_count"]
    assert total == EXPECTED_DISTINCT
    # alice (99) -> core, bob (30) -> regular, carol (5) -> casual
    assert result["core_count"] == 1
    assert result["regular_count"] == 1
    assert result["casual_count"] == 1


@pytest.mark.parametrize("module,mock_target", [
    (cm_v1, "compass_metrics.contributor_metrics.get_contributor_list"),
    (cm_v2, "compass_metrics_v2.contributor_metrics_v2.get_contributor_list"),
])
def test_normal_window_valid_structure(module, mock_target):
    """Default 90-day window (>= 4 Mondays) must return a valid structure."""
    with patch(mock_target, return_value=_fake_contributor_records()):
        result = module.contributor_detail_list(
            client=None,
            contributors_enriched_index="index",
            date=FIXED_DATE,
            repo_list=["repo1"],
        )
    assert set(result.keys()) == EXPECTED_KEYS
    total = result["core_count"] + result["regular_count"] + result["casual_count"]
    assert total == EXPECTED_DISTINCT
