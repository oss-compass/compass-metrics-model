from datetime import datetime

from compass_metrics_v2 import contributor_metrics_v2


def test_short_period_keeps_contribution_record_count(monkeypatch):
    records = [
        {
            "contributor": "alice", "contribution": 1, "contribution_without_observe": 1,
            "ecological_type": "individual participant", "organization": None,
            "is_bot": False, "repo_name": "repo", "contribution_type_list": [],
        }
        for _ in range(2)
    ]
    monkeypatch.setattr(contributor_metrics_v2, "get_contributor_list", lambda *_args: records)

    result = contributor_metrics_v2.contributor_detail_list(
        None, "contributors", datetime(2026, 1, 9), ["repo"], from_date=datetime(2026, 1, 1)
    )

    assert result["core_count"] == 1
    assert result["contributor_detail_list"][0]["contribution_weeks"] == 2
