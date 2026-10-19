"""Live aggregation regressions; use only a disposable Elasticsearch/OpenSearch.

COMPASS_TEST_SEARCH_URL=http://localhost:9200 python -m unittest discover \
    -s tests -p test_period_contribution_sums.py -v
Set COMPASS_TEST_SEARCH_CLIENT=elasticsearch for the declared Elasticsearch client.
The suite creates and deletes only its own uniquely named test indices.
"""

import os
import unittest
from datetime import datetime, timedelta
from uuid import uuid4

from compass_metrics_v2 import contributor_metrics_v2 as metrics
from compass_metrics_v2 import developer_metrics_v2 as developer_metrics
from compass_metrics import contributor_metrics as legacy_metrics


URL = os.environ.get("COMPASS_TEST_SEARCH_URL")
CLIENT = os.environ.get("COMPASS_TEST_SEARCH_CLIENT", "opensearch")
DATE = datetime(2026, 1, 20)
REPO = "https://github.com/example/project"


def contribution(name, kind, entries, **overrides):
    row = {
        "contributor": name,
        "ecological_type": kind,
        "repo_name": REPO,
        "grimoire_creation_date": "2026-01-15T12:00:00",
        "is_bot": False,
        "contribution": sum(count for _, count in entries),
        "contribution_type_list": [
            {"contribution_type": activity, "contribution": count}
            for activity, count in entries
        ],
    }
    row.update(overrides)
    return row


