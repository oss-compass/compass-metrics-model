"""Regression tests for the contributor mileage split of the metrics models.

``contributor_detail_list()`` raised ``UnboundLocalError`` whenever callers
passed an analysis window shorter than four weeks. The regular-contributor rule
marks contributors who were active in 3/4 of the weeks covered by the window,
and the week threshold was only computed for windows containing at least four
Mondays while being read unconditionally afterwards. These tests pin the
behaviour for short windows (the rule must be skipped) and make sure longer
windows keep working.

Run from the repository root with
``python -m pytest tests/test_contributor_metrics_short_window.py`` or
``python -m unittest discover -s tests``.
"""

import datetime
from unittest import TestCase
from unittest import mock

import compass_metrics.contributor_metrics as contributor_metrics_v1
import compass_metrics_v2.contributor_metrics_v2 as contributor_metrics_v2


class _FakeClient:
    """Placeholder for the Elasticsearch client.

    ``contributor_detail_list()`` only uses its client to fetch raw contributor
    records through ``get_contributor_list()``, which every test patches out, so
    this object is never touched.
    """


def _contributor_record(contributor, contribution):
    """Build one raw enriched-index record in the shape the aggregation reads.

    ``contributor_detail_list()`` groups the raw records by contributor and
    derives ``contribution_weeks`` from the size of that group. Passing the same
    contributor several times therefore models a contributor active in several
    weeks of the analysis window.
    """
    return {
        "contributor": contributor,
        "contribution": contribution,
        "contribution_without_observe": contribution,
        "ecological_type": "individual participant",
        "organization": None,
        "is_bot": False,
        "repo_name": "demo/repo",
        "contribution_type_list": [
            {"contribution_type": "code_author", "contribution": contribution}
        ],
    }


def _aggregate(module, end_date, from_date, records):
    """Call ``contributor_detail_list()`` with a stubbed contributor lookup."""
    with mock.patch.object(module, "get_contributor_list", return_value=records):
        return module.contributor_detail_list(
            _FakeClient(),
            "contributors_enriched",
            end_date,
            ["demo/repo"],
            from_date=from_date,
        )


def _mileage_by_contributor(result):
    """Map every contributor of a result to its mileage type."""
    return {
        item["contributor"]: item["mileage_type"]
        for item in result["contributor_detail_list"]
    }


# The v1 and the v2 module carry the same mileage-split implementation, and both
# were affected by the bug, so each scenario is exercised against both of them.
_MODULES = (contributor_metrics_v1, contributor_metrics_v2)


class ShortAnalysisWindowTest(TestCase):
    """The mileage split must work for analysis windows shorter than four weeks."""

    # A Wednesday, chosen so that subtracting whole weeks lands on other
    # Wednesdays and the number of Mondays in each window stays easy to verify.
    END_DATE = datetime.date(2024, 5, 15)

    def _simple_records(self):
        # alice reaches 50% of the contributions, bob pushes the running total
        # past 80%, so the expected split is core/regular/casual.
        return [
            _contributor_record("alice", 6),
            _contributor_record("bob", 3),
            _contributor_record("carol", 1),
        ]

    def test_one_day_window_returns_full_split(self):
        # The reported crash: a one-day window raised UnboundLocalError inside
        # the "3/4 of the weeks" rule instead of returning classifications.
        from_date = self.END_DATE - datetime.timedelta(days=1)
        for module in _MODULES:
            with self.subTest(module=module.__name__):
                result = _aggregate(module, self.END_DATE, from_date, self._simple_records())
                self.assertEqual(result["core_count"], 1)
                self.assertEqual(result["regular_count"], 1)
                self.assertEqual(result["casual_count"], 1)
                self.assertEqual(
                    _mileage_by_contributor(result),
                    {"alice": "core", "bob": "regular", "carol": "casual"},
                )

    def test_window_with_three_mondays_does_not_raise(self):
        # 20 days cover the Mondays 2024-04-29, 2024-05-06 and 2024-05-13,
        # which is still one Monday short of the four-week threshold.
        from_date = self.END_DATE - datetime.timedelta(days=20)
        for module in _MODULES:
            with self.subTest(module=module.__name__):
                result = _aggregate(module, self.END_DATE, from_date, self._simple_records())
                self.assertEqual(
                    _mileage_by_contributor(result),
                    {"alice": "core", "bob": "regular", "carol": "casual"},
                )

    def test_short_window_without_contributors_returns_empty_split(self):
        # An empty window is the extreme case of "shorter than four weeks" and
        # must return zeroed counters rather than raising.
        from_date = self.END_DATE - datetime.timedelta(days=2)
        for module in _MODULES:
            with self.subTest(module=module.__name__):
                result = _aggregate(module, self.END_DATE, from_date, [])
                self.assertEqual(result["contributor_detail_list"], [])
                self.assertEqual(result["core_count"], 0)
                self.assertEqual(result["regular_count"], 0)
                self.assertEqual(result["casual_count"], 0)

    def test_long_window_keeps_the_regular_contributor_rule(self):
        # A 28-day window contains four Mondays, so the week-based rule is
        # evaluated again; the 80% split still decides the classifications and
        # nothing raises.
        from_date = self.END_DATE - datetime.timedelta(days=28)
        for module in _MODULES:
            with self.subTest(module=module.__name__):
                result = _aggregate(module, self.END_DATE, from_date, self._simple_records())
                self.assertEqual(result["core_count"], 1)
                self.assertEqual(result["regular_count"], 1)
                self.assertEqual(result["casual_count"], 1)

    def test_default_window_still_returns_split(self):
        # When from_date is omitted the function falls back to its 90-day
        # default, which is long enough for the week-based rule.
        for module in _MODULES:
            with self.subTest(module=module.__name__):
                result = _aggregate(module, self.END_DATE, None, self._simple_records())
                self.assertEqual(result["core_count"], 1)
                self.assertEqual(result["regular_count"], 1)
                self.assertEqual(result["casual_count"], 1)


class ContributionWeeksThresholdTest(TestCase):
    """The shared helper must be explicit about windows that are too short."""

    END_DATE = datetime.date(2024, 5, 15)

    def test_missing_threshold_for_short_windows(self):
        # Zero days, a single day, a week and three weeks do not provide the
        # four Mondays the rule needs, so the threshold has to be None.
        for days in (0, 1, 7, 20):
            from_date = self.END_DATE - datetime.timedelta(days=days)
            for module in _MODULES:
                with self.subTest(module=module.__name__, days=days):
                    self.assertIsNone(
                        module.get_contribution_weeks_threshold(from_date, self.END_DATE)
                    )

    def test_threshold_for_long_enough_windows(self):
        # 28 days contain four Mondays -> 4 * 3/4 = 3.0 weeks.
        self.assertEqual(
            contributor_metrics_v2.get_contribution_weeks_threshold(
                self.END_DATE - datetime.timedelta(days=28), self.END_DATE
            ),
            3.0,
        )
        # 35 days contain five Mondays -> 5 * 3/4 = 3.75 weeks.
        self.assertEqual(
            contributor_metrics_v1.get_contribution_weeks_threshold(
                self.END_DATE - datetime.timedelta(days=35), self.END_DATE
            ),
            3.75,
        )

    def test_threshold_is_none_when_range_is_inverted(self):
        # Defensive case: an end date before the start date covers no weeks.
        for module in _MODULES:
            with self.subTest(module=module.__name__):
                self.assertIsNone(
                    module.get_contribution_weeks_threshold(
                        self.END_DATE + datetime.timedelta(days=1), self.END_DATE
                    )
                )
