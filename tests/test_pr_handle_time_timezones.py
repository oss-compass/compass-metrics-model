import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from compass_metrics_v2.pr_metrics_v2 import pr_new_handle_time_by_period


class PrHandleTimeTimezoneTests(unittest.TestCase):
    def test_equivalent_offset_timestamps_have_zero_elapsed_time(self):
        items = [{"_source": {
            "grimoire_creation_date": "2024-02-10T12:00:00+08:00",
            "state": "merged",
            "merged_at": "2024-02-10T13:00:00+09:00",
        }}]
        with patch("compass_metrics_v2.pr_metrics_v2.get_all_index_data", return_value=items):
            result = pr_new_handle_time_by_period(
                object(), "prs", datetime(2024, 3, 15, tzinfo=timezone.utc), ["repo"])

        self.assertEqual(result["pr_new_handle_time_avg"], 0)
        self.assertEqual(result["pr_new_handle_time_mid"], 0)

    def test_z_and_offset_timestamps_use_same_clock(self):
        items = [{"_source": {
            "grimoire_creation_date": "2024-02-10T10:00:00Z",
            "state": "closed",
            "closed_at": "2024-02-10T12:00:00+01:00",
        }}]
        with patch("compass_metrics_v2.pr_metrics_v2.get_all_index_data", return_value=items):
            result = pr_new_handle_time_by_period(
                object(), "prs", datetime(2024, 3, 15, tzinfo=timezone.utc), ["repo"])

        self.assertAlmostEqual(result["pr_new_handle_time_avg"], 1 / 24)
        self.assertAlmostEqual(result["pr_new_handle_time_mid"], 1 / 24)


if __name__ == "__main__":
    unittest.main()
