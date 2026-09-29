"""Regression tests for the index ``lifecycle_statement`` is queried against.

``BaseMetricsModel.get_metrics`` builds a hand written ``metrics_switch`` table
of zero argument lambdas.  Every entry has to hand its metric the index that the
metric actually reads, and the whole supply-chain security block reads the
OpenCheck raw index (``openchecker_index``): the raw index stores the
``command_result`` documents written by the OpenCheck checkers, keyed by the
``command`` and ``label`` fields that ``base_opencheck_query`` filters on.

``lifecycle_statement`` is backed by the ``lifecycle-doc-checker`` command whose
``command_result`` (``has_eol`` / ``keywords_found``) only exists on the
OpenCheck raw index.  Repository documents are addressed through ``tag`` /
``origin`` and carry no ``command`` / ``label`` field, so ``base_opencheck_query``
matches nothing there and ``_fetch_command_result`` returns ``{}``.
``get_metrics`` used to hand ``lifecycle_statement`` ``self.repo_index`` - the
lone outlier in an otherwise uniformly ``self.openchecker_index`` block - which
made ``_calc_lifecycle_statement({})`` report ``lifecycle_statement = 0`` and
``lifecycle_statement_exists = False`` for every repository.  Because
``MaintenanceManagementMetricsModel`` weights ``lifecycle_statement`` at 0.5,
half of that model score was permanently zero.

The wiring is pinned twice: by parsing the ``metrics_switch`` table with ``ast``
and by executing the extracted ``lifecycle_statement`` lambda against a
recording client.  Both work without importing the heavy runtime dependencies
of ``compass_model.base_metrics_model_v2``.  A final end to end test drives
``MaintenanceManagementMetricsModel`` itself and skips itself when those runtime
dependencies (pendulum, elasticsearch, ...) are not installed.

Run from the repository root with
    python -m pytest tests/test_lifecycle_statement_index.py
or
    python -m unittest discover -s tests
"""

import ast
import datetime
import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

BASE_MODEL_FILE = os.path.join(REPO_ROOT, "compass_model", "base_metrics_model_v2.py")
SUPPLY_CHAIN_FILE = os.path.join(
    REPO_ROOT, "compass_metrics_v2", "supply_chain_security_metrics_v2.py")

LIFECYCLE_COMMAND = "lifecycle-doc-checker"

# Sentinel values instead of real index names, so a test cannot pass just
# because two attributes happen to hold the same string.
OPENCHECK_INDEX_VALUE = "opencheck-index-sentinel"
REPO_INDEX_VALUE = "repo-index-sentinel"

REPO_LIST = ["https://github.com/example/demo"]

# Every supply-chain security metric wired into ``get_metrics`` reads the
# OpenCheck raw index.  ``lifecycle_statement`` used to be the single exception.
OPENCHECK_BACKED_METRICS = (
    "compliance_copyright_statement",
    "compliance_license",
    "compliance_license_compatibility",
    "compliance_copyright_anti_tamper",
    "vulnerability_disclosure",
    "security_vulnerability",
    "dependency_reachable",
    "compliance_snippet_reference",
    "patent_risk_oin",
    "ecology_test_coverage",
    "ecology_readme",
    "ecology_build_doc",
    "ecology_interface_doc",
    "ecology_maintainer_doc",
    "trusted_build_success",
    "ci_integration",
    "build_metadata_available",
    "reproducible_build",
    "lifecycle_statement",
    "avg_vulnerability_fix_time",
    "sbom_in_release",
    "security_binary_artifact",
    "security_package_sig",
    "lifecycle_release_note",
)


def _read_source(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _metrics_switch_entries(source):
    """Return ``{metric_name: lambda_expression}`` for ``get_metrics``."""
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "metrics_switch" \
                    and isinstance(node.value, ast.Dict):
                entries = {}
                for key, value in zip(node.value.keys, node.value.values):
                    if isinstance(key, ast.Constant) and isinstance(key.value, str):
                        entries[key.value] = value
                return entries
    raise AssertionError("metrics_switch table not found in %s" % BASE_MODEL_FILE)


def _metric_function_name(expression):
    if not isinstance(expression, ast.Lambda):
        raise AssertionError("metrics_switch entry is not a lambda: %r" % expression)
    call = expression.body
    if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name):
        raise AssertionError("metrics_switch lambda does not call a named metric")
    return call.func.id


