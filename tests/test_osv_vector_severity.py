import json
import unittest

from compass_metrics_v2.supply_chain_security_metrics_v2 import (
    _calc_security_vulnerability,
    _osv_severity_bucket,
)


V3_CRITICAL = 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'
V3_HIGH = 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N'
V4_CRITICAL = 'CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:N'


class OsvVectorSeverityTests(unittest.TestCase):
    def test_osv_vector_versions(self):
        for kind, vector, expected in [
            ('CVSS_V2', 'AV:N/AC:L/Au:N/C:P/I:P/A:P', 'HIGH'),
            ('CVSS_V3', V3_CRITICAL, 'CRITICAL'),
            ('CVSS_V3', V3_HIGH, 'HIGH'),
            ('CVSS_V4', V4_CRITICAL, 'CRITICAL'),
        ]:
            with self.subTest(kind=kind, vector=vector):
                self.assertEqual(_osv_severity_bucket({
                    'severity': [{'type': kind, 'score': vector}],
                }), expected)

    def test_existing_numeric_scores(self):
        for score, expected in [('9.8', 'CRITICAL'), (7.5, 'HIGH'), ('5.0', 'MEDIUM')]:
            with self.subTest(score=score):
                self.assertEqual(_osv_severity_bucket({'severity': [{'score': score}]}), expected)

    def test_invalid_entries_do_not_hide_later_valid_vector(self):
        self.assertEqual(_osv_severity_bucket({'severity': [
            None, {'type': 'CVSS_V3', 'score': 'CVSS:3.1/AV:invalid'},
            {'type': 'CVSS_V3', 'score': V3_CRITICAL},
        ]}), 'CRITICAL')

    def test_unknown_data_keeps_fallback(self):
        for severity in [[], [{'score': None}], [{'type': 'Ubuntu', 'score': 'high'}]]:
            with self.subTest(severity=severity):
                self.assertEqual(_osv_severity_bucket({'severity': severity}), 'UNKNOWN')

    def test_scanner_payload_reports_critical_and_high(self):
        result = _calc_security_vulnerability({'results': [{'packages': [{
            'vulnerabilities': [
                {'id': 'EXAMPLE-1', 'severity': [{'type': 'CVSS_V3', 'score': V3_CRITICAL}]},
                {'id': 'EXAMPLE-2', 'severity': [{'type': 'CVSS_V3', 'score': V3_HIGH}]},
                {'id': 'EXAMPLE-3'},
            ],
        }]}]})
        self.assertEqual(result['vuln_counts'], {'critical': 1, 'high': 1, 'medium': 1, 'total_unique': 3})
        self.assertEqual(json.loads(result['security_vulnerability_detail'])['critical'], 1)
        self.assertEqual(result['security_vulnerability'], 7)


if __name__ == '__main__':
    unittest.main()
