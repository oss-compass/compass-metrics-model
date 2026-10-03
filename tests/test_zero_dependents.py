from unittest.mock import patch

from compass_metrics.opencheck_metrics import dependents_count


def test_zero_dependents_remains_a_measured_zero():
    with patch('compass_metrics.opencheck_metrics.get_openchecker_data', return_value={
        '_source': {'command_result': {'bedependent': 0}},
    }):
        assert dependents_count(None, 'index', ['https://github.com/example/repo']) == {'dependents_count': 0}


def test_boolean_placeholder_is_not_a_count():
    with patch('compass_metrics.opencheck_metrics.get_openchecker_data', return_value={
        '_source': {'command_result': {'bedependent': False}},
    }):
        assert dependents_count(None, 'index', ['https://github.com/example/repo']) == {'dependents_count': None}
