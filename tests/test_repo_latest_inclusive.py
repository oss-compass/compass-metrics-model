from datetime import datetime
from unittest.mock import Mock

from compass_metrics_v2.repo_metrics_v2 import get_latest_count


def test_latest_count_includes_snapshot_at_the_cutoff():
    client = Mock()
    client.search.return_value = {"aggregations": {"by_repo": {"buckets": []}}}
    cutoff = datetime(2026, 5, 31, 23, 59, 59, 999999)

    assert get_latest_count(client, "stars", ["repo"], cutoff) == 0
    query = client.search.call_args.kwargs["body"]
    assert query["query"]["bool"]["filter"][1] == {
        "range": {"grimoire_creation_date": {"lte": cutoff.isoformat()}}
    }
