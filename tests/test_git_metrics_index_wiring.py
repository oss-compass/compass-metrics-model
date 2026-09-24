"""Regression tests for the Elasticsearch index wiring of the by_period metrics.

``BaseMetricsModel.get_metrics`` builds a ``metrics_switch`` table of zero
argument lambdas and every lambda passes the index that its metric function
actually reads.  The table is hand written, so a metric is easy to wire to the
wrong index - which is what happened to the two git metrics:

* ``commit_count_by_period`` (``compass_metrics_v2/git_metrics_v2.py``) aggregates
  ``cardinality(hash)`` over commit documents, filtered by the git ``tag`` field
  and with ``.git`` appended to every repository name.
* ``lines_changed_by_period`` sums ``lines_added`` / ``lines_removed`` from the
  same commit documents.

Both were wired to ``self.contributors_enriched_index``
(``github-contributors_org_repo_enriched``).  The documents written by
``contributor_enrich`` only carry ``uuid``, ``contributor``, ``contribution``,
``contribution_without_observe``, ``ecological_type``, ``organization``,
``contribution_type_list``, ``is_bot``, ``repo_name`` and
``grimoire_creation_date`` - none of ``tag``, ``hash``, ``lines_added`` or
``lines_removed``.  The ``terms`` filter on ``tag`` therefore matched nothing and
both metrics silently returned 0, so ``ContributionActivityMetricsModel`` always
scored 0 for two of its five metrics while still charging their weights.

The wiring is pinned twice: by parsing ``metrics_switch`` with ``ast`` and by
executing the extracted lambda expressions against fakes.  The heavy runtime
dependencies of ``compass_model.base_metrics_model_v2`` (Elasticsearch, pendulum,
...) are only imported by the end to end test, which skips itself when they are
unavailable.

Run from the repository root with
    python -m pytest tests/test_git_metrics_index_wiring.py
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
GIT_METRICS_FILE = os.path.join(REPO_ROOT, "compass_metrics_v2", "git_metrics_v2.py")
CONTRIBUTOR_ENRICH_FILE = os.path.join(
    REPO_ROOT, "compass_contributor", "contributor_dev_org_repo.py")

GIT_INDEX_ATTR = "git_index"
CONTRIBUTORS_ENRICHED_INDEX_ATTR = "contributors_enriched_index"
ISSUE_INDEX_ATTR = "issue_index"
PR_INDEX_ATTR = "pr_index"

# Sentinel values instead of real index names so a test cannot pass just because
# two attributes happen to hold the same string.
GIT_INDEX_VALUE = "git-index-sentinel"
ENRICHED_INDEX_VALUE = "enriched-index-sentinel"
ISSUE_INDEX_VALUE = "issue-index-sentinel"
PR_INDEX_VALUE = "pr-index-sentinel"
REPO_INDEX_VALUE = "repo-index-sentinel"

# Aggregations the fake git index answers with.
GIT_COMMIT_COUNT = 42
GIT_LINES_ADDED = 120
GIT_LINES_REMOVED = 30

# Fields that only exist on the commit documents of the git index.
GIT_ONLY_FIELDS = {"tag", "hash", "lines_added", "lines_removed"}

# The enriched contributor metrics read repo_name / contribution / organization,
# so they must keep using the enriched contributor index.
CONTRIBUTOR_ENRICHED_METRICS = (
    "total_active_contributors_by_period",
    "code_contributors_by_period",
    "non_code_contributors_by_period",
    "followers_by_period",
)


def _read_source(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _parse(path):
    return ast.parse(_read_source(path), filename=path)


def _metrics_switch_entries(path):
    """Return {metric_name: lambda_expression} for BaseMetricsModel.get_metrics."""
    for node in ast.walk(_parse(path)):
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
    raise AssertionError("metrics_switch table not found in %s" % path)


def _metric_function_name(expression):
    if not isinstance(expression, ast.Lambda):
        raise AssertionError("metrics_switch entry is not a lambda: %r" % expression)
    call = expression.body
    if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name):
        raise AssertionError("metrics_switch lambda does not call a named metric")
    return call.func.id


def _index_attribute(expression):
    """Return the ``self.<attr>`` index argument of a metrics_switch lambda.

    Every entry has the shape
    ``lambda: <metric_fn>(self.client, self.<index>, date, repo_list, period)``,
    so the second positional argument names the index the metric reads.
    """
    call = expression.body
    if len(call.args) < 2:
        raise AssertionError("metrics_switch lambda passes no index argument")
    index_arg = call.args[1]
    if not isinstance(index_arg, ast.Attribute) or not isinstance(index_arg.value, ast.Name):
        raise AssertionError("index argument is not a `self.<attr>` access: %r" % index_arg)
    return index_arg.value.id, index_arg.attr


def _function_definitions(path):
    return {node.name: node for node in ast.walk(_parse(path))
            if isinstance(node, ast.FunctionDef)}


def _string_constants(node):
    return {child.value for child in ast.walk(node)
            if isinstance(child, ast.Constant) and isinstance(child.value, str)}


def _search_index_arguments(function_node):
    """Return the names passed as ``index=`` to ``client.search`` calls."""
    names = set()
    for child in ast.walk(function_node):
        if not isinstance(child, ast.Call):
            continue
        if not isinstance(child.func, ast.Attribute) or child.func.attr != "search":
            continue
        for keyword in child.keywords:
            if keyword.arg == "index" and isinstance(keyword.value, ast.Name):
                names.add(keyword.value.id)
    return names


def _contributor_enrich_source_keys(path):
    """Return the ``_source`` keys written by ``contributor_enrich``."""
    function = _function_definitions(path).get("contributor_enrich")
    if function is None:
        raise AssertionError("contributor_enrich not found in %s" % path)
    keys = set()
    for child in ast.walk(function):
        if not isinstance(child, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "contributor_data"
                   for target in child.targets):
            continue
        if not isinstance(child.value, ast.Dict):
            continue
        for key, value in zip(child.value.keys, child.value.values):
            if isinstance(key, ast.Constant) and key.value == "_source" \
                    and isinstance(value, ast.Dict):
                for source_key in value.keys:
                    if isinstance(source_key, ast.Constant):
                        keys.add(source_key.value)
    return keys


class _RecordingMetric:
    """Callable metric that records the index it is handed."""

    def __init__(self, recorded):
        self.recorded = recorded

    def __call__(self, client, index, end_date, repos_list, period="month"):
        self.recorded.append(index)
        return {"index": index}


class _FakeModel:
    """Stand-in for BaseMetricsModel carrying the attributes the lambdas read."""

    def __init__(self, client, **indexes):
        self.client = client
        for name, value in indexes.items():
            setattr(self, name, value)


class _GitOnlyFakeClient:
    """Fake client that answers aggregations only for the git index.

    The enriched contributor index stores neither ``tag`` nor ``hash`` nor
    ``lines_added`` / ``lines_removed``, so a real cluster answers every
    aggregation against it with 0; the fake mirrors that so a wrong wiring cannot
    accidentally look healthy.
    """

    def __init__(self, git_index, commit_count=GIT_COMMIT_COUNT,
                 lines_added=GIT_LINES_ADDED, lines_removed=GIT_LINES_REMOVED):
        self.git_index = git_index
        self.commit_count = commit_count
        self.lines_added = lines_added
        self.lines_removed = lines_removed
        self.queries = []

    def aggregation(self, index, field):
        self.queries.append((index, field))
        if index != self.git_index:
            return 0
        return {
            "hash": self.commit_count,
            "lines_added": self.lines_added,
            "lines_removed": self.lines_removed,
        }.get(field, 0)


def _fake_commit_count_by_period(client, git_index, end_date, repos_list, period="month"):
    """Mirror of compass_metrics_v2.git_metrics_v2.commit_count_by_period."""
    return {"commit_count": client.aggregation(git_index, "hash"), "period": period}


def _fake_lines_changed_by_period(client, git_index, end_date, repos_list, period="month"):
    """Mirror of compass_metrics_v2.git_metrics_v2.lines_changed_by_period."""
    return {
        "lines_added": client.aggregation(git_index, "lines_added"),
        "lines_removed": client.aggregation(git_index, "lines_removed"),
        "period": period,
    }


FAKE_GIT_METRICS = {
    "commit_count_by_period": _fake_commit_count_by_period,
    "lines_changed_by_period": _fake_lines_changed_by_period,
}


def _build_lambda(metric_name, source, entries, namespace):
    """Compile the real metrics_switch lambda of metric_name inside namespace."""
    expression = entries[metric_name]
    return eval(ast.get_source_segment(source, expression), namespace)


def _run_metric(metric_name, source, entries, model, fakes=None):
    """Run the real metrics_switch lambda and return its result."""
    namespace = {
        "self": model,
        "date": datetime.datetime(2024, 12, 31),
        "repo_list": ["https://github.com/example/demo"],
        "period": "month",
    }
    namespace.update(fakes or {})
    function_name = _metric_function_name(entries[metric_name])
    namespace.setdefault(function_name, _RecordingMetric([]))
    return _build_lambda(metric_name, source, entries, namespace)()


class MetricsSwitchWiringTest(unittest.TestCase):
    """Pin the index each by_period metric of get_metrics is wired to."""

    @classmethod
    def setUpClass(cls):
        cls.source = _read_source(BASE_MODEL_FILE)
        cls.entries = _metrics_switch_entries(BASE_MODEL_FILE)
        cls.model = _FakeModel(
            client=object(),
            git_index=GIT_INDEX_VALUE,
            contributors_enriched_index=ENRICHED_INDEX_VALUE,
            issue_index=ISSUE_INDEX_VALUE,
            pr_index=PR_INDEX_VALUE,
            repo_index=REPO_INDEX_VALUE,
        )

    def _recorded_index(self, metric_name):
        recorded = []
        namespace = {
            "self": self.model,
            "date": datetime.datetime(2024, 12, 31),
            "repo_list": ["https://github.com/example/demo"],
            "period": "month",
        }
        namespace[_metric_function_name(self.entries[metric_name])] = _RecordingMetric(recorded)
        _build_lambda(metric_name, self.source, self.entries, namespace)()
        self.assertEqual(len(recorded), 1, "%s was not called exactly once" % metric_name)
        return recorded[0]

    def test_git_period_metrics_use_the_git_index(self):
        for metric_name in ("commit_count_by_period", "lines_changed_by_period"):
            self.assertIn(metric_name, self.entries)
            owner, attribute = _index_attribute(self.entries[metric_name])
            self.assertEqual(owner, "self")
            self.assertEqual(
                attribute, GIT_INDEX_ATTR,
                "%s aggregates commit fields (tag/hash/lines_added/lines_removed) "
                "and must read the git index" % metric_name)
            self.assertEqual(self._recorded_index(metric_name), GIT_INDEX_VALUE)

    def test_contributor_period_metrics_keep_the_enriched_index(self):
        for metric_name in CONTRIBUTOR_ENRICHED_METRICS:
            self.assertIn(metric_name, self.entries)
            _, attribute = _index_attribute(self.entries[metric_name])
            self.assertEqual(
                attribute, CONTRIBUTORS_ENRICHED_INDEX_ATTR,
                "%s reads repo_name/contribution documents, so it must keep using "
                "the enriched contributor index" % metric_name)
            self.assertEqual(self._recorded_index(metric_name), ENRICHED_INDEX_VALUE)

    def test_issue_period_metrics_use_the_issue_index(self):
        for metric_name in ("issue_comment_activity_by_period", "issue_new_count_by_period"):
            self.assertIn(metric_name, self.entries)
            _, attribute = _index_attribute(self.entries[metric_name])
            self.assertEqual(attribute, ISSUE_INDEX_ATTR)

    def test_pr_comment_count_uses_the_pull_request_index(self):
        self.assertIn("pr_comment_count_by_period", self.entries)
        _, attribute = _index_attribute(self.entries["pr_comment_count_by_period"])
        self.assertEqual(
            attribute, PR_INDEX_ATTR,
            "pr_comment_count_by_period aggregates num_review_comments_without_bot on "
            "pull-request documents, so it must read the pull-request index")
        self.assertEqual(self._recorded_index("pr_comment_count_by_period"), PR_INDEX_VALUE)


class GitMetricFunctionContractTest(unittest.TestCase):
    """The git metric functions themselves only make sense against the git index."""

    @classmethod
    def setUpClass(cls):
        cls.functions = _function_definitions(GIT_METRICS_FILE)

    def test_second_parameter_is_named_git_index(self):
        for function_name in ("commit_count_by_period", "lines_changed_by_period"):
            function = self.functions.get(function_name)
            self.assertIsNotNone(function, "%s is missing" % function_name)
            self.assertGreaterEqual(len(function.args.args), 2)
            self.assertEqual(function.args.args[1].arg, "git_index")

    def test_queries_target_the_git_index(self):
        for function_name in ("commit_count_by_period", "lines_changed_by_period"):
            self.assertIn("git_index",
                          _search_index_arguments(self.functions[function_name]),
                          "%s must query the index it was handed" % function_name)

    def test_aggregated_fields_are_commit_fields(self):
        commit_fields = _string_constants(self.functions["commit_count_by_period"])
        self.assertIn("hash", commit_fields)
        line_fields = _string_constants(self.functions["lines_changed_by_period"])
        self.assertIn("lines_added", line_fields)
        self.assertIn("lines_removed", line_fields)


class ContributorEnrichDocumentShapeTest(unittest.TestCase):
    """The enriched index cannot answer git aggregations - it has no such fields."""

    @classmethod
    def setUpClass(cls):
        cls.keys = _contributor_enrich_source_keys(CONTRIBUTOR_ENRICH_FILE)

    def test_source_documents_carry_contributor_fields_only(self):
        for expected in ("uuid", "contributor", "contribution", "organization",
                         "repo_name", "grimoire_creation_date"):
            self.assertIn(expected, self.keys)

    def test_source_documents_have_no_git_fields(self):
        self.assertEqual(self.keys & GIT_ONLY_FIELDS, set(),
                         "the enriched contributor index gained git fields; the git "
                         "metrics wiring would no longer be justified by this test")


class GitMetricsDispatchTest(unittest.TestCase):
    """Run the real lambdas end to end against a fake git-only client."""

    @classmethod
    def setUpClass(cls):
        cls.source = _read_source(BASE_MODEL_FILE)
        cls.entries = _metrics_switch_entries(BASE_MODEL_FILE)

    def _model(self, client):
        return _FakeModel(
            client=client,
            git_index=GIT_INDEX_VALUE,
            contributors_enriched_index=ENRICHED_INDEX_VALUE,
            issue_index=ISSUE_INDEX_VALUE,
            pr_index=PR_INDEX_VALUE,
            repo_index=REPO_INDEX_VALUE,
        )

    def test_git_metrics_report_non_zero_values(self):
        client = _GitOnlyFakeClient(GIT_INDEX_VALUE)
        model = self._model(client)
        metrics = {}
        for metric_name in ("commit_count_by_period", "lines_changed_by_period"):
            metrics.update(_run_metric(metric_name, self.source, self.entries,
                                       model, FAKE_GIT_METRICS))
        self.assertEqual(metrics["commit_count"], GIT_COMMIT_COUNT)
        self.assertEqual(metrics["lines_added"], GIT_LINES_ADDED)
        self.assertEqual(metrics["lines_removed"], GIT_LINES_REMOVED)

    def test_git_metrics_query_the_git_index_only(self):
        client = _GitOnlyFakeClient(GIT_INDEX_VALUE)
        model = self._model(client)
        for metric_name in ("commit_count_by_period", "lines_changed_by_period"):
            _run_metric(metric_name, self.source, self.entries, model, FAKE_GIT_METRICS)
        self.assertTrue(client.queries)
        self.assertEqual({index for index, _ in client.queries}, {GIT_INDEX_VALUE})

    def test_enriched_index_cannot_answer_the_git_aggregations(self):
        client = _GitOnlyFakeClient(GIT_INDEX_VALUE)
        for field in ("hash", "lines_added", "lines_removed"):
            self.assertEqual(client.aggregation(ENRICHED_INDEX_VALUE, field), 0)


class _SearchFakeClient:
    """Fake Elasticsearch client implementing the search() call shape."""

    def __init__(self, git_index, commit_count=GIT_COMMIT_COUNT,
                 lines_added=GIT_LINES_ADDED, lines_removed=GIT_LINES_REMOVED):
        self.git_index = git_index
        self.commit_count = commit_count
        self.lines_added = lines_added
        self.lines_removed = lines_removed
        self.search_calls = []

    def search(self, index=None, body=None, **kwargs):
        self.search_calls.append({"index": index, "body": body})
        if index != self.git_index:
            return {"aggregations": {"count_of_uuid": {"value": 0}},
                    "hits": {"total": {"value": 0}}}
        field = None
        aggregation = (body or {}).get("aggs", {}).get("count_of_uuid", {})
        for specification in aggregation.values():
            if isinstance(specification, dict) and "field" in specification:
                field = specification["field"]
        value = {"hash": self.commit_count,
                 "lines_added": self.lines_added,
                 "lines_removed": self.lines_removed}.get(field, 0)
        return {"aggregations": {"count_of_uuid": {"value": value}},
                "hits": {"total": {"value": 1}}}


try:
    from compass_model_v2.community_health.community_vitality.contribution_activity_metrics_model import (
        ContributionActivityMetricsModel,
    )
    RUNTIME_IMPORT_ERROR = None
except Exception as import_error:  # pragma: no cover - depends on the local environment
    ContributionActivityMetricsModel = None
    RUNTIME_IMPORT_ERROR = import_error


@unittest.skipIf(RUNTIME_IMPORT_ERROR is not None,
                 "compass_model runtime dependencies are unavailable: %r"
                 % (RUNTIME_IMPORT_ERROR,))
class ContributionActivityMetricsModelTest(unittest.TestCase):
    """End to end check through the model that consumes the two metrics."""

    def _build_model(self, client):
        model = ContributionActivityMetricsModel(
            repo_index="github-repo_enriched",
            git_index=GIT_INDEX_VALUE,
            issue_index=ISSUE_INDEX_VALUE,
            pr_index=PR_INDEX_VALUE,
            issue_comments_index="github2-issues_enriched",
            pr_comments_index="github2-pulls_enriched",
            contributors_index="github-contributors_org_repo",
            release_index="github-repo_release_enriched",
            out_index="v2_metric_model_test",
            from_date="2024-01-01",
            end_date="2024-12-31",
            level="repo",
            community="pytorch",
            source="github",
            json_file="projects-github-pytorch.json",
            contributors_enriched_index=ENRICHED_INDEX_VALUE,
            custom_fields={"period": "month"},
        )
        model.client = client
        return model

    def test_get_metrics_reports_non_zero_git_metrics(self):
        client = _SearchFakeClient(GIT_INDEX_VALUE)
        model = self._build_model(client)
        metrics, _ = model.get_metrics(datetime.datetime(2024, 12, 31),
                                       ["https://github.com/example/demo"])
        self.assertEqual(metrics["commit_count"], GIT_COMMIT_COUNT)
        self.assertEqual(metrics["lines_added"], GIT_LINES_ADDED)
        self.assertEqual(metrics["lines_removed"], GIT_LINES_REMOVED)

    def test_get_metrics_queries_the_git_index_for_git_metrics(self):
        client = _SearchFakeClient(GIT_INDEX_VALUE)
        model = self._build_model(client)
        model.get_metrics(datetime.datetime(2024, 12, 31),
                          ["https://github.com/example/demo"])
        git_calls = [call for call in client.search_calls if call["index"] == GIT_INDEX_VALUE]
        self.assertEqual(len(git_calls), 3,
                         "commit_count, lines_added and lines_removed must all hit the git index")
