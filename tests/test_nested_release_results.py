from compass_metrics_v2.supply_chain_security_metrics_v2 import (
    _calc_lifecycle_release_note,
    _calc_security_package_sig,
)


def test_nested_release_results_contribute_to_signature_and_note_scores():
    result = {
        'signed-release-checker': {'signed_files': [
            {'tag': 'v1', 'signature_files': ['app.sig']},
        ]},
        'notes': {'release_contents': [
            {'tag': 'v1', 'has_content': True, 'content_files': ['CHANGELOG.md']},
        ]},
    }
    assert _calc_security_package_sig(result)['security_package_sig'] == 10
    assert _calc_lifecycle_release_note(result)['lifecycle_release_note'] == 10


def test_nested_release_errors_are_not_scored_as_missing_assets():
    assert _calc_security_package_sig({'signed-release-checker': {'error': 'API unavailable'}})[
        'security_package_sig'
    ] == -1
    assert _calc_lifecycle_release_note({'notes': {'error': 'API unavailable'}})[
        'lifecycle_release_note'
    ] == -1