def _index_attribute(expression):
    """Return ``(receiver, attribute)`` of the index a metrics lambda passes.

    Every entry has the shape
    ``lambda: <metric_fn>(self.client, self.<index>, repo_list)``, so the second
    positional argument names the index the metric reads.
    """
    call = expression.body
    if len(call.args) < 2:
        raise AssertionError("metrics_switch lambda passes no index argument")
    index_arg = call.args[1]
    if not isinstance(index_arg, ast.Attribute) or not isinstance(index_arg.value, ast.Name):
        raise AssertionError("index argument is not a `self.<attr>` access: %r" % index_arg)
    return index_arg.value.id, index_arg.attr


def _function_arguments(path, name):
    """Return the argument names of ``name`` as declared in ``path``."""
    for node in ast.walk(ast.parse(_read_source(path), filename=path)):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return [argument.arg for argument in node.args.args]
    raise AssertionError("function %s not found in %s" % (name, path))


def _build_metric_lambda(metric_name, source, entries, namespace):
    """Compile the real ``metrics_switch`` lambda of ``metric_name``."""
    return eval(ast.get_source_segment(source, entries[metric_name]), namespace)


class _RecordingOpenCheckClient:
    """Fake Elasticsearch client that records the index of every search call.

    The fake answers a command only for the OpenCheck raw index, mirroring a
    real cluster in which repository documents have neither the ``command`` nor
    the ``label`` field that ``base_opencheck_query`` filters on.
    """

    def __init__(self, opencheck_index, lifecycle_doc=None, command=LIFECYCLE_COMMAND):
        self.opencheck_index = opencheck_index
        self.lifecycle_doc = lifecycle_doc
        self.command = command
        self.search_calls = []

    def search(self, index=None, body=None, **kwargs):
        self.search_calls.append({"index": index, "body": body})
        if index != self.opencheck_index:
            return {"hits": {"hits": []}}
        if self._requested_command(body) != self.command:
            return {"hits": {"hits": []}}
        if self.lifecycle_doc is None:
            return {"hits": {"hits": []}}
        return {"hits": {"hits": [
            {"_source": {"command_result": dict(self.lifecycle_doc)}}]}}

    def indices_queried(self):
        return [call["index"] for call in self.search_calls]

    @staticmethod
    def _requested_command(body):
        try:
            for clause in body["query"]["bool"]["must"]:
                match = clause.get("match") or {}
                if "command.keyword" in match:
                    return match["command.keyword"]
        except (AttributeError, KeyError, TypeError):
            return None
        return None


class _FakeModel:
    """Stand-in for ``BaseMetricsModel`` carrying the attributes lambdas read."""

    def __init__(self, client, repo_index=REPO_INDEX_VALUE,
                 openchecker_index=OPENCHECK_INDEX_VALUE):
        self.client = client
        self.repo_index = repo_index
        self.openchecker_index = openchecker_index


try:
    from compass_metrics_v2.supply_chain_security_metrics_v2 import (
        _fetch_command_result,
        _calc_lifecycle_statement,
        base_opencheck_query,
        lifecycle_statement,
    )
    RUNTIME_IMPORT_ERROR = None
except Exception as import_error:  # pragma: no cover - depends on the environment
    _fetch_command_result = None
    _calc_lifecycle_statement = None
    base_opencheck_query = None
    lifecycle_statement = None
    RUNTIME_IMPORT_ERROR = import_error


class MetricsSwitchIndexWiringTest(unittest.TestCase):
    """Pin the index the supply-chain security metrics are wired to."""

    @classmethod
    def setUpClass(cls):
        cls.source = _read_source(BASE_MODEL_FILE)
        cls.entries = _metrics_switch_entries(cls.source)

    def test_lifecycle_statement_reads_the_openchecker_index(self):
        self.assertEqual(
            _index_attribute(self.entries["lifecycle_statement"]),
            ("self", "openchecker_index"),
            "lifecycle_statement must query the opencheck raw index, not repo_index")

    def test_lifecycle_statement_lambda_calls_the_lifecycle_metric(self):
        self.assertEqual(_metric_function_name(self.entries["lifecycle_statement"]),
                         "lifecycle_statement")

    def test_every_opencheck_backed_metric_reads_the_openchecker_index(self):
        offenders = []
        for metric_name in OPENCHECK_BACKED_METRICS:
            self.assertIn(metric_name, self.entries,
                          "%s is missing from the metrics_switch table" % metric_name)
            if _index_attribute(self.entries[metric_name]) != ("self", "openchecker_index"):
                offenders.append(metric_name)
        self.assertEqual(offenders, [],
                         "these supply-chain metrics do not read the opencheck raw index")

    def test_lifecycle_statement_metric_declares_the_opencheck_raw_index(self):
        arguments = _function_arguments(SUPPLY_CHAIN_FILE, "lifecycle_statement")
        self.assertEqual(arguments[:2], ["client", "opencheck_raw_index"],
                         "the callee reads the opencheck raw index, so the caller must pass it")


