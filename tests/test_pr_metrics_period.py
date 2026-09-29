"""Regression tests for the PR period metrics' date windows.

Audit finding: ``pr_metrics_v2.get_period_range`` located the start of the
natural month/quarter/year but then returned the caller's ``end_date``
unchanged as the *end* of the window.  ``get_uuid_count_query`` (used by
``build_base_pr_query``) renders both bounds at day precision with an
exclusive upper bound, so for a period start the window collapsed to
``gte == lt`` and every current-period PR metric -- including
``pr_comment_count_by_period``, the only PR metric consumed by the shipped
Contribution Activity model -- was reported as 0.

These tests pin the fixed behaviour:

* the helper returns the period's last second;
* the generated queries use an inclusive, second-precision upper bound so a
  document dated on the last day of the period is counted;
* the bounds are never equal for a non-empty period.
"""

import unittest
from datetime import datetime

from compass_common.datetime import get_period_bounds
from compass_metrics_v2.pr_metrics_v2 import (
    build_base_pr_query,
    get_period_range,
    get_previous_period_range,
    pr_closed_count_by_period,
    pr_comment_count_by_period,
    pr_comment_rank_by_period,
    pr_created_and_closed_count_by_period,
    pr_created_and_responded_count_by_period,
    pr_created_count_by_period,
)

INDEX = "github-pulls_enriched"
TAG = "https://github.com/x/y"


def _parse_bound(value):
    """Convert an OpenSearch range bound into a comparable Python value."""
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    return value


def _bounds_match(value, bounds):
    for operator, bound in bounds.items():
        limit = _parse_bound(bound)
        if operator == "gte" and not value >= limit:
            return False
        if operator == "gt" and not value > limit:
            return False
        if operator == "lte" and not value <= limit:
            return False
        if operator == "lt" and not value < limit:
            return False
    return True


def _clause_matches(document, clause):
    if "range" in clause:
        for field, bounds in clause["range"].items():
            if document.get(field) is None:
                return False
            if not _bounds_match(document[field], bounds):
                return False
        return True
    if "term" in clause:
        return all(document.get(field) == expected for field, expected in clause["term"].items())
    if "terms" in clause:
        return all(document.get(field) in expected for field, expected in clause["terms"].items())
    if "match_phrase" in clause:
        return all(document.get(field) == expected for field, expected in clause["match_phrase"].items())
    # Scripts and any other clauses are irrelevant to the window assertions.
    return True


def _matches(document, body):
    bool_query = body.get("query", {}).get("bool", {})

    must = bool_query.get("must", [])
    must = [must] if isinstance(must, dict) else must
    if not all(_clause_matches(document, clause) for clause in must):
        return False

    filters = bool_query.get("filter", [])
    filters = [filters] if isinstance(filters, dict) else filters
    if not all(_clause_matches(document, clause) for clause in filters):
        return False

    must_not = bool_query.get("must_not", [])
    must_not = [must_not] if isinstance(must_not, dict) else must_not
    if any(_clause_matches(document, clause) for clause in must_not):
        return False

    return True


class _FakeClient:
    """In-memory OpenSearch stub.

    It records every query body and, crucially, *evaluates* the generated
    range filters against a document set instead of blindly replaying a canned
    response.  A regression back to an empty ``gte == lt`` window therefore
    surfaces as a zero count instead of passing silently.
    """

    def __init__(self, documents):
        self.documents = documents
        self.calls = []

    def search(self, index=None, body=None):
        self.calls.append({"index": index, "body": body})
        matched = [document for document in self.documents if _matches(document, body)]
        aggregation = body.get("aggs", {}).get("count_of_uuid", {})
        option = next(iter(aggregation), None)
        field = aggregation.get(option, {}).get("field") if option else None
        return {
            "hits": {
                "total": {"value": len(matched)},
                "hits": [{"_source": document} for document in matched],
            },
            "aggregations": {"count_of_uuid": {"value": self._aggregate(option, field, matched)}},
        }

    @staticmethod
    def _aggregate(option, field, matched):
        if option == "cardinality":
            return len({document[field] for document in matched if field in document})
        if option == "sum":
            return sum(document[field] for document in matched if field in document)
        return len(matched)


def _date_range(client, call_index=0, date_field="grimoire_creation_date"):
    filters = client.calls[call_index]["body"]["query"]["bool"]["filter"]
    for clause in filters:
        if date_field in clause.get("range", {}):
            return clause["range"][date_field]
    raise AssertionError("no range query for %s in %r" % (date_field, filters))


