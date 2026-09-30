import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from compass_metrics.issue_metrics import time_to_close


class TestIssueMetrics(unittest.TestCase):

    @patch("compass_metrics.issue_metrics.get_all_index_data")
    def test_time_to_close_empty_items(self, mock_get_data):
        mock_client = MagicMock()
        mock_get_data.return_value = []
        test_date = datetime(2025, 3, 1, 0, 0, 0)

        result = time_to_close(mock_client, "test_issue_index", test_date, ["repo1"])
        self.assertIsNone(result["time_to_close_avg"])
        self.assertIsNone(result["time_to_close_mid"])

    @patch("compass_metrics.issue_metrics.get_all_index_data")
    def test_time_to_close_items_without_state_no_zero_division(self, mock_get_data):
        """Verify that items without 'state' field do not cause ZeroDivisionError."""
        mock_client = MagicMock()
        mock_get_data.return_value = [
            {"_source": {"id": 1, "created_at": "2025-01-01T00:00:00"}},
            {"_source": {"id": 2, "created_at": "2025-01-02T00:00:00"}},
        ]
        test_date = datetime(2025, 3, 1, 0, 0, 0)

        result = time_to_close(mock_client, "test_issue_index", test_date, ["repo1"])
        self.assertIsNone(result["time_to_close_avg"])
        self.assertIsNone(result["time_to_close_mid"])

    @patch("compass_metrics.issue_metrics.get_all_index_data")
    def test_time_to_close_normal_data(self, mock_get_data):
        mock_client = MagicMock()
        mock_get_data.return_value = [
            {
                "_source": {
                    "state": "closed",
                    "created_at": "2025-01-01T00:00:00",
                    "closed_at": "2025-01-11T00:00:00",
                }
            },
            {
                "_source": {
                    "state": "closed",
                    "created_at": "2025-01-01T00:00:00",
                    "closed_at": "2025-01-21T00:00:00",
                }
            },
        ]
        test_date = datetime(2025, 3, 1, 0, 0, 0)

        result = time_to_close(mock_client, "test_issue_index", test_date, ["repo1"])
        self.assertEqual(result["time_to_close_avg"], 15.0)
        self.assertEqual(result["time_to_close_mid"], 15.0)


if __name__ == "__main__":
    unittest.main()
