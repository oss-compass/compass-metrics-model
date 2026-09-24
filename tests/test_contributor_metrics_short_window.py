"""Regression tests for the contributor mileage split on short analysis windows.

``contributor_detail_list()`` splits the contributors of an analysis window into the
core/regular/casual groups described by the CHAOSS contributor metrics model.  The regular group
is built from two rules: the contributors that cover the next 30% of the contribution, and the
contributors that were active in 3/4 of the weeks covered by the window.

The second rule needs the window to span a few weeks.  The implementation used to only bind the
threshold inside an ``if len(date_list) >= 4`` guard while the loop below read the name
unconditionally, so every window holding fewer than four Mondays - a one-day "last 7 days" style
view, a single week, or three weeks - aborted with ``UnboundLocalError`` before the
core/regular/casual split was returned.  The default 90 days window (13 Mondays) happened to
work, which is why the defect stayed hidden.

These tests pin the fixed behaviour for the v2 module and for the v1 copy that is still wired into
the metrics model switch:

* short windows return the full split instead of raising,
* the threshold helper reports "not applicable" for short and for inverted windows,
* the 3/4 rule still classifies a weekly active contributor as regular on longer windows,
* the public helpers that forward a caller supplied window keep working.
"""

import datetime
import os
import sys
import unittest
from unittest import mock

# Make the repository root importable no matter how the tests are launched (unittest discover,
# plain pytest, or ``python -m pytest`` from another working directory).
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from compass_metrics import contributor_metrics
from compass_metrics_v2 import contributor_metrics_v2


# 2025-03-10 is a Monday.  Every window below is anchored on it so that the number of covered
# Mondays is easy to reason about:
#   2025-03-07 .. 2025-03-10 -> 1 Monday   (shorter than four weeks)
#   2025-02-24 .. 2025-03-10 -> 3 Mondays  (shorter than four weeks)
#   2025-02-17 .. 2025-03-10 -> 4 Mondays  (the first window where the rule applies)
#   2024-12-10 .. 2025-03-10 -> 13 Mondays (the default 90 days window)
TO_DATE = datetime.date(2025, 3, 10)
ONE_DAY_FROM_DATE = datetime.date(2025, 3, 7)
THREE_WEEK_FROM_DATE = datetime.date(2025, 2, 24)
FOUR_WEEK_FROM_DATE = datetime.date(2025, 2, 17)
LONG_FROM_DATE = datetime.date(2024, 12, 10)

ENRICHED_INDEX = "contributors_enriched"
REPO_LIST = ["https://github.com/example/demo"]
SPLIT_KEYS = {"contributor_detail_list", "core_count", "regular_count", "casual_count"}


def make_record(contributor, contribution, ecological_type="individual participant",
                organization=None, is_bot=False, repo_name="example/demo",
                contribution_type="code_author"):
    """ Build one raw contributors_enriched document, as consumed by the split helper. """
    return {
        "contributor": contributor,
        "contribution": contribution,
        "contribution_without_observe": contribution,
        "ecological_type": ecological_type,
        "organization": organization,
        "is_bot": is_bot,
        "repo_name": repo_name,
        "contribution_type_list": [
            {"contribution_type": contribution_type, "contribution": contribution}
        ],
    }


def weekly_active_records(contributor="weekly", contribution=1, weeks=10):
    """ Records of a contributor that shows up in ``weeks`` different weeks. """
    return [make_record(contributor, contribution) for _ in range(weeks)]


def call_detail_list(module, records, from_date, to_date=TO_DATE, filter_mileage=None):
    """ Run contributor_detail_list with the OpenSearch lookup replaced by ``records``. """
    with mock.patch.object(module, "get_contributor_list", return_value=records):
        return module.contributor_detail_list(None, ENRICHED_INDEX, to_date, REPO_LIST,
                                             from_date=from_date, filter_mileage=filter_mileage)


