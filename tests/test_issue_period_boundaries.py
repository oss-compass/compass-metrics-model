import unittest
from datetime import datetime

from compass_metrics_v2.issue_metrics_v2 import (
    get_period_range,
    get_previous_period_range,
    issue_new_and_closed_count_by_period,
    issue_new_count_by_period,
)


class RecordingClient:
    def __init__(self):
        self.body = None

    def search(self, index, body):
        self.body = body
        return {"aggregations": {"count_of_uuid": {"value": 1}}}


class IssuePeriodBoundaryTests(unittest.TestCase):
    def test_current_period_has_exclusive_next_period_boundary(self):
        cases = [
            ("month", datetime(2024, 2, 15, 12, 30), datetime(2024, 2, 1), datetime(2024, 3, 1)),
            ("quarter", datetime(2024, 11, 15, 12, 30), datetime(2024, 10, 1), datetime(2025, 1, 1)),
            ("year", datetime(2024, 5, 15, 12, 30), datetime(2024, 1, 1), datetime(2025, 1, 1)),
        ]
        for period, end_date, expected_start, expected_end in cases:
            with self.subTest(period=period):
                self.assertEqual(get_period_range(end_date, period), (expected_start, expected_end))

                client = RecordingClient()
                issue_new_count_by_period(client, "issues", end_date, ["repo"], period)
                self.assertEqual(client.body["query"]["bool"]["filter"][0]["range"]
                                 ["grimoire_creation_date"],
                                 {"gte": expected_start.strftime("%Y-%m-%d"),
                                  "lt": expected_end.strftime("%Y-%m-%d")})

    def test_previous_month_includes_its_last_day(self):
        start, end = get_previous_period_range(datetime(2024, 3, 15), "month")
        self.assertEqual((start, end), (datetime(2024, 2, 1), datetime(2024, 3, 1)))

    def test_created_and_closed_uses_same_exclusive_boundary(self):
        client = RecordingClient()
        issue_new_and_closed_count_by_period(
            client, "issues", datetime(2024, 2, 15, 12, 30), ["repo"])
        closed_range = client.body["query"]["bool"]["filter"][-1]["range"]["closed_at"]
        self.assertEqual(closed_range, {"gte": "2024-02-01", "lt": "2024-03-01"})


if __name__ == "__main__":
    unittest.main()
