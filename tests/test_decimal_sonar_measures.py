import json

from compass_metrics_v2.supply_chain_security_metrics_v2 import _calc_ecology_test_coverage


def test_decimal_sonar_percentages_are_scored_and_preserved():
    scan = {'component': {'measures': [
        {'metric': 'duplicated_lines_density', 'value': '2.5'},
        {'metric': 'coverage', 'value': '79.5'},
    ]}}

    result = _calc_ecology_test_coverage(scan)

    assert result['ecology_test_coverage'] == 9
    assert result['test_coverage_percent'] == 79.5
    detail = json.loads(result['ecology_test_coverage_detail'])
    assert detail['duplication_ratio'] == 2.5
    assert detail['coverage_ratio'] == 79.5


def test_missing_measure_value_does_not_receive_a_zero_duplication_bonus():
    result = _calc_ecology_test_coverage({'component': {'measures': [
        {'metric': 'duplicated_lines_density'},
    ]}})
    assert result['ecology_test_coverage'] == 0
