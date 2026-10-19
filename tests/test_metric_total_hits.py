"""Native-service metric checks for integer and object total-hit responses.

Use COMPASS_TEST_SEARCH_URL with a disposable search service. Set
COMPASS_TEST_SEARCH_CLIENT=elasticsearch for its native client. Optionally set
COMPASS_TEST_INTEGER_HITS=1 to request integer totals from OpenSearch itself.
Responses are never replaced or rewritten. Only unique test indices and an
alias created by a test are deleted; existing security aliases are refused.
"""

import json
import importlib.util
import os
import unittest
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from compass_common.search_results import total_hits
from compass_metrics import issue_metrics as issue
from compass_metrics import pr_metrics as pr
from compass_metrics_v2 import issue_metrics_v2 as issue_v2
from compass_metrics_v2 import pr_metrics_v2 as pr_v2
from compass_metrics_v2 import git_metrics_v2 as git_v2


# Execute the real leaf module without the unrelated security package initializer,
# which imports document-rendering integrations and creates /data directories.
# This tests the public function's native search path, not package initialization.
spec = importlib.util.spec_from_file_location(
    "compass_vul_levels_native_test",
    Path(__file__).resolve().parents[1] / "compass_metrics/security_metric/get_vul_level.py",
)
security_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(security_module)
get_vul_levels_metrics = security_module.get_vul_levels_metrics


URL = os.environ.get("COMPASS_TEST_SEARCH_URL")
CLIENT = os.environ.get("COMPASS_TEST_SEARCH_CLIENT", "opensearch")
INTEGER = os.environ.get("COMPASS_TEST_INTEGER_HITS") == "1"
DATE = datetime(2026, 1, 20)
REPO = "https://github.com/example/project"
SECURITY_ALIAS = "compass_metric_model_opencheck"


class NativeResponseMode:
    """Add a wire-format query parameter, leaving native responses untouched."""
    def __init__(self, client):
        self.client = client

    def search(self, **kwargs):
        if INTEGER:
            params = dict(kwargs.pop("params", {}))
            params["rest_total_hits_as_int"] = "true"
            kwargs["params"] = params
        return self.client.search(**kwargs)


def metric(module, name):
    return lambda client, index: getattr(module, name)(client, index, DATE, [REPO])


CASES = [
    ("issue_response", metric(issue, "issue_first_reponse"),
     {"issue_first_reponse_avg": 3, "issue_first_reponse_mid": 3},
     {"issue_first_reponse_avg": None, "issue_first_reponse_mid": None}),
    ("issue_comments", metric(issue, "comment_frequency"),
     {"comment_frequency": 5}, {"comment_frequency": None}),
    ("issue_comments_year", metric(issue, "comment_frequency_year"),
     {"comment_frequency_year": 5}, {"comment_frequency_year": None}),
    ("pr_reviews", metric(pr, "code_review_count"),
     {"code_review_count": 9}, {"code_review_count": None}),
    ("pr_reviews_year", metric(pr, "code_review_count_year"),
     {"code_review_count_year": 9}, {"code_review_count_year": None}),
    ("v2_issue_response", metric(issue_v2, "issue_new_first_response_time_by_period"),
     {"issue_new_first_response_avg": 4, "issue_new_first_response_mid": 4, "period": "month"},
     {"issue_new_first_response_avg": None, "issue_new_first_response_mid": None, "period": "month"}),
    ("v2_issue_comments", metric(issue_v2, "issue_comment_activity_by_period"),
     {"issue_comment_activity": 4, "period": "month"}, {"issue_comment_activity": 0, "period": "month"}),
    ("v2_pr_response", metric(pr_v2, "pr_new_first_response_time_by_period"),
     {"pr_new_first_response_avg": 8, "pr_new_first_response_mid": 8, "period": "month"},
     {"pr_new_first_response_avg": None, "pr_new_first_response_mid": None, "period": "month"}),
    ("v2_pr_interactions", metric(pr_v2, "pr_avg_interactions_by_period"),
     {"pr_avg_interactions": 10, "pr_comments_total": 10, "pr_total_count": 1, "period": "month"},
     {"pr_avg_interactions": None, "pr_comments_total": 0, "pr_total_count": 0, "period": "month"}),
    ("v2_pr_comments", metric(pr_v2, "pr_comment_count_by_period"),
     {"pr_comment_count": 8, "period": "month"}, {"pr_comment_count": 0, "period": "month"}),
    ("v2_git_lines", metric(git_v2, "lines_changed_by_period"),
     {"lines_added": 18, "lines_removed": 4, "period": "month"},
     {"lines_added": 0, "lines_removed": 0, "period": "month"}),
    ("v2_git_org_lines", metric(git_v2, "org_code_contribution_by_period"),
     {"org_code_contribution_lines": 11, "period": "month"},
     {"org_code_contribution_lines": 0, "period": "month"}),
    ("v2_git_personal_lines", metric(git_v2, "personal_code_contribution_by_period"),
     {"personal_code_contribution_lines": 7, "period": "month"},
     {"personal_code_contribution_lines": 0, "period": "month"}),
    ("security_levels", lambda client, index: get_vul_levels_metrics(REPO, client, "v1"),
     {"vul_levels": 1, "vul_level_details": [{
         "package_name": "fixture", "package_version": "1.0", "vulnerabilities": ["TEST-1"], "severity": "LOW",
     }]}, ValueError),
]


