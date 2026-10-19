"""Live ranking regressions on a disposable native Elasticsearch/OpenSearch.

COMPASS_TEST_SEARCH_URL=http://localhost:9200 python -m unittest discover \
    -s tests -p test_highest_contribution.py -v
Set COMPASS_TEST_SEARCH_CLIENT=elasticsearch for its declared native client.
Only this suite's uniquely named test indices are deleted.
"""

import json
import os
import unittest
from datetime import datetime
from uuid import uuid4

from compass_metrics import contributor_metrics as legacy
from compass_metrics_v2 import contributor_metrics_v2 as v2


URL = os.environ.get("COMPASS_TEST_SEARCH_URL")
CLIENT = os.environ.get("COMPASS_TEST_SEARCH_CLIENT", "opensearch")
DATE = datetime(2026, 1, 20)
REPO = "https://github.com/example/project"
OTHER_REPO = "https://github.com/example/other"
MODULES = (legacy, v2)


def contribution(name, value=1, **overrides):
    row = {
        "contributor": name,
        "organization": name,
        "ecological_type": "organization participant",
        "repo_name": REPO,
        "grimoire_creation_date": "2026-01-15T12:00:00",
        "is_bot": False,
        "contribution": value,
    }
    row.update(overrides)
    return row


@unittest.skipUnless(URL, "requires COMPASS_TEST_SEARCH_URL for a disposable search service")
class HighestContributionTest(unittest.TestCase):
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
        self.index = "compass-contribution-ranking-test-" + uuid4().hex
        self.client.indices.create(index=self.index, body={
            "settings": {"number_of_shards": 2, "number_of_replicas": 0},
        })
        self.addCleanup(self.client.indices.delete, index=self.index)

    def insert(self, rows):
        lines = []
        for position, source in enumerate(rows):
            row = source.copy()
            meta = {"_index": self.index, "_id": str(position)}
            if CLIENT == "elasticsearch":
                meta["_type"] = "_doc"
            if "_routing" in row:
                meta["routing"] = row.pop("_routing")
            lines.extend((json.dumps({"index": meta}), json.dumps(row)))
        response = self.client.bulk(body="\n".join(lines) + "\n")
        self.assertFalse(response["errors"], response)
        self.client.indices.refresh(index=self.index)

    def metric(self, kind, module, **kwargs):
        key = "highest_contribution_" + kind
        return getattr(module, key)(self.client, self.index, DATE,
                                   kwargs.pop("repos", [REPO]), **kwargs)

    def assert_winner(self, expected, kinds=("organization", "contributor"), **kwargs):
        for module in MODULES:
            for kind in kinds:
                self.assertEqual(self.metric(kind, module, **kwargs), {
                    "highest_contribution_" + kind: expected,
                })

    def top_ten_trap(self):
        rows = []
        for n in range(11):
            rows.extend([contribution("frequent-%02d" % n), contribution("frequent-%02d" % n)])
        rows.append(contribution("winner", 100))
        self.insert(rows)

    def test_legacy_organization_winner_outside_ten_frequent_entities(self):
        self.top_ten_trap()
        self.assertEqual(self.metric("organization", legacy), {"highest_contribution_organization": "winner"})

    def test_legacy_contributor_winner_outside_ten_frequent_entities(self):
        self.top_ten_trap()
        self.assertEqual(self.metric("contributor", legacy), {"highest_contribution_contributor": "winner"})

    def test_v2_organization_winner_outside_ten_frequent_entities(self):
        self.top_ten_trap()
        self.assertEqual(self.metric("organization", v2), {"highest_contribution_organization": "winner"})

    def test_v2_contributor_winner_outside_ten_frequent_entities(self):
        self.top_ten_trap()
        self.assertEqual(self.metric("contributor", v2), {"highest_contribution_contributor": "winner"})

    def many_entities(self, winner):
        self.insert([contribution("actor-%04d" % n, 100000 if n == winner else 1) for n in range(1005)])

    def test_organization_winner_on_last_composite_page(self):
        self.many_entities(1004)
        self.assert_winner("actor-1004", ("organization",))

    def test_contributor_winner_on_last_composite_page(self):
        self.many_entities(1004)
        self.assert_winner("actor-1004", ("contributor",))

    def test_organization_winner_on_first_page_survives_later_pages(self):
        self.many_entities(0)
        self.assert_winner("actor-0000", ("organization",))

    def test_contributor_winner_on_first_page_survives_later_pages(self):
        self.many_entities(0)
        self.assert_winner("actor-0000", ("contributor",))

    def shard_trap(self):
        # Discover two actual distinct shards, rather than assuming routing hashes.
        routes = {}
        for number in range(30):
            route = str(number)
            shard = self.client.search_shards(index=self.index, routing=route)["shards"][0][0]["shard"]
            routes.setdefault(shard, route)
            if len(routes) == 2:
                break
        self.assertEqual(len(routes), 2)
        first, second = list(routes.values())
        rows = [contribution("winner", _routing=first) for _ in range(40)]
        rows.extend(contribution("runner-up", 2, _routing=first) for _ in range(30))
        for n in range(26):
            rows.extend([contribution("decoy-%02d" % n, _routing=second) for _ in range(2)])
        rows.append(contribution("winner", 100, _routing=second))
        self.insert(rows)

    def test_organization_sum_includes_a_low_frequency_shard(self):
        self.shard_trap()
        self.assert_winner("winner", ("organization",))

    def test_contributor_sum_includes_a_low_frequency_shard(self):
        self.shard_trap()
        self.assert_winner("winner", ("contributor",))

    def test_empty_index_returns_none(self):
        self.assert_winner(None)

    def test_missing_organization_key_returns_none_for_organizations(self):
        self.insert([contribution("person", organization=None, ecological_type="individual participant")])
        self.assert_winner(None, ("organization",))
        self.assert_winner("person", ("contributor",))

    def test_human_and_bot_scopes_remain_separate(self):
        self.insert([contribution("human", 3), contribution("bot", 300, is_bot=True)])
        self.assert_winner("human")
        self.assert_winner("bot", is_bot=True)

    def test_repository_and_date_filters(self):
        self.insert([
            contribution("winner", 3),
            contribution("other", 100, repo_name=OTHER_REPO),
            contribution("old", 100, grimoire_creation_date="2025-01-01T00:00:00"),
            contribution("future", 100, grimoire_creation_date="2026-01-20T00:00:00"),
        ])
        self.assert_winner("winner")

    def test_explicit_start_date_is_respected(self):
        self.insert([
            contribution("winner", 3),
            contribution("earlier", 100, grimoire_creation_date="2026-01-05T00:00:00"),
        ])
        self.assert_winner("winner", from_date=datetime(2026, 1, 10))

    def test_organization_scope_requires_organization_role(self):
        self.insert([
            contribution("org", 3),
            contribution("person", 100, ecological_type="individual participant"),
        ])
        self.assert_winner("org", ("organization",))
        self.assert_winner("person", ("contributor",))

    def test_sum_combines_selected_repositories_and_weeks(self):
        self.insert([
            contribution("winner", 30),
            contribution("winner", 40, repo_name=OTHER_REPO, grimoire_creation_date="2026-01-08T00:00:00"),
            contribution("runner-up", 60),
        ])
        self.assert_winner("winner", repos=[REPO, OTHER_REPO])

    def test_equal_sums_prefer_more_documents(self):
        self.insert([contribution("a", 10), contribution("b", 5), contribution("b", 5)])
        self.assert_winner("b")

    def test_equal_sums_and_counts_prefer_ascending_key(self):
        self.insert([contribution("z", 10), contribution("a", 10)])
        self.assert_winner("a")

    def test_zero_and_missing_contributions_preserve_sum_behavior(self):
        self.insert([contribution("a", 0), contribution("b", None), contribution("b", None)])
        self.assert_winner("b")

    def test_negative_sums_do_not_leave_the_winner_unset(self):
        self.insert([contribution("a", -5), contribution("b", -1)])
        self.assert_winner("b")
