from compass_metrics_v2.supply_chain_security_metrics_v2 import (
    _calc_compliance_copyright_statement,
    _calc_compliance_license,
)


def test_license_violation_count_is_not_ignored_when_details_are_empty():
    result = _calc_compliance_license(
        {"files": []}, {}, {"total_count": 2, "details": []}
    )
    assert result["compliance_license"] == 0


def test_copyright_violation_count_is_not_ignored_when_details_are_empty():
    scancode = {"files": [{"path": "repo/main.py", "type": "file", "copyrights": []}]}
    result = _calc_compliance_copyright_statement(
        scancode, {}, None, {"total_count": 1, "details": []}
    )
    assert result["compliance_copyright_statement"] == 0


def test_zero_violations_still_receive_full_credit():
    assert _calc_compliance_license(
        {"files": []}, {}, {"total_count": 0, "details": []}
    )["compliance_license"] == 10
    assert _calc_compliance_copyright_statement(
        {"files": []}, {}, None, {"total_count": 0, "details": []}
    )["compliance_copyright_statement"] == 10
