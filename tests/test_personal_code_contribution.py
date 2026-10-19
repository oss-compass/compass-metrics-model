"""Native search regressions for unknown-organization personal Git contributions.

Use COMPASS_TEST_SEARCH_URL with a disposable OpenSearch service. The default
upstream integer-total issue must be fixed separately for Elasticsearch 6;
the fork's verification workflow also tests an actual merge with that fix.
Only uniquely named test indices created by this suite are deleted.
"""

import json
import os
import unittest
from datetime import datetime
from uuid import uuid4

from compass_metrics_v2 import git_metrics_v2 as metrics


URL = os.environ.get("COMPASS_TEST_SEARCH_URL")
CLIENT = os.environ.get("COMPASS_TEST_SEARCH_CLIENT", "opensearch")
DATE = datetime(2026, 1, 20)
REPO = "https://github.com/example/project"
MISSING = object()


def commit(lines, organization=MISSING, **overrides):
    row = {
        "tag": REPO + ".git", "grimoire_creation_date": "2026-01-15T12:00:00",
        "lines_added": lines, "lines_removed": 0,
    }
    if organization is not MISSING:
        row["author_org_name"] = organization
    row.update(overrides)
    return row


@unittest.skipUnless(URL, "requires COMPASS_TEST_SEARCH_URL for a disposable search service")
class PersonalCodeContributionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if CLIENT == "elasticsearch":
            from elasticsearch import Elasticsearch
            cls.client = Elasticsearch(URL)
        elif CLIENT == "opensearch":
            from opensearchpy import OpenSearch
            cls.client = OpenSearch(URL)
        else:
            raise ValueError("unknown COMPASS_TEST_SEARCH_CLIENT: " + CLIENT)
        print("Live personal-contribution search:", cls.client.info()["version"]["number"], "client:", CLIENT)

    def setUp(self):
        self.index = None

    def create_index(self, keyword=False):
        self.assertIsNone(self.index)
        self.index = "compass-personal-lines-test-" + uuid4().hex
        organization = {"type": "keyword"} if keyword else {
            "type": "text", "fields": {"keyword": {"type": "keyword"}},
        }
        mapping = {"properties": {
            "tag": {"type": "keyword"}, "grimoire_creation_date": {"type": "date"},
            "lines_added": {"type": "long"}, "lines_removed": {"type": "long"},
            "author_org_name": organization,
        }}
        if CLIENT == "elasticsearch":
            mapping = {"_doc": mapping}
        self.client.indices.create(index=self.index, body={
            "settings": {"number_of_shards": 1, "number_of_replicas": 0}, "mappings": mapping,
        })
        self.addCleanup(self.client.indices.delete, index=self.index)

    def insert(self, rows, keyword=False):
        self.create_index(keyword)
        lines = []
        for number, row in enumerate(rows):
            meta = {"_index": self.index, "_id": str(number)}
            if CLIENT == "elasticsearch":
                meta["_type"] = "_doc"
            lines.extend((json.dumps({"index": meta}), json.dumps(row)))
        result = self.client.bulk(body="\n".join(lines) + "\n")
        self.assertFalse(result["errors"], result)
        self.client.indices.refresh(index=self.index)

    def metric(self, name, period="month"):
        if self.index is None:
            self.create_index()
        return getattr(metrics, name + "_by_period")(self.client, self.index, DATE, [REPO], period)

    def assert_personal(self, personal, total, organization, period="month"):
        self.assertEqual(self.metric("personal_code_contribution", period), {
            "personal_code_contribution_lines": personal, "period": period,
        })
        self.assertEqual(self.metric("personal_code_contribution_ratio", period), {
            "personal_code_contribution_ratio": personal / total if total else None,
            "personal_code_contribution_lines": personal, "total_lines_added": total, "period": period,
        })
        self.assertEqual(self.metric("org_code_contribution", period), {
            "org_code_contribution_lines": organization, "period": period,
        })

    def test_unknown_text_organization_is_personal(self):
        self.insert([commit(7, "Unknown")])
        self.assert_personal(7, 7, 0)

    def test_unknown_keyword_organization_is_personal(self):
        self.insert([commit(7, "Unknown")], keyword=True)
        self.assert_personal(7, 7, 0)

    def test_personal_ratio_includes_unknown_and_missing_text_fields(self):
        self.insert([commit(11, "Acme"), commit(7, "Unknown"), commit(3)])
        self.assert_personal(10, 21, 11)

    def test_personal_ratio_includes_unknown_and_missing_keyword_fields(self):
        self.insert([commit(11, "Acme"), commit(7, "Unknown"), commit(3)], keyword=True)
        self.assert_personal(10, 21, 11)

    def test_missing_organization_remains_personal(self):
        self.insert([commit(3)])
        self.assert_personal(3, 3, 0)

    def test_null_organization_remains_personal(self):
        self.insert([commit(5, None)])
        self.assert_personal(5, 5, 0)

    def test_empty_array_organization_remains_personal(self):
        self.insert([commit(4, [])])
        self.assert_personal(4, 4, 0)

    def test_known_organization_remains_excluded(self):
        self.insert([commit(11, "Acme")])
        self.assert_personal(0, 11, 11)

    def test_personal_and_existing_organization_selectors_partition_total(self):
        self.insert([commit(11, "Acme"), commit(7, "Unknown"), commit(3), commit(5, "")])
        total = self.metric("lines_changed")["lines_added"]
        personal = self.metric("personal_code_contribution")["personal_code_contribution_lines"]
        organization = self.metric("org_code_contribution")["org_code_contribution_lines"]
        self.assertEqual(total, 26)
        self.assertEqual(personal + organization, total)
        self.assertAlmostEqual(self.metric("personal_code_contribution_ratio")["personal_code_contribution_ratio"] +
                               self.metric("org_code_contribution_ratio")["org_code_contribution_ratio"], 1)

    def test_text_analysis_matches_existing_unknown_rule(self):
        self.insert([commit(7, "unknown")])
        self.assert_personal(7, 7, 0)

    def test_keyword_analysis_keeps_existing_case_sensitive_rule(self):
        self.insert([commit(7, "unknown")], keyword=True)
        self.assert_personal(0, 7, 7)

    def test_multiple_values_follow_existing_organization_exclusion(self):
        self.insert([commit(7, ["Acme", "Unknown"])])
        self.assert_personal(7, 7, 0)

    def test_repository_and_date_filters_remain_in_force(self):
        self.insert([
            commit(7, "Unknown"), commit(3, "Acme"),
            commit(100, "Unknown", tag="https://github.com/example/other.git"),
            commit(100, "Unknown", grimoire_creation_date="2025-12-15T12:00:00"),
            commit(100, "Unknown", grimoire_creation_date="2026-02-05T12:00:00"),
        ])
        self.assert_personal(7, 10, 3)

    def test_period_arguments_and_result_keys_are_preserved(self):
        self.insert([commit(7, "Unknown")])
        for period in ("quarter", "year"):
            self.assert_personal(7, 7, 0, period)

    def test_empty_period_returns_zero_and_no_ratio(self):
        self.assert_personal(0, 0, 0)

    def test_zero_lines_return_zero_and_no_ratio(self):
        self.insert([commit(0, "Unknown"), commit(0, "Acme")])
        self.assert_personal(0, 0, 0)

    def test_existing_organization_metric_and_ratio_are_unchanged(self):
        self.insert([commit(11, "Acme"), commit(7, "Unknown"), commit(3)])
        self.assertEqual(self.metric("org_code_contribution"), {
            "org_code_contribution_lines": 11, "period": "month",
        })
        self.assertEqual(self.metric("org_code_contribution_ratio"), {
            "org_code_contribution_ratio": 11 / 21, "org_code_contribution_lines": 11,
            "total_lines_added": 21, "period": "month",
        })

    def test_existing_bot_inclusion_is_preserved(self):
        self.insert([commit(7, "Unknown", author_bot=True)])
        self.assert_personal(7, 7, 0)