class MileageSplitContract(object):
    """ Checks shared by the v1 and the v2 implementations of the mileage split. """

    module = None

    def assert_split(self, result, core, regular, casual):
        self.assertEqual(set(result.keys()), SPLIT_KEYS)
        self.assertEqual(result["core_count"], core)
        self.assertEqual(result["regular_count"], regular)
        self.assertEqual(result["casual_count"], casual)
        self.assertEqual(len(result["contributor_detail_list"]), core + regular + casual)

    def mileage_of(self, result):
        return {item["contributor"]: item["mileage_type"] for item in result["contributor_detail_list"]}

    def test_one_day_window_returns_split_instead_of_raising(self):
        result = call_detail_list(self.module, [make_record("alice", 5)], ONE_DAY_FROM_DATE)
        self.assert_split(result, 1, 0, 0)
        self.assertEqual(self.mileage_of(result), {"alice": "core"})

    def test_three_week_window_returns_split_instead_of_raising(self):
        records = [make_record("alice", 8), make_record("bob", 2)]
        result = call_detail_list(self.module, records, THREE_WEEK_FROM_DATE)
        self.assert_split(result, 1, 0, 1)
        self.assertEqual(self.mileage_of(result), {"alice": "core", "bob": "casual"})

    def test_empty_contributor_list_returns_empty_split(self):
        result = call_detail_list(self.module, [], ONE_DAY_FROM_DATE)
        self.assert_split(result, 0, 0, 0)
        self.assertEqual(result["contributor_detail_list"], [])

    def test_weekly_active_contributor_is_regular_on_long_window(self):
        records = [make_record("big", 100)] + weekly_active_records()
        result = call_detail_list(self.module, records, LONG_FROM_DATE)
        self.assert_split(result, 1, 1, 0)
        self.assertEqual(self.mileage_of(result), {"big": "core", "weekly": "regular"})
        weekly = [item for item in result["contributor_detail_list"] if item["contributor"] == "weekly"][0]
        self.assertEqual(weekly["contribution_weeks"], 10)

    def test_weekly_active_contributor_is_casual_when_rule_cannot_be_applied(self):
        records = [make_record("big", 100)] + weekly_active_records()
        result = call_detail_list(self.module, records, ONE_DAY_FROM_DATE)
        self.assert_split(result, 1, 0, 1)
        self.assertEqual(self.mileage_of(result), {"big": "core", "weekly": "casual"})

    def test_default_window_returns_split(self):
        with mock.patch.object(self.module, "get_contributor_list", return_value=[make_record("alice", 5)]):
            result = self.module.contributor_detail_list(None, ENRICHED_INDEX, TO_DATE, REPO_LIST)
        self.assert_split(result, 1, 0, 0)

    def test_inverted_window_returns_split_instead_of_raising(self):
        result = call_detail_list(self.module, [make_record("alice", 5)], TO_DATE, to_date=ONE_DAY_FROM_DATE)
        self.assert_split(result, 1, 0, 0)

    def test_threshold_helper_bounds(self):
        self.assertEqual(self.module.MIN_WEEKS_FOR_REGULAR_CONTRIBUTOR_RULE, 4)
        threshold = self.module.get_contribution_weeks_threshold
        self.assertIsNone(threshold(ONE_DAY_FROM_DATE, TO_DATE))
        self.assertIsNone(threshold(THREE_WEEK_FROM_DATE, TO_DATE))
        self.assertEqual(threshold(FOUR_WEEK_FROM_DATE, TO_DATE), 3.0)
        self.assertEqual(threshold(LONG_FROM_DATE, TO_DATE), 13 * 3 / 4)
        self.assertIsNone(threshold(TO_DATE, ONE_DAY_FROM_DATE))


class ContributorMetricsV2ShortWindowTest(MileageSplitContract, unittest.TestCase):
    module = contributor_metrics_v2


class ContributorMetricsV1ShortWindowTest(MileageSplitContract, unittest.TestCase):
    module = contributor_metrics


class ForwardedWindowTest(unittest.TestCase):
    """ The public helpers forward a caller supplied window to the split helper. """

    def test_v2_contribution_distribution_with_one_day_window(self):
        records = [make_record("alice", 8),
                   make_record("bob", 2, ecological_type="organization participant", organization="Acme")]
        with mock.patch.object(contributor_metrics_v2, "get_contributor_list", return_value=records):
            result = contributor_metrics_v2.contribution_distribution(None, ENRICHED_INDEX, TO_DATE, REPO_LIST,
                                                                     from_date=ONE_DAY_FROM_DATE)
        data = result["contribution_distribution"]
        self.assertIsNotNone(data)
        self.assertEqual(data["total_contribution"], 10)

    def test_v2_organization_distribution_with_one_day_window(self):
        records = [make_record("alice", 8, organization="Acme")]
        with mock.patch.object(contributor_metrics_v2, "get_contributor_list", return_value=records):
            result = contributor_metrics_v2.organization_distribution(None, ENRICHED_INDEX, TO_DATE, REPO_LIST,
                                                                     from_date=ONE_DAY_FROM_DATE)
        data = result["organization_distribution"]
        self.assertIsNotNone(data)
        self.assertEqual(data["total_contribution"], 8)
        self.assertIn("Acme", data)

    def test_v2_contributor_distribution_with_one_day_window(self):
        records = [make_record("alice", 8)]
        with mock.patch.object(contributor_metrics_v2, "get_contributor_list", return_value=records):
            result = contributor_metrics_v2.contributor_distribution(None, ENRICHED_INDEX, TO_DATE, REPO_LIST,
                                                                    from_date=ONE_DAY_FROM_DATE)
        self.assertIsNotNone(result["contributor_distribution"])

    def test_v1_contribution_distribution_with_one_day_window(self):
        records = [make_record("alice", 8)]
        with mock.patch.object(contributor_metrics, "get_contributor_list", return_value=records):
            result = contributor_metrics.contribution_distribution(None, ENRICHED_INDEX, TO_DATE, REPO_LIST,
                                                                  from_date=ONE_DAY_FROM_DATE)
        self.assertIsNotNone(result["contribution_distribution"])

    def test_v2_mileage_filter_on_short_window(self):
        records = [make_record("alice", 8), make_record("bob", 2)]
        core_only = call_detail_list(contributor_metrics_v2, records, ONE_DAY_FROM_DATE, filter_mileage="core")
        self.assertEqual([item["contributor"] for item in core_only["contributor_detail_list"]], ["alice"])
        casual_only = call_detail_list(contributor_metrics_v2, records, ONE_DAY_FROM_DATE, filter_mileage="casual")
        self.assertEqual([item["contributor"] for item in casual_only["contributor_detail_list"]], ["bob"])


if __name__ == "__main__":
    unittest.main()
