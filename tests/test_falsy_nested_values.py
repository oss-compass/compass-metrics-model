from compass_common.dict_utils import deep_get


def test_existing_falsy_values_are_not_replaced_by_default():
    data = {'metrics': {'count': 0, 'enabled': False, 'names': [], 'details': {}}}
    for key, expected in (('count', 0), ('enabled', False), ('names', []), ('details', {})):
        assert deep_get(data, ['metrics', key], 'missing') == expected
    assert deep_get(data, ['metrics', 'absent'], 'missing') == 'missing'
    assert deep_get(data, ['metrics', 'count', 'nested'], 'missing') == 'missing'
