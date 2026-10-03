from unittest.mock import patch

from compass_metrics.opencheck_metrics import token_permissions


def test_top_level_contents_write_reduces_score():
    scan = {'_source': {'command_result': {
        'num_workflows': 1,
        'token_permissions': [{
            'file_path': '.github/workflows/build.yml',
            'location_type': 'top',
            'name': 'contents',
            'value': 'write',
            'permission_level': 'write',
        }],
    }}}
    with patch('compass_metrics.opencheck_metrics.get_openchecker_data', return_value=scan):
        result = token_permissions(None, 'index', ['https://github.com/example/repo'])

    assert result['token_permissions'] == 0
