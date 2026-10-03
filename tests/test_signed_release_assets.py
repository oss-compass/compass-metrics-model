from unittest.mock import patch

from compass_metrics.opencheck_metrics import signed_releases


def test_asc_and_sig_assets_count_as_signed_releases():
    scan = {'_source': {'command_result': {'signed-release-checker': {'signed_files': [
        {'release_name': 'v1', 'signature_files': ['package.asc']},
        {'release_name': 'v2', 'signature_files': ['package.SIG']},
        {'release_name': 'v3', 'signature_files': ['package.asc.txt']},
    ]}}}}
    with patch('compass_metrics.opencheck_metrics.get_openchecker_data', return_value=scan):
        result = signed_releases(None, 'index', ['https://github.com/example/repo'])

    assert result['signed_releases'] == 6
    assert result['signed_releases_detail']['signed_release_list'] == ['v1', 'v2']
