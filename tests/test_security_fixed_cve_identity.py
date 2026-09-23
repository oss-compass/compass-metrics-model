from unittest.mock import patch

from compass_metrics.security import security_vul_fixed


def _scan(date, *cves):
    return {"_source": {
        "grimoire_creation_date": date,
        "security": [{"package_name": "dependency", "vulnerabilities": [
            {"aliases": [cve], "severity": "HIGH"} for cve in cves
        ]}]
    }}


def test_fixed_count_uses_cve_identity_when_totals_are_unchanged():
    latest = _scan("2025-02-01", "CVE-B", "CVE-C")
    earliest = _scan("2025-01-01", "CVE-A", "CVE-B")
    with patch("compass_metrics.security.get_all_index_data", side_effect=[[latest, earliest], [earliest]]):
        result = security_vul_fixed(None, "index", "v1", ["repo"])

    assert result["security_vul_fixed"] == 1
    assert result["security_vul_unfixed"] == 2


def test_new_vulnerabilities_do_not_count_as_fixed():
    latest = _scan("2025-02-01", "CVE-A", "CVE-B")
    earliest = _scan("2025-01-01", "CVE-A")
    with patch("compass_metrics.security.get_all_index_data", side_effect=[[latest, earliest], [earliest]]):
        result = security_vul_fixed(None, "index", "v1", ["repo"])

    assert result["security_vul_fixed"] == 0
    assert result["security_vul_unfixed"] == 2
