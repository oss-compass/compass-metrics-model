"""Unit tests for the per-contributor code contribution metrics (git_metrics_v2)."""

import unittest
from datetime import datetime

from compass_metrics_v2.git_metrics_v2 import (
    _get_period_range,
    contributor_code_contribution_by_period,
    contributor_code_contribution_ratio_by_period,
)


class _FakeClient:
    """Minimal OpenSearch stub that records queries and replays a canned response."""

    def __init__(self, response):
        self.response = response
        self.calls = []

    def search(self, index=None, body=None):
        self.calls.append({"index": index, "body": body})
        return self.response


def _buckets_response(rows):
    """Build a terms aggregation response from (author, commits, added, removed, changed)."""
    buckets = []
    for author, commits, added, removed, changed in rows:
        buckets.append({
            "key": author,
            "commit_count": {"value": commits},
            "lines_added": {"value": added},
            "lines_removed": {"value": removed},
            "lines_changed": {"value": changed},
        })
    return {"aggregations": {"by_author": {"buckets": buckets}}}


class PeriodRangeTest(unittest.TestCase):
    def test_month_range_is_inclusive(self):
        start, end = _get_period_range(datetime(2025, 3, 15), "month")
        self.assertEqual(start, datetime(2025, 3, 1, 0, 0, 0))
        self.assertEqual(end, datetime(2025, 3, 31, 23, 59, 59))

    def test_quarter_range(self):
        start, end = _get_period_range(datetime(2025, 5, 20), "quarter")
        self.assertEqual(start, datetime(2025, 4, 1, 0, 0, 0))
        self.assertEqual(end, datetime(2025, 6, 30, 23, 59, 59))

    def test_invalid_period_rejected(self):
        with self.assertRaises(ValueError):
            _get_period_range(datetime(2025, 1, 1), "week")


class ContributorCodeContributionTest(unittest.TestCase):
    rows = [
        ("alice", 3, 100, 10, 110),
        ("bob", 1, 40, 0, 40),
    ]

    def test_volume_totals_and_detail(self):
        client = _FakeClient(_buckets_response(self.rows))
        result = contributor_code_contribution_by_period(
            client, "github-git_enriched", datetime(2025, 3, 15), ["https://github.com/x/y"])

        self.assertEqual(result["contributor_code_contribution"], 150)
        self.assertEqual(result["contributor_code_contribution_contributors"], 2)
        detail = result["contributor_code_contribution_detail"]
        self.assertEqual([item["author_name"] for item in detail], ["alice", "bob"])
        self.assertEqual(detail[0]["commit_count"], 3)
        self.assertEqual(detail[0]["lines_added"], 100)
        self.assertEqual(detail[1]["lines_removed"], 0)

    def test_query_scopes_repo_and_period(self):
        client = _FakeClient(_buckets_response(self.rows))
        contributor_code_contribution_by_period(
            client, "github-git_enriched", datetime(2025, 3, 15), ["https://github.com/x/y"])

        self.assertEqual(client.calls[0]["index"], "github-git_enriched")
        body = client.calls[0]["body"]
        self.assertEqual(body["query"]["bool"]["must"][0]["terms"]["tag"],
                         ["https://github.com/x/y.git"])
        date_range = body["query"]["bool"]["filter"][0]["range"]["grimoire_creation_date"]
        self.assertEqual(date_range["gte"], "2025-03-01T00:00:00")
        self.assertEqual(date_range["lte"], "2025-03-31T23:59:59")
        self.assertEqual(body["aggs"]["by_author"]["terms"]["field"], "author_name")
        self.assertEqual(body["aggs"]["by_author"]["terms"]["order"], {"lines_changed": "desc"})

    def test_bots_are_excluded_by_default(self):
        client = _FakeClient(_buckets_response(self.rows))
        contributor_code_contribution_by_period(
            client, "github-git_enriched", datetime(2025, 3, 15), ["https://github.com/x/y"])
        self.assertEqual(client.calls[0]["body"]["query"]["bool"]["must_not"],
                         [{"term": {"author_bot": True}}])

    def test_bots_can_be_included(self):
        client = _FakeClient(_buckets_response(self.rows))
        result = contributor_code_contribution_by_period(
            client, "github-git_enriched", datetime(2025, 3, 15),
            ["https://github.com/x/y"], include_bot=True)
        self.assertNotIn("must_not", client.calls[0]["body"]["query"]["bool"])
        self.assertEqual(result["contributor_code_contribution"], 150)

    def test_top_n_limits_bucket_size(self):
        client = _FakeClient(_buckets_response(self.rows))
        contributor_code_contribution_by_period(
            client, "github-git_enriched", datetime(2025, 3, 15),
            ["https://github.com/x/y"], top_n=5)
        self.assertEqual(client.calls[0]["body"]["aggs"]["by_author"]["terms"]["size"], 5)

    def test_null_values_are_normalised_to_zero(self):
        client = _FakeClient(_buckets_response([("alice", None, None, None, None)]))
        detail = contributor_code_contribution_by_period(
            client, "github-git_enriched", datetime(2025, 3, 15),
            ["https://github.com/x/y"])["contributor_code_contribution_detail"]
        self.assertEqual(detail[0]["commit_count"], 0)
        self.assertEqual(detail[0]["lines_changed"], 0)

    def test_empty_result(self):
        client = _FakeClient(_buckets_response([]))
        result = contributor_code_contribution_by_period(
            client, "github-git_enriched", datetime(2025, 3, 15), ["https://github.com/x/y"])
        self.assertEqual(result["contributor_code_contribution"], 0)
        self.assertEqual(result["contributor_code_contribution_contributors"], 0)
        self.assertEqual(result["contributor_code_contribution_detail"], [])

    def test_ratio_sums_to_one_and_top_share(self):
        client = _FakeClient(_buckets_response(self.rows))
        result = contributor_code_contribution_ratio_by_period(
            client, "github-git_enriched", datetime(2025, 3, 15), ["https://github.com/x/y"])

        self.assertEqual(result["contributor_code_contribution_total_lines"], 150)
        self.assertAlmostEqual(result["contributor_code_contribution_ratio"], 0.733333, places=6)
        ratios = result["contributor_code_contribution_ratio_detail"]
        self.assertAlmostEqual(sum(item["contribution_ratio"] for item in ratios), 1.0, places=6)

    def test_ratio_is_none_without_code(self):
        client = _FakeClient(_buckets_response([]))
        result = contributor_code_contribution_ratio_by_period(
            client, "github-git_enriched", datetime(2025, 3, 15), ["https://github.com/x/y"])
        self.assertIsNone(result["contributor_code_contribution_ratio"])
        self.assertEqual(result["contributor_code_contribution_ratio_detail"], [])