@unittest.skipUnless(URL, "requires COMPASS_TEST_SEARCH_URL for a disposable search service")
class MetricTotalHitsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if CLIENT == "elasticsearch":
            from elasticsearch import Elasticsearch
            cls.native = Elasticsearch(URL)
        elif CLIENT == "opensearch":
            from opensearchpy import OpenSearch
            cls.native = OpenSearch(URL)
        else:
            raise ValueError("unknown COMPASS_TEST_SEARCH_CLIENT: " + CLIENT)
        cls.client = NativeResponseMode(cls.native)
        print("Live search:", cls.native.info()["version"]["number"], "client:", CLIENT, "integer wire request:", INTEGER)

    def setUp(self):
        self.index = "compass-total-hits-test-" + uuid4().hex
        properties = {
            "uuid": {"type": "keyword"}, "tag": {"type": "keyword"},
            "pull_request": {"type": "boolean"}, "grimoire_creation_date": {"type": "date"},
            "time_to_first_attention_without_bot": {"type": "double"},
            "num_of_comments_without_bot": {"type": "long"},
            "num_review_comments_without_bot": {"type": "long"},
            "lines_added": {"type": "long"}, "lines_removed": {"type": "long"},
            "author_org_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "project_url": {"type": "keyword"},
        }
        mapping = {"properties": properties}
        if CLIENT == "elasticsearch":
            mapping = {"_doc": mapping}
        self.native.indices.create(index=self.index, body={
            "settings": {"number_of_shards": 1, "number_of_replicas": 0}, "mappings": mapping,
        })
        self.addCleanup(self.native.indices.delete, index=self.index)

    def populate(self):
        rows = []
        for month, issue_comments, issue_response, pr_comments, pr_response in [
            ("2026-01", 4, 2, 8, 6), ("2025-12", 6, 4, 10, 8),
        ]:
            rows.extend([
                {"uuid": "issue-" + month, "tag": REPO, "pull_request": False,
                 "grimoire_creation_date": month + "-15T12:00:00",
                 "num_of_comments_without_bot": issue_comments,
                 "time_to_first_attention_without_bot": issue_response},
                {"uuid": "pr-" + month, "tag": REPO, "pull_request": True,
                 "grimoire_creation_date": month + "-15T12:00:00",
                 "num_review_comments_without_bot": pr_comments,
                 "time_to_first_attention_without_bot": pr_response},
            ])
        rows.extend([
            {"tag": REPO + ".git", "grimoire_creation_date": "2026-01-15T12:00:00",
             "lines_added": 11, "lines_removed": 3, "author_org_name": "Acme"},
            {"tag": REPO + ".git", "grimoire_creation_date": "2026-01-16T12:00:00",
             "lines_added": 7, "lines_removed": 1},
            {"project_url": REPO, "security": [{"package_name": "fixture", "package_version": "1.0",
              "vulnerabilities": [{"aliases": ["TEST-1"], "severity": "LOW"}]}]},
        ])
        lines = []
        for position, row in enumerate(rows):
            meta = {"_index": self.index, "_id": str(position)}
            if CLIENT == "elasticsearch":
                meta["_type"] = "_doc"
            lines.extend((json.dumps({"index": meta}), json.dumps(row)))
        result = self.native.bulk(body="\n".join(lines) + "\n")
        self.assertFalse(result["errors"], result)
        self.native.indices.refresh(index=self.index)

    def bind_security_alias(self):
        if self.native.indices.exists(index=SECURITY_ALIAS):
            raise RuntimeError("refusing to replace an existing security index or alias")
        self.native.indices.put_alias(index=self.index, name=SECURITY_ALIAS)
        self.addCleanup(self.native.indices.delete_alias, index=self.index, name=SECURITY_ALIAS)

    def test_actual_wire_format(self):
        self.populate()
        response = self.client.search(index=self.index, body={"size": 0, "track_total_hits": True})
        raw = response["hits"]["total"]
        self.assertIs(type(raw), int if INTEGER or CLIENT == "elasticsearch" else dict)
        self.assertEqual(total_hits(response), 7)

    def test_unchanged_pr_response_metric(self):
        self.populate()
        self.assertEqual(pr.pr_time_to_first_response(self.client, self.index, DATE, [REPO]), {
            "pr_time_to_first_response_avg": 7, "pr_time_to_first_response_mid": 7,
        })

    def test_helper_accepts_integer_totals(self):
        self.assertEqual(total_hits({"hits": {"total": 0}}), 0)
        self.assertEqual(total_hits({"hits": {"total": 2 ** 40}}), 2 ** 40)

    def test_helper_preserves_object_value(self):
        self.assertEqual(total_hits({"hits": {"total": {"value": 0, "relation": "eq"}}}), 0)
        self.assertEqual(total_hits({"hits": {"total": {"value": 10000, "relation": "gte"}}}), 10000)

    def test_helper_does_not_hide_missing_fields(self):
        for response in ({}, {"hits": {}}, {"hits": {"total": {"relation": "eq"}}}):
            with self.assertRaises(KeyError):
                total_hits(response)

    def test_helper_rejects_malformed_total_types(self):
        for value in (None, "0", [], True, 0.5):
            with self.assertRaises(TypeError):
                total_hits({"hits": {"total": value}})


def make_case(name, call, expected, empty):
    def test(self):
        if not empty:
            self.populate()
        if name == "security_levels":
            self.bind_security_alias()
        result = call(self.client, self.index)
        if expected is ValueError:
            self.assertIsInstance(result, ValueError)
            self.assertEqual(str(result), "No security metrics found for this repo")
        else:
            self.assertEqual(result, expected)
    return test


for name, call, populated, empty in CASES:
    setattr(MetricTotalHitsTest, "test_" + name + "_populated", make_case(name, call, populated, False))
    setattr(MetricTotalHitsTest, "test_" + name + "_empty", make_case(name, call, empty, True))
