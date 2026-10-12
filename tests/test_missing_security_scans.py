"""An absent or failed security scan is not evidence for a perfect score."""

import unittest
from unittest.mock import Mock

from compass_metrics.opencheck_metrics import binary_artifacts, vulnerabilities


def scan_client(*results):
    client = Mock()
    client.search.side_effect = [
        {"hits": {"hits": [] if result is None else [
            {"_source": {"command_result": result}}]}}
        for result in results
    ]
    return client


class MissingSecurityScansTest(unittest.TestCase):
    def test_absent_scans_are_unscored(self):
        for metric in (binary_artifacts, vulnerabilities):
            with self.subTest(metric=metric.__name__):
                result = metric(scan_client(None), "scans", ["repo"])
                self.assertIsNone(result[metric.__name__])

    def test_failed_or_incomplete_scans_are_unscored(self):
        for metric, field in ((binary_artifacts, "binary_file_list"),
                              (vulnerabilities, "results")):
            for scan in ({}, {"error": "scanner failed"},
                         {"error": "partial scan", field: []},
                         {field: None}, {field: "not a list"}):
                with self.subTest(metric=metric.__name__, scan=scan):
                    result = metric(scan_client(scan), "scans", ["repo"])
                    self.assertIsNone(result[metric.__name__])

    def test_successful_empty_scans_still_score_ten(self):
        for metric, field in ((binary_artifacts, "binary_file_list"),
                              (vulnerabilities, "results")):
            with self.subTest(metric=metric.__name__):
                result = metric(scan_client({field: []}), "scans", ["repo"])
                self.assertEqual(result[metric.__name__], 10)

    def test_binary_scan_requires_coverage_of_every_repository(self):
        result = binary_artifacts(scan_client({"binary_file_list": ["app.exe"]}, None),
                                  "scans", ["one", "two"])
        self.assertIsNone(result["binary_artifacts"])
        self.assertEqual(result["binary_artifacts_detail"], ["app.exe"])

    def test_complete_binary_scans_keep_existing_penalties(self):
        result = binary_artifacts(scan_client({"binary_file_list": ["app.exe", "README"]},
                                              {"binary_file_list": ["lib.so"]}),
                                  "scans", ["one", "two"])
        self.assertEqual(result["binary_artifacts"], 8)
        self.assertCountEqual(result["binary_artifacts_detail"], ["app.exe", "lib.so"])

    def test_vulnerability_penalties_still_deduplicate_ids(self):
        result = vulnerabilities(scan_client({"results": [{"packages": [
            {"package": {"name": "one"}, "vulnerabilities": [{"id": "CVE-1"}]},
            {"package": {"name": "two"}, "vulnerabilities": [{"id": "CVE-1"}, {"id": "CVE-2"}]},
        ]}]}), "scans", ["repo"])
        self.assertEqual(result["vulnerabilities"], 8)
        self.assertEqual(len(result["vulnerabilities_detail"]), 2)


if __name__ == "__main__":
    unittest.main()