@unittest.skipIf(RUNTIME_IMPORT_ERROR is not None,
                 "supply-chain metric dependencies are unavailable: %r"
                 % (RUNTIME_IMPORT_ERROR,))
class LifecycleStatementMetricTest(unittest.TestCase):
    """Exercise the real lambda and the real metric against a recording client."""

    @classmethod
    def setUpClass(cls):
        cls.source = _read_source(BASE_MODEL_FILE)
        cls.entries = _metrics_switch_entries(cls.source)

    def _run_lambda(self, client, openchecker_index=OPENCHECK_INDEX_VALUE,
                    repo_index=REPO_INDEX_VALUE):
        model = _FakeModel(client, repo_index=repo_index,
                           openchecker_index=openchecker_index)
        namespace = {
            "self": model,
            "date": datetime.datetime(2024, 12, 31),
            "repo_list": REPO_LIST,
            "period": "month",
            "lifecycle_statement": lifecycle_statement,
        }
        return _build_metric_lambda("lifecycle_statement", self.source,
                                    self.entries, namespace)()

    def test_lambda_queries_the_openchecker_index(self):
        client = _RecordingOpenCheckClient(OPENCHECK_INDEX_VALUE, {"has_eol": True})
        result = self._run_lambda(client)
        self.assertEqual(client.indices_queried(), [OPENCHECK_INDEX_VALUE])
        self.assertEqual(result["lifecycle_statement"], 10)
        self.assertTrue(result["lifecycle_statement_exists"])

    def test_has_eol_scores_ten(self):
        client = _RecordingOpenCheckClient(OPENCHECK_INDEX_VALUE,
                                           {"has_eol": True, "keywords_found": ["eol"]})
        result = self._run_lambda(client)
        self.assertEqual(result["lifecycle_statement"], 10)
        self.assertTrue(result["lifecycle_statement_exists"])

    def test_keywords_found_without_eol_scores_six(self):
        client = _RecordingOpenCheckClient(OPENCHECK_INDEX_VALUE,
                                           {"keywords_found": ["maintained"]})
        result = self._run_lambda(client)
        self.assertEqual(result["lifecycle_statement"], 6)
        self.assertTrue(result["lifecycle_statement_exists"])

    def test_no_document_scores_zero(self):
        client = _RecordingOpenCheckClient(OPENCHECK_INDEX_VALUE, None)
        result = self._run_lambda(client)
        self.assertEqual(client.indices_queried(), [OPENCHECK_INDEX_VALUE])
        self.assertEqual(result["lifecycle_statement"], 0)
        self.assertFalse(result["lifecycle_statement_exists"])

    def test_repeated_calls_are_stable(self):
        client = _RecordingOpenCheckClient(OPENCHECK_INDEX_VALUE, {"has_eol": True})
        first = self._run_lambda(client)
        second = self._run_lambda(client)
        self.assertEqual(first, second)
        self.assertEqual(client.indices_queried(),
                         [OPENCHECK_INDEX_VALUE, OPENCHECK_INDEX_VALUE])

    def test_repo_index_cannot_answer_the_lifecycle_query(self):
        # The regression baseline: the fake answers nothing for the repo index,
        # exactly like a real cluster, so the old wiring silently scored 0.
        client = _RecordingOpenCheckClient(OPENCHECK_INDEX_VALUE, {"has_eol": True})
        self.assertEqual(
            _fetch_command_result(client, REPO_INDEX_VALUE, REPO_LIST, LIFECYCLE_COMMAND), {})
        self.assertEqual(client.indices_queried(), [REPO_INDEX_VALUE])
        self.assertEqual(
            _fetch_command_result(client, OPENCHECK_INDEX_VALUE, REPO_LIST, LIFECYCLE_COMMAND),
            {"has_eol": True})

    def test_fetch_command_result_query_matches_the_command_and_label(self):
        client = _RecordingOpenCheckClient(OPENCHECK_INDEX_VALUE, {"has_eol": True})
        _fetch_command_result(client, OPENCHECK_INDEX_VALUE, REPO_LIST, LIFECYCLE_COMMAND)
        body = client.search_calls[0]["body"]
        self.assertEqual(body, base_opencheck_query(REPO_LIST, LIFECYCLE_COMMAND))

    def test_calc_lifecycle_statement_scores_the_empty_result(self):
        empty = _calc_lifecycle_statement({})
        self.assertEqual(empty["lifecycle_statement"], 0)
        self.assertFalse(empty["lifecycle_statement_exists"])