DOCUMENTS = [
    {
        "uuid": "pr-1",
        "pull_request": "true",
        "state": "open",
        "tag": TAG,
        "grimoire_creation_date": datetime(2025, 3, 5, 9, 0),
        "num_review_comments_without_bot": 4,
        "time_to_first_attention_without_bot": 1.5,
    },
    {
        "uuid": "pr-2",
        "pull_request": "true",
        "state": "closed",
        "tag": TAG,
        "grimoire_creation_date": datetime(2025, 3, 31, 23, 58),
        "closed_at": datetime(2025, 3, 31, 23, 59, 30),
        "num_review_comments_without_bot": 2,
        "time_to_first_attention_without_bot": 2.0,
    },
    {
        "uuid": "pr-3",
        "pull_request": "true",
        "state": "open",
        "tag": TAG,
        "grimoire_creation_date": datetime(2025, 3, 31, 12, 0),
        "num_review_comments_without_bot": 1,
        "time_to_first_attention_without_bot": 0.5,
    },
    # Belongs to the next period and must never leak into a March window.
    {
        "uuid": "pr-4",
        "pull_request": "true",
        "state": "closed",
        "tag": TAG,
        "grimoire_creation_date": datetime(2025, 4, 1, 0, 0),
        "closed_at": datetime(2025, 4, 1, 8, 0),
        "num_review_comments_without_bot": 9,
        "time_to_first_attention_without_bot": 5.0,
    },
]


class PeriodRangeTest(unittest.TestCase):
    def test_month_range_ends_on_last_second(self):
        start, end = get_period_range(datetime(2025, 3, 15), "month")
        self.assertEqual(start, datetime(2025, 3, 1, 0, 0, 0))
        self.assertEqual(end, datetime(2025, 3, 31, 23, 59, 59))
        self.assertNotEqual(start, end)

    def test_quarter_range_ends_on_last_second(self):
        start, end = get_period_range(datetime(2025, 5, 20), "quarter")
        self.assertEqual(start, datetime(2025, 4, 1, 0, 0, 0))
        self.assertEqual(end, datetime(2025, 6, 30, 23, 59, 59))

    def test_year_range_ends_on_last_second(self):
        start, end = get_period_range(datetime(2025, 7, 1), "year")
        self.assertEqual(start, datetime(2025, 1, 1, 0, 0, 0))
        self.assertEqual(end, datetime(2025, 12, 31, 23, 59, 59))

    def test_december_month_does_not_overflow_into_next_year(self):
        start, end = get_period_range(datetime(2025, 12, 10), "month")
        self.assertEqual(start, datetime(2025, 12, 1, 0, 0, 0))
        self.assertEqual(end, datetime(2025, 12, 31, 23, 59, 59))

    def test_fourth_quarter_ends_in_december(self):
        start, end = get_period_range(datetime(2025, 11, 5), "quarter")
        self.assertEqual(start, datetime(2025, 10, 1, 0, 0, 0))
        self.assertEqual(end, datetime(2025, 12, 31, 23, 59, 59))

    def test_leap_year_february_is_handled(self):
        _, end = get_period_range(datetime(2024, 2, 10), "month")
        self.assertEqual(end, datetime(2024, 2, 29, 23, 59, 59))

    def test_non_leap_february_is_handled(self):
        _, end = get_period_range(datetime(2023, 2, 10), "month")
        self.assertEqual(end, datetime(2023, 2, 28, 23, 59, 59))

    def test_end_date_argument_is_not_used_as_upper_bound(self):
        moment = datetime(2025, 3, 15, 12, 30, 45)
        start, end = get_period_range(moment, "month")
        self.assertNotEqual(end, moment)
        self.assertGreater(end, moment)

    def test_bounds_are_never_equal_for_supported_periods(self):
        moments = (datetime(2025, 1, 1), datetime(2025, 6, 15, 12, 30), datetime(2025, 12, 31, 23, 59, 59))
        for moment in moments:
            for period in ("month", "quarter", "year"):
                start, end = get_period_range(moment, period)
                self.assertLess(start, end)

    def test_helper_matches_the_shared_implementation(self):
        for period in ("month", "quarter", "year"):
            self.assertEqual(get_period_range(datetime(2025, 3, 15), period),
                             get_period_bounds(datetime(2025, 3, 15), period))

    def test_invalid_period_is_rejected(self):
        with self.assertRaises(ValueError):
            get_period_range(datetime(2025, 1, 1), "week")
        with self.assertRaises(ValueError):
            get_period_bounds(datetime(2025, 1, 1), "week")

    def test_previous_month_range_is_unchanged(self):
        start, end = get_previous_period_range(datetime(2025, 3, 15), "month")
        self.assertEqual(start, datetime(2025, 2, 1, 0, 0, 0))
        self.assertEqual(end, datetime(2025, 2, 28, 23, 59, 59, 999999))

    def test_previous_period_never_collapses(self):
        for period in ("month", "quarter", "year"):
            start, end = get_previous_period_range(datetime(2025, 3, 15), period)
            self.assertLess(start, end)


