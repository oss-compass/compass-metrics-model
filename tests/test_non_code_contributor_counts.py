"""Run against a disposable Elasticsearch/OpenSearch with its native client.

COMPASS_TEST_SEARCH_URL=http://localhost:9200 python -m unittest discover \
    -s tests -p test_non_code_contributor_counts.py -v
Set COMPASS_TEST_SEARCH_CLIENT=elasticsearch for Elasticsearch's declared client.
Only uniquely named indices created by this suite are deleted.
"""

import json
import os
import unittest
from datetime import datetime
from uuid import uuid4

from compass_metrics_v2 import contributor_metrics_v2 as metrics
from compass_metrics_v2 import developer_metrics_v2 as developer_metrics


URL = os.environ.get("COMPASS_TEST_SEARCH_URL")
CLIENT = os.environ.get("COMPASS_TEST_SEARCH_CLIENT", "opensearch")
DATE = datetime(2026, 1, 20)
REPO = "https://github.com/example/project"
OTHER_REPO = "https://github.com/example/other"
MODULES = (metrics, developer_metrics)


def contribution(name, role, activity="issue_creation", **overrides):
    row = {
        "contributor": name,
        "ecological_type": role,
        "repo_name": REPO,
        "grimoire_creation_date": "2026-01-15T12:00:00",
        "is_bot": False,
        "contribution": 1,
        "contribution_without_observe": int(activity not in ("star", "fork")),
        "contribution_type_list": [{"contribution_type": activity, "contribution": 1}],
    }
    row.update(overrides)
    return row


