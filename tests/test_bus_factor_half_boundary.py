from datetime import datetime

from compass_metrics_v2 import contributor_metrics_v2


def test_one_of_two_equal_contributors_reaches_half(monkeypatch):
    contributors = [
        {"is_bot": False, "id_git_author_name_list": [name], "code_author_date_list": ["2026-03-01"] * 5}
        for name in ("alice", "bob")
    ]
    monkeypatch.setattr(contributor_metrics_v2, "get_contributor_list", lambda *_args: contributors)

    result = contributor_metrics_v2.bus_factor(None, "contributors", datetime(2026, 4, 1), ["repo"])
    assert result == {"bus_factor": 1}


def test_zero_contributions_do_not_count_as_bus_factor(monkeypatch):
    contributors = [{"is_bot": False, "id_git_author_name_list": ["alice"], "code_author_date_list": []}]
    monkeypatch.setattr(contributor_metrics_v2, "get_contributor_list", lambda *_args: contributors)

    result = contributor_metrics_v2.bus_factor(None, "contributors", datetime(2026, 4, 1), ["repo"])
    assert result == {"bus_factor": 0}
