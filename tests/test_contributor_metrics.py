import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from compass_metrics.contributor_metrics import pr_review_contributor_count


class TestContributorMetrics(unittest.TestCase):

    @patch("compass_metrics.contributor_metrics.get_contributor_count")
    def test_pr_review_contributor_count_keys_and_values(self, mock_get_count):
        """Verify that pr_review_contributor_count returns both bot and without_bot keys without overwriting."""
        mock_client = MagicMock()
        test_date = datetime(2025, 3, 1, 0, 0, 0)

        # Returns different values for total, bot, without_bot calls
        mock_get_count.side_effect = [15, 3, 12]

        result = pr_review_contributor_count(
            mock_client, "test_contributors_index", test_date, ["repo1"]
        )

        self.assertIn("pr_review_contributor_count", result)
        self.assertIn("pr_review_contributor_count_bot", result)
        self.assertIn("pr_review_contributor_count_without_bot", result)

        self.assertEqual(result["pr_review_contributor_count"], 15)
        self.assertEqual(result["pr_review_contributor_count_bot"], 3)
        self.assertEqual(result["pr_review_contributor_count_without_bot"], 12)


if __name__ == "__main__":
    unittest.main()
