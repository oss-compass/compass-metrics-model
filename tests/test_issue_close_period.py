from datetime import datetime

from compass_metrics_v2.issue_metrics_v2 import issue_closed_count_by_period


class SearchClient:
    def __init__(self):
        self.query = None

    def search(self, *, index, body):
        self.query = body
        return {"aggregations": {"count_of_uuid": {"value": 3}}}


def test_closed_issue_count_uses_close_date_and_includes_period_last_day():
    client = SearchClient()
    result = issue_closed_count_by_period(client, "issues", datetime(2026, 2, 15), ["repo"])

    assert result["issue_closed_count"] == 3
    date_range = client.query["query"]["bool"]["filter"][0]["range"]
    assert date_range == {"closed_at": {"gte": "2026-02-01", "lt": "2026-03-01"}}