@unittest.skipUnless(URL, "requires COMPASS_TEST_SEARCH_URL for a disposable search service")
class PeriodContributionSumsTest(unittest.TestCase):
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
        print("Live search version:", cls.client.info()["version"]["number"], "client:", CLIENT)

    def setUp(self):
        self.index = "compass-period-sums-test-" + uuid4().hex
        self.client.indices.create(index=self.index, body={
            "settings": {"number_of_shards": 1, "number_of_replicas": 0},
        })
        self.addCleanup(self.client.indices.delete, index=self.index)

    def insert(self, rows):
        for position, row in enumerate(rows):
            args = {"index": self.index, "id": str(position), "body": row}
            if CLIENT == "elasticsearch":
                args["doc_type"] = "_doc"
            self.client.index(**args)
        self.client.indices.refresh(index=self.index)

    def mixed(self):
        self.insert([
            contribution("org", "organization participant", [
                ("code_author", 2), ("pr_comments", 3), ("issue_creation", 7), ("star", 13),
            ]),
            contribution("person", "individual participant", [
                ("code_committer", 1), ("pr_merged", 2), ("issue_comments", 11), ("fork", 17),
            ]),
        ])

    def metric(self, key, module=metrics):
        return getattr(module, key + "_by_period")(
            self.client, self.index, DATE, [REPO], "month"
        )

    def test_org_code_counts_only_code_entries(self):
        self.mixed()
        self.assertEqual(self.metric("org_code_contribution"), {
            "org_code_contribution": 5, "period": "month",
        })

    def test_individual_code_counts_only_code_entries(self):
        self.mixed()
        self.assertEqual(self.metric("individual_code_contribution"), {
            "individual_code_contribution": 3, "period": "month",
        })

    def test_org_non_code_includes_mixed_contributors(self):
        self.mixed()
        self.assertEqual(self.metric("org_non_code_contribution"), {
            "org_non_code_contribution": 20, "period": "month",
        })

    def test_individual_non_code_includes_mixed_contributors(self):
        self.mixed()
        self.assertEqual(self.metric("individual_non_code_contribution"), {
            "individual_non_code_contribution": 28, "period": "month",
        })

    def test_org_code_ratio_uses_code_total(self):
        self.mixed()
        self.assertEqual(self.metric("org_code_contribution_ratio"), {
            "org_code_contribution_ratio": 5 / 8, "org_code_contribution": 5,
            "total_code_contribution": 8, "period": "month",
        })

    def test_individual_code_ratio_uses_code_total(self):
        self.mixed()
        self.assertEqual(self.metric("individual_code_contribution_ratio"), {
            "individual_code_contribution_ratio": 3 / 8, "individual_code_contribution": 3,
            "total_code_contribution": 8, "period": "month",
        })

    def test_org_non_code_ratio_uses_all_non_code_entries(self):
        self.mixed()
        self.assertEqual(self.metric("org_non_code_contribution_ratio"), {
            "org_non_code_contribution_ratio": 20 / 48, "org_non_code_contribution": 20,
            "total_non_code_contribution": 48, "period": "month",
        })

    def test_individual_non_code_ratio_uses_all_non_code_entries(self):
        self.mixed()
        self.assertEqual(self.metric("individual_non_code_contribution_ratio"), {
            "individual_non_code_contribution_ratio": 28 / 48, "individual_non_code_contribution": 28,
            "total_non_code_contribution": 48, "period": "month",
        })

    def test_developer_org_non_code_includes_mixed_contributors(self):
        self.mixed()
        self.assertEqual(self.metric("org_non_code_contribution", developer_metrics), {
            "org_non_code_contribution": 20, "period": "month",
        })

    def test_developer_individual_non_code_includes_mixed_contributors(self):
        self.mixed()
        self.assertEqual(self.metric("individual_non_code_contribution", developer_metrics), {
            "individual_non_code_contribution": 28, "period": "month",
        })

    def test_developer_org_non_code_ratio_uses_all_non_code_entries(self):
        self.mixed()
        self.assertEqual(self.metric("org_non_code_contribution_ratio", developer_metrics), {
            "org_non_code_contribution_ratio": 20 / 48, "org_non_code_contribution": 20,
            "total_non_code_contribution": 48, "period": "month",
        })

    def test_developer_individual_non_code_ratio_uses_all_non_code_entries(self):
        self.mixed()
        self.assertEqual(self.metric("individual_non_code_contribution_ratio", developer_metrics), {
            "individual_non_code_contribution_ratio": 28 / 48, "individual_non_code_contribution": 28,
            "total_non_code_contribution": 48, "period": "month",
        })

    def assert_totals(self, org_code, person_code, org_non_code, person_non_code):
        for kind, org, person in [
            ("code", org_code, person_code), ("non_code", org_non_code, person_non_code),
        ]:
            total = org + person
            for owner, amount in [("org", org), ("individual", person)]:
                key = owner + "_" + kind + "_contribution"
                modules = [metrics, developer_metrics] if kind == "non_code" else [metrics]
                for module in modules:
                    self.assertEqual(self.metric(key, module)[key], amount)
                    result = self.metric(key + "_ratio", module)
                    self.assertEqual(result[key], amount)
                    self.assertEqual(result["total_" + kind + "_contribution"], total)
                    self.assertEqual(result[key + "_ratio"], amount / total if total else None)

    def test_empty_index_keeps_zero_counts_and_none_ratios(self):
        self.assert_totals(0, 0, 0, 0)

    def test_code_only_contributors(self):
        self.insert([
            contribution("org", "organization participant", [("pr_creation", 4)]),
            contribution("person", "individual participant", [("code_author", 6)]),
        ])
        self.assert_totals(4, 6, 0, 0)

    def test_non_code_only_contributors_keep_observer_activity(self):
        self.insert([
            contribution("org", "organization participant", [("issue_comments", 2), ("star", 7)]),
            contribution("person", "individual participant", [("issue_creation", 3), ("fork", 11)]),
        ])
        self.assert_totals(0, 0, 9, 14)

    def test_repository_date_and_bot_filters_are_preserved(self):
        self.insert([
            contribution("org", "organization participant", [("pr_creation", 4)]),
            contribution("person", "individual participant", [("issue_comments", 6)]),
            contribution("bot", "organization participant", [("code_author", 100)], is_bot=True),
            contribution("elsewhere", "individual participant", [("issue_comments", 200)], repo_name="other"),
            contribution("old", "individual participant", [("code_author", 300)],
                         grimoire_creation_date="2025-12-15T12:00:00"),
            contribution("future", "organization participant", [("issue_comments", 400)],
                         grimoire_creation_date="2026-02-15T12:00:00"),
        ])
        self.assert_totals(4, 0, 0, 6)

    def test_large_contribution_counts_do_not_overflow_script_integer(self):
        self.insert([
            contribution("org", "organization participant", [("code_author", 2 ** 31), ("pr_merged", 9)]),
            contribution("person", "individual participant", [("issue_comments", 2 ** 31 + 3)]),
        ])
        self.assert_totals(2 ** 31 + 9, 0, 0, 2 ** 31 + 3)


    def assert_types(self, module, expected):
        self.assertEqual(module.types_of_contributions(self.client, self.index, DATE, [REPO]), {
            "types_of_contributions": len(expected),
            "types_of_contributions_detail": [
                {"contribution_type": kind, "contributor": people, "contribution": count}
                for kind, people, count in expected
            ],
        })

    def mixed_types(self, module):
        self.mixed()
        self.assert_types(module, [
            ("code_author", 1, 2), ("code_committer", 1, 1), ("fork", 1, 17),
            ("issue_comments", 1, 11), ("issue_creation", 1, 7),
            ("pr_comments", 1, 3), ("pr_merged", 1, 2), ("star", 1, 13),
        ])

    def repeated_contributor_types(self, module):
        self.insert([
            contribution("same", "organization participant", [("code_author", 2), ("issue_comments", 7)]),
            contribution("same", "organization participant", [("code_author", 5)]),
            contribution("other", "individual participant", [("code_author", 3), ("issue_comments", 11)]),
        ])
        self.assert_types(module, [("code_author", 2, 10), ("issue_comments", 2, 18)])

    def filtered_types(self, module):
        self.insert([
            contribution("org", "organization participant", [
                ("issue_comments", 2 ** 31 + 3), ("自定义贡献", 7), ("star", 13),
            ]),
            # Type summaries have always included bot activity, unlike period governance counts.
            contribution("bot", "individual participant", [("自定义贡献", 11)], is_bot=True),
            contribution("edge", "individual participant", [("star", 5)],
                         grimoire_creation_date=(DATE - timedelta(days=90)).isoformat()),
            contribution("edge", "individual participant", [("star", 2)],
                         grimoire_creation_date=DATE.isoformat()),
            contribution("elsewhere", "individual participant", [("自定义贡献", 1000)], repo_name="other"),
            contribution("old", "individual participant", [("star", 2000)],
                         grimoire_creation_date="2025-01-01T12:00:00"),
            contribution("future", "individual participant", [("star", 3000)],
                         grimoire_creation_date="2026-02-01T12:00:00"),
        ])
        self.assert_types(module, [("star", 2, 20), ("自定义贡献", 2, 18), ("issue_comments", 1, 2 ** 31 + 3)])

    def test_legacy_type_summary_keeps_mixed_counts_paired(self):
        self.mixed_types(legacy_metrics)

    def test_v2_type_summary_keeps_mixed_counts_paired(self):
        self.mixed_types(metrics)

    def test_legacy_type_summary_deduplicates_contributors(self):
        self.repeated_contributor_types(legacy_metrics)

    def test_v2_type_summary_deduplicates_contributors(self):
        self.repeated_contributor_types(metrics)

    def test_legacy_type_summary_preserves_filters_and_unknown_types(self):
        self.filtered_types(legacy_metrics)

    def test_v2_type_summary_preserves_filters_and_unknown_types(self):
        self.filtered_types(metrics)

    def test_empty_legacy_type_summary(self):
        self.assert_types(legacy_metrics, [])

    def test_empty_v2_type_summary(self):
        self.assert_types(metrics, [])


if __name__ == "__main__":
    unittest.main()