class PrPeriodWindowTest(unittest.TestCase):
    def test_created_count_includes_last_day_and_excludes_next_period(self):
        client = _FakeClient(DOCUMENTS)
        result = pr_created_count_by_period(client, INDEX, datetime(2025, 3, 1), [TAG])
        self.assertEqual(result["pr_created_count"], 3)
        self.assertEqual(result["period"], "month")
        self.assertEqual(client.calls[0]["index"], INDEX)

        date_range = _date_range(client)
        self.assertEqual(date_range, {"gte": "2025-03-01T00:00:00",
                                      "lte": "2025-03-31T23:59:59"})
        self.assertNotEqual(date_range["gte"], date_range["lte"])

    def test_comment_count_is_no_longer_zero(self):
        client = _FakeClient(DOCUMENTS)
        result = pr_comment_count_by_period(client, INDEX, datetime(2025, 3, 1), [TAG])
        # 4 + 2 + 1 comments on the three March PRs; the April PR is excluded.
        self.assertEqual(result["pr_comment_count"], 7)

    def test_document_on_last_day_is_counted(self):
        client = _FakeClient([document for document in DOCUMENTS if document["uuid"] == "pr-3"])
        result = pr_created_count_by_period(client, INDEX, datetime(2025, 3, 1), [TAG])
        self.assertEqual(result["pr_created_count"], 1)

    def test_document_on_last_second_is_counted(self):
        document = dict(DOCUMENTS[0])
        document["uuid"] = "pr-boundary"
        document["grimoire_creation_date"] = datetime(2025, 3, 31, 23, 59, 59)
        client = _FakeClient([document])
        result = pr_created_count_by_period(client, INDEX, datetime(2025, 3, 1), [TAG])
        self.assertEqual(result["pr_created_count"], 1)

    def test_created_and_responded_counts_march_prs(self):
        client = _FakeClient(DOCUMENTS)
        result = pr_created_and_responded_count_by_period(client, INDEX, datetime(2025, 3, 1), [TAG])
        self.assertEqual(result["pr_created_and_responded_count"], 3)

    def test_closed_count_counts_march_closed_prs(self):
        client = _FakeClient(DOCUMENTS)
        result = pr_closed_count_by_period(client, INDEX, datetime(2025, 3, 1), [TAG])
        self.assertEqual(result["pr_closed_count"], 1)

    def test_created_and_closed_counts_prs_closed_in_period(self):
        client = _FakeClient(DOCUMENTS)
        result = pr_created_and_closed_count_by_period(client, INDEX, datetime(2025, 3, 1), [TAG])
        self.assertEqual(result["pr_created_and_closed_count"], 1)

    def test_comment_rank_uses_inclusive_window(self):
        client = _FakeClient(DOCUMENTS)
        result = pr_comment_rank_by_period(client, INDEX, datetime(2025, 3, 1), [TAG])
        self.assertEqual(len(result["pr_comment_rank"]), 3)
        self.assertEqual(_date_range(client)["lte"], "2025-03-31T23:59:59")

    def test_every_period_metric_builds_a_non_empty_window(self):
        metrics = (
            pr_comment_count_by_period,
            pr_created_count_by_period,
            pr_created_and_responded_count_by_period,
            pr_closed_count_by_period,
            pr_created_and_closed_count_by_period,
        )
        for metric in metrics:
            for moment, period in ((datetime(2025, 3, 1), "month"),
                                   (datetime(2025, 5, 1), "quarter"),
                                   (datetime(2025, 1, 1), "year")):
                client = _FakeClient(DOCUMENTS)
                metric(client, INDEX, moment, [TAG], period=period)
                date_range = _date_range(client)
                self.assertNotEqual(date_range["gte"], date_range["lte"],
                                    "%s produced an empty %s window" % (metric.__name__, period))

    def test_build_base_query_uses_inclusive_second_precision(self):
        query = build_base_pr_query("cardinality", [TAG], "uuid", "grimoire_creation_date",
                                    datetime(2025, 3, 1), datetime(2025, 3, 31, 23, 59, 59))
        date_range = query["query"]["bool"]["filter"][0]["range"]["grimoire_creation_date"]
        self.assertEqual(date_range["gte"], "2025-03-01T00:00:00")
        self.assertEqual(date_range["lte"], "2025-03-31T23:59:59")
        self.assertNotEqual(date_range["gte"], date_range["lte"])


if __name__ == "__main__":
    unittest.main()
