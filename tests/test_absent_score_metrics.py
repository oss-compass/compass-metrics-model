from compass_common.algorithm_utils import (
    get_score_by_aggregate_score,
    get_score_by_criticality_score,
)


def test_absent_criticality_metrics_use_existing_missing_value_rules():
    weights = {
        'activity': {'weight': 1, 'threshold': 10},
        'staleness': {'weight': -0.5, 'threshold': 10},
    }
    assert get_score_by_criticality_score({}, weights) == get_score_by_criticality_score(
        {'activity': None, 'staleness': None}, weights
    )


def test_absent_aggregate_metric_is_excluded_from_weighted_average():
    weights = {'present': {'weight': 1}, 'missing': {'weight': 2}}
    assert get_score_by_aggregate_score({'present': 4}, weights) == 4
