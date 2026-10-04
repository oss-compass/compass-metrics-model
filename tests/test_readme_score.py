from compass_metrics_v2.supply_chain_security_metrics_v2 import _calc_ecology_readme


def test_missing_readme_does_not_receive_full_score():
    assert _calc_ecology_readme({}, None)['ecology_readme'] == 0
    assert _calc_ecology_readme({'readme_file': ['repo/OTHER.md']}, None)['ecology_readme'] == 0


def test_repository_readme_scores_unless_audit_reports_it_missing():
    result = {'readme_file': ['repo/README.md']}
    assert _calc_ecology_readme(result, None)['ecology_readme'] == 10
    assert _calc_ecology_readme(result, {'total_count': 1})['ecology_readme'] == 0
