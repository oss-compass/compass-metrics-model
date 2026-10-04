from datetime import datetime, timezone
import json

import pytest

from compass_metrics import db_dsl


@pytest.mark.parametrize("make_query", [
    lambda: db_dsl.get_updated_since_query(["repo"]),
    lambda: db_dsl.get_recent_releases_uuid_count(["repo"]),
    lambda: db_dsl.get_uuid_count_query("cardinality", ["repo"], "uuid"),
    lambda: db_dsl.get_pr_closed_uuid_count("cardinality", ["repo"], "uuid"),
    lambda: db_dsl.get_pr_message_count(["repo"], "uuid"),
    lambda: db_dsl.get_pr_linked_issue_count("repo"),
    lambda: db_dsl.get_message_list_query(),
    lambda: db_dsl.get_updated_issues_count_query(["repo"]),
])
def test_default_end_date_is_resolved_when_query_is_built(monkeypatch, make_query):
    monkeypatch.setattr(db_dsl, "datetime_utcnow", lambda: datetime(2030, 1, 2, tzinfo=timezone.utc))
    assert "2030-01-02" in json.dumps(make_query())
