"""Regression tests for the metric wiring of the compass_model_v2 models.

BaseMetricsModel.__init__ resolves every metric a model declares through
compass_metrics/resources/thresholds.yaml and BaseMetricsModel.get_metrics
resolves it through the metrics_switch table of
compass_model/base_metrics_model_v2.py. A model that references a metric which is
missing from either place cannot be built (KeyError while resolving the default
threshold) or cannot be run (Invalid metric raised by get_metrics), which is what
happened to the ecological-influence models.

The tests pin the contract down for the whole package and cover the ecological
influence models end to end: every metric they declare must be implemented in
compass_metrics_v2/ecological_influence_metrics_v2.py, must have a default
threshold for the repo level and for the community level and must be registered
in the metrics_switch.

The wiring is inspected by parsing the sources with ast instead of importing
them, so the checks need no Elasticsearch client and cannot be fooled by a metric
that only appears in a comment. The aggregation semantics are covered through the
pure summarize_ecological_influence helper.

Run from the repository root with
    python -m pytest tests/test_metric_model_registration.py
or
    python -m unittest discover -s tests
"""

import ast
import os
import sys
import unittest

import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

MODEL_ROOT = os.path.join(REPO_ROOT, "compass_model_v2")
BASE_MODEL_FILE = os.path.join(REPO_ROOT, "compass_model", "base_metrics_model_v2.py")
THRESHOLDS_FILE = os.path.join(REPO_ROOT, "compass_metrics", "resources", "thresholds.yaml")
ECOLOGICAL_METRICS_FILE = os.path.join(
    REPO_ROOT, "compass_metrics_v2", "ecological_influence_metrics_v2.py")

ECOLOGICAL_MODEL_FILES = [
    os.path.join("compass_model_v2", "community_health", "ecological_influence",
                 "partner_diversity_metrics_model.py"),
    os.path.join("compass_model_v2", "community_health", "ecological_influence",
                 "partner_influence_metrics_model.py"),
    os.path.join("compass_model_v2", "community_health", "ecological_influence",
                 "technology_adoption_metrics_model.py"),
]

# Metrics the ecological influence models have to declare: the ones the enriched
# contributor index can actually feed. package_downloads and paper_citations are
# deliberately absent, the repository has no package download and no publication
# citation data source, so those two metrics cannot be computed here.
EXPECTED_ECOLOGICAL_METRICS = {
    "business_org_count",
    "business_org_contributors",
    "research_institution_count",
    "research_institution_developers",
    "individual_core_contributors",
    "business_org_influence",
    "research_institution_influence",
    "individual_contributor_influence",
    "open_source_adoption",
    "commercial_adoption",
}


def _model_files():
    """Yield (path relative to the repository root, absolute path) per module."""
    for dirpath, _, filenames in os.walk(MODEL_ROOT):
        for filename in sorted(filenames):
            if not filename.endswith(".py") or filename == "__init__.py":
                continue
            absolute_path = os.path.join(dirpath, filename)
            yield os.path.relpath(absolute_path, REPO_ROOT), absolute_path


def _parse(absolute_path):
    with open(absolute_path, encoding="utf-8") as handle:
        return ast.parse(handle.read(), filename=absolute_path)


def _dict_string_keys(absolute_path, variable_name):
    """Return the string keys of every dict assigned to variable_name.

    The sources are parsed, not imported, so a metric that only lives in a
    comment is invisible here and a model whose code is commented out
    contributes nothing.
    """
    keys = set()
    for node in ast.walk(_parse(absolute_path)):
        if not isinstance(node, ast.Assign):
            continue
        targets = [target for target in node.targets
                   if isinstance(target, ast.Name) and target.id == variable_name]
        if not targets or not isinstance(node.value, ast.Dict):
            continue
        for key in node.value.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                keys.add(key.value)
    return keys


def _declared_metrics(absolute_path):
    return _dict_string_keys(absolute_path, "metrics_weights_thresholds")


def _class_names(absolute_path):
    return {node.name for node in ast.walk(_parse(absolute_path))
            if isinstance(node, ast.ClassDef)}


def _function_names(absolute_path):
    return {node.name for node in ast.walk(_parse(absolute_path))
            if isinstance(node, ast.FunctionDef)}


def _switch_keys():
    return _dict_string_keys(BASE_MODEL_FILE, "metrics_switch")


def _default_threshold_metrics():
    """Return (repo level, community level) metric names of thresholds.yaml."""
    with open(THRESHOLDS_FILE, encoding="utf-8") as handle:
        groups = yaml.safe_load(handle)["metrics_default_threshold"]
    repo_level, community_level = set(), set()
    for entries in groups.values():
        for entry in entries:
            repo_level.add(entry["metric"])
            community_level.add(entry["metric"])
    return repo_level, community_level