@unittest.skipUnless(URL, "requires COMPASS_TEST_SEARCH_URL for a disposable search service")
class NonCodeContributorCountsTest(unittest.TestCase):
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
        self.index = "compass-non-code-counts-test-" + uuid4().hex
        self.client.indices.create(index=self.index, body={
            "settings": {"number_of_shards": 2, "number_of_replicas": 0},
        })
        self.addCleanup(self.client.indices.delete, index=self.index)

    def insert(self, rows):
        lines = []
        for position, row in enumerate(rows):
            meta = {"_index": self.index, "_id": str(position)}
            if CLIENT == "elasticsearch":
                meta["_type"] = "_doc"
            lines.extend((json.dumps({"index": meta}), json.dumps(row)))
        response = self.client.bulk(body="\n".join(lines) + "\n")
        self.assertFalse(response["errors"], response)
        self.client.indices.refresh(index=self.index)

    def metric(self, key, module=metrics, repos=None):
        return getattr(module, key + "_by_period")(
            self.client, self.index, DATE, repos or [REPO], "month"
        )

    def mixed(self):
        self.insert([
            contribution("actual-org", "organization participant"),
            contribution("actual-person", "individual participant"),
            contribution("org-star", "organization participant", "star"),
            contribution("org-fork", "organization participant", "fork"),
            contribution("person-star", "individual participant", "star"),
            contribution("mixed-org", "organization participant", "code_author"),
            contribution("mixed-org", "organization participant", "issue_comments",
                         grimoire_creation_date="2026-01-08T12:00:00"),
        ])

    def assert_count(self, key, value, module, repos=None):
        self.assertEqual(self.metric(key, module, repos), {key: value, "period": "month"})

    def assert_ratio(self, role, count, total, module, repos=None):
        key = role + "_non_code_contributors"
        self.assertEqual(self.metric(key + "_ratio", module, repos), {
            key + "_ratio": count / total if total else None,
            key: count, "total_non_code_contributors": total, "period": "month",
        })

    def assert_counts(self, total, org, individual, repos=None):
        for module in MODULES:
            self.assert_count("non_code_contributors", total, module, repos)
            self.assert_count("org_non_code_contributors", org, module, repos)
            self.assert_count("individual_non_code_contributors", individual, module, repos)
            self.assert_ratio("org", org, total, module, repos)
            self.assert_ratio("individual", individual, total, module, repos)

    def test_global_non_code_count(self):
        self.mixed()
        self.assert_count("non_code_contributors", 2, metrics)

    def test_org_non_code_count(self):
        self.mixed()
        self.assert_count("org_non_code_contributors", 1, metrics)

    def test_org_non_code_ratio(self):
        self.mixed()
        self.assert_ratio("org", 1, 2, metrics)

    def test_individual_non_code_count(self):
        self.mixed()
        self.assert_count("individual_non_code_contributors", 1, metrics)

    def test_individual_non_code_ratio(self):
        self.mixed()
        self.assert_ratio("individual", 1, 2, metrics)

    def test_developer_global_non_code_count(self):
        self.mixed()
        self.assert_count("non_code_contributors", 2, developer_metrics)

    def test_developer_org_non_code_count(self):
        self.mixed()
        self.assert_count("org_non_code_contributors", 1, developer_metrics)

    def test_developer_org_non_code_ratio(self):
        self.mixed()
        self.assert_ratio("org", 1, 2, developer_metrics)

    def test_developer_individual_non_code_count(self):
        self.mixed()
        self.assert_count("individual_non_code_contributors", 1, developer_metrics)

    def test_developer_individual_non_code_ratio(self):
        self.mixed()
        self.assert_ratio("individual", 1, 2, developer_metrics)

    def test_observers_only_have_no_non_code_activity(self):
        self.insert([
            contribution("org", "organization participant", "star"),
            contribution("person", "individual participant", "fork"),
        ])
        self.assert_counts(0, 0, 0)

    def test_code_on_another_week_excludes_the_person(self):
        rows = []
        for name, role in [("org", "organization participant"),
                           ("person", "individual participant")]:
            rows.extend([
                contribution(name, role, "pr_creation", grimoire_creation_date="2026-01-05T00:00:00"),
                contribution(name, role, "issue_comments"),
            ])
        self.insert(rows)
        self.assert_counts(0, 0, 0)

    def test_code_in_another_selected_repository_excludes_the_person(self):
        self.insert([
            contribution("org", "organization participant", "code_author", repo_name=OTHER_REPO),
            contribution("org", "organization participant", "issue_comments"),
            contribution("person", "individual participant", "issue_creation"),
        ])
        self.assert_counts(1, 0, 1, [REPO, OTHER_REPO])

    def test_pure_non_code_activity_keeps_counts_and_result_keys(self):
        self.insert([
            contribution("org", "organization participant"),
            contribution("person", "individual participant"),
            contribution("org", "organization participant", "issue_comments"),
        ])
        self.assert_counts(2, 1, 1)

    def test_code_outside_the_date_repo_or_human_scope_does_not_exclude(self):
        rows = []
        for name, role in [("org", "organization participant"),
                           ("person", "individual participant")]:
            rows.extend([
                contribution(name, role),
                contribution(name, role, "code_author", repo_name=OTHER_REPO),
                contribution(name, role, "code_committer", grimoire_creation_date="2025-12-31T23:59:59"),
                contribution(name, role, "pr_merged", is_bot=True),
            ])
        self.insert(rows)
        self.assert_counts(2, 1, 1)

    def test_composite_pages_count_unique_people_without_readmitting_code(self):
        rows = [contribution("actor-%04d" % n, "organization participant") for n in range(1005)]
        rows.extend([
            contribution("actor-0000", "organization participant", "pr_comments"),
            contribution("actor-1004", "organization participant", "code_author"),
            contribution("observer", "organization participant", "fork"),
        ])
        self.insert(rows)
        self.assert_counts(1003, 1003, 0)

    def test_observer_only_role_does_not_supply_role_membership(self):
        self.insert([
            contribution("person", "organization participant", "star"),
            contribution("person", "individual participant", "issue_comments"),
        ])
        self.assert_counts(1, 0, 1)

    def test_empty_index_returns_zero_and_undefined_ratios(self):
        self.assert_counts(0, 0, 0)

    def test_actual_role_membership_can_overlap(self):
        self.insert([
            contribution("person", "organization participant", "issue_creation"),
            contribution("person", "individual participant", "issue_comments"),
        ])
        self.assert_counts(1, 1, 1)