try:
    from compass_model_v2.supply_chain_security.release_and_maintenance.maintenance_management_metrics_model import (
        MaintenanceManagementMetricsModel,
    )
    MODEL_IMPORT_ERROR = None
except Exception as import_error:  # pragma: no cover - depends on the environment
    MaintenanceManagementMetricsModel = None
    MODEL_IMPORT_ERROR = import_error


@unittest.skipIf(MODEL_IMPORT_ERROR is not None,
                 "compass_model runtime dependencies are unavailable: %r"
                 % (MODEL_IMPORT_ERROR,))
class MaintenanceManagementMetricsModelTest(unittest.TestCase):
    """End to end check through the model that consumes the metric."""

    def _build_model(self, client):
        model = MaintenanceManagementMetricsModel(
            repo_index=REPO_INDEX_VALUE,
            git_index="git-index-sentinel",
            issue_index="issue-index-sentinel",
            pr_index="pr-index-sentinel",
            issue_comments_index="issue-comments-index-sentinel",
            pr_comments_index="pr-comments-index-sentinel",
            contributors_index="contributors-index-sentinel",
            release_index="release-index-sentinel",
            out_index="out-index-sentinel",
            from_date="2024-01-01",
            end_date="2024-12-31",
            level="repo",
            community="example",
            source="github",
            json_file="projects-github-pytorch.json",
            contributors_enriched_index="contributors-enriched-index-sentinel",
            custom_fields={"period": "month"},
            openchecker_index=OPENCHECK_INDEX_VALUE,
        )
        model.client = client
        return model

    def _lifecycle_calls(self, client):
        return [call for call in client.search_calls
                if _RecordingOpenCheckClient._requested_command(call["body"]) == LIFECYCLE_COMMAND]

    def test_get_metrics_reads_lifecycle_statement_from_the_openchecker_index(self):
        client = _RecordingOpenCheckClient(OPENCHECK_INDEX_VALUE, {"has_eol": True})
        model = self._build_model(client)
        metrics, _ = model.get_metrics(datetime.datetime(2024, 12, 31), REPO_LIST)
        lifecycle_calls = self._lifecycle_calls(client)
        self.assertTrue(lifecycle_calls)
        self.assertEqual({call["index"] for call in lifecycle_calls},
                         {OPENCHECK_INDEX_VALUE})
        self.assertEqual(metrics["lifecycle_statement"], 10)
        self.assertTrue(metrics["lifecycle_statement_exists"])

    def test_get_metrics_keywords_only_scores_six(self):
        client = _RecordingOpenCheckClient(OPENCHECK_INDEX_VALUE,
                                           {"keywords_found": ["maintained"]})
        model = self._build_model(client)
        metrics, _ = model.get_metrics(datetime.datetime(2024, 12, 31), REPO_LIST)
        self.assertEqual(metrics["lifecycle_statement"], 6)
        self.assertTrue(metrics["lifecycle_statement_exists"])

    def test_get_metrics_without_document_scores_zero(self):
        client = _RecordingOpenCheckClient(OPENCHECK_INDEX_VALUE, None)
        model = self._build_model(client)
        metrics, _ = model.get_metrics(datetime.datetime(2024, 12, 31), REPO_LIST)
        self.assertEqual(metrics["lifecycle_statement"], 0)
        self.assertFalse(metrics["lifecycle_statement_exists"])
        lifecycle_calls = self._lifecycle_calls(client)
        self.assertTrue(lifecycle_calls)
        self.assertEqual({call["index"] for call in lifecycle_calls},
                         {OPENCHECK_INDEX_VALUE})


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