class ModelRegistrationTest(unittest.TestCase):
    def test_every_declared_metric_has_a_default_threshold(self):
        repo_level, community_level = _default_threshold_metrics()
        self.assertGreater(len(repo_level), 0)
        for path, absolute_path in _model_files():
            for metric in sorted(_declared_metrics(absolute_path)):
                self.assertIn(metric, repo_level,
                              "%s: no repo_threshold for %s" % (path, metric))
                self.assertIn(metric, community_level,
                              "%s: no multiple_threshold for %s" % (path, metric))

    def test_every_declared_metric_is_registered_in_the_switch(self):
        switch = _switch_keys()
        self.assertGreater(len(switch), 0)
        for path, absolute_path in _model_files():
            for metric in sorted(_declared_metrics(absolute_path)):
                self.assertIn(metric, switch,
                              "%s: %s is missing from metrics_switch" % (path, metric))

    def test_threshold_entries_define_both_levels(self):
        with open(THRESHOLDS_FILE, encoding="utf-8") as handle:
            groups = yaml.safe_load(handle)["metrics_default_threshold"]
        self.assertGreater(len(groups), 0)
        for group, entries in groups.items():
            for entry in entries:
                self.assertIn("repo_threshold", entry,
                              "%s: %s" % (group, entry.get("metric")))
                self.assertIn("multiple_threshold", entry,
                              "%s: %s" % (group, entry.get("metric")))


class EcologicalInfluenceWiringTest(unittest.TestCase):
    def test_models_are_active_and_declare_the_expected_metrics(self):
        declared = set()
        for relative_path in ECOLOGICAL_MODEL_FILES:
            absolute_path = os.path.join(REPO_ROOT, relative_path)
            self.assertTrue(os.path.exists(absolute_path), relative_path)
            self.assertNotEqual(set(), _class_names(absolute_path), relative_path)
            declared |= _declared_metrics(absolute_path)
        self.assertEqual(EXPECTED_ECOLOGICAL_METRICS, declared)

    def test_every_metric_is_implemented_and_registered(self):
        switch = _switch_keys()
        functions = _function_names(ECOLOGICAL_METRICS_FILE)
        for metric in sorted(EXPECTED_ECOLOGICAL_METRICS):
            self.assertIn(metric, functions,
                          "%s is not implemented in ecological_influence_metrics_v2" % metric)
            self.assertIn(metric, switch,
                          "%s is not registered in metrics_switch" % metric)

    def test_metrics_have_default_thresholds(self):
        repo_level, community_level = _default_threshold_metrics()
        for metric in sorted(EXPECTED_ECOLOGICAL_METRICS):
            self.assertIn(metric, repo_level, "no repo_threshold for %s" % metric)
            self.assertIn(metric, community_level, "no multiple_threshold for %s" % metric)


class EcologicalInfluenceLogicTest(unittest.TestCase):
    def test_classify_organization(self):
        from compass_metrics_v2.ecological_influence_metrics_v2 import (
            BUSINESS_ORGANIZATION, RESEARCH_INSTITUTION, classify_organization)
        self.assertEqual(RESEARCH_INSTITUTION, classify_organization("Tsinghua University"))
        self.assertEqual(RESEARCH_INSTITUTION, classify_organization("Chinese Academy of Sciences"))
        self.assertEqual(BUSINESS_ORGANIZATION, classify_organization("Huawei Technologies"))
        self.assertIsNone(classify_organization(None))
        self.assertIsNone(classify_organization(""))

    def test_summarize_ecological_influence(self):
        from compass_metrics_v2.ecological_influence_metrics_v2 import summarize_ecological_influence
        contributors = [
            {"contribution": 60, "contribution_without_observe": 40,
             "ecological_type": "organization manager",
             "organization": "Huawei Technologies", "mileage_type": "core"},
            {"contribution": 30, "contribution_without_observe": 30,
             "ecological_type": "organization participant",
             "organization": "Huawei Technologies", "mileage_type": "regular"},
            {"contribution": 20, "contribution_without_observe": 20,
             "ecological_type": "organization participant",
             "organization": "Tsinghua University", "mileage_type": "core"},
            {"contribution": 10, "contribution_without_observe": 0,
             "ecological_type": "individual participant",
             "organization": None, "mileage_type": "core"},
        ]
        summary = summarize_ecological_influence(contributors)
        self.assertEqual(1, summary["business_org_count"])
        self.assertEqual(2, summary["business_org_contributors"])
        self.assertEqual(1, summary["research_institution_count"])
        self.assertEqual(1, summary["research_institution_developers"])
        self.assertEqual(1, summary["individual_core_contributors"])
        self.assertEqual(0.75, summary["business_org_influence"])
        self.assertEqual(0.1667, summary["research_institution_influence"])
        self.assertEqual(0.0833, summary["individual_contributor_influence"])
        self.assertEqual(30, summary["open_source_adoption"])
        self.assertEqual(1, summary["commercial_adoption"])

    def test_summarize_without_contributors(self):
        from compass_metrics_v2.ecological_influence_metrics_v2 import summarize_ecological_influence
        summary = summarize_ecological_influence([])
        self.assertEqual(0, summary["business_org_count"])
        self.assertIsNone(summary["business_org_influence"])
        self.assertEqual(0, summary["open_source_adoption"])


if __name__ == "__main__":
    unittest.main()
