import unittest
from datetime import date
from unittest.mock import patch

from compass_metrics.contributor_metrics import contributor_detail_list


class ContributorDetailListTest(unittest.TestCase):
    def test_short_analysis_window_does_not_use_an_uninitialized_week_threshold(self):
        contributors = [{
            "contributor": "alice",
            "contribution": 1,
            "contribution_without_observe": 1,
            "ecological_type": "individual participant",
            "organization": None,
            "contribution_type_list": [],
            "is_bot": False,
            "repo_name": "example/repo",
        }]

        with patch("compass_metrics.contributor_metrics.get_contributor_list", return_value=contributors):
            result = contributor_detail_list(
                client=None,
                contributors_enriched_index="contributors",
                date=date(2026, 7, 12),
                repo_list=["example/repo"],
                from_date=date(2026, 7, 11),
            )

        self.assertEqual(result["core_count"], 1)
        self.assertEqual(result["regular_count"], 0)
        self.assertEqual(result["casual_count"], 0)


if __name__ == "__main__":
    unittest.main()
