"""Exercise the complete release-index entrypoint without external services."""

import argparse
import copy
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import sys
import tempfile
import types
import unittest
from unittest import mock


SOURCE_PATH = Path(__file__).resolve().parents[1] / "tools" / "release_index.py"
REPO_URL = "https://gitee.com/mindspore/mindspore"
CONFIG = {
    "HOST": "search.invalid",
    "PORT": 443,
    "USER": "fixture-user",
    "PASSWD": "fixture-only",
}
EXPECTED_QUERY = {
    "query": {"match": {"tag": REPO_URL}},
    "sort": [{"metadata__updated_on": {"order": "desc"}}],
}
RELEASES = [
    {
        "id": 101,
        "tag_name": "v1.0",
        "target_commitish": "main",
        "prerelease": False,
        "name": "First release",
        "body": "Release one",
        "author": {"login": "alice", "name": "Alice"},
        "created_at": "2026-01-02T03:04:05Z",
    },
    {
        "id": 202,
        "tag_name": "v2.0-rc1",
        "target_commitish": "release/2",
        "prerelease": True,
        "name": "Second release",
        "body": "Release two\nDetails",
        "author": {"login": "bob", "name": None},
        "created_at": "2026-02-03T04:05:06Z",
    },
]
EXPECTED_ACTIONS = [
    {
        "_index": "repo_release_enriched",
        "_id": "fixture-uuid-101",
        "_source": {
            "uuid": "fixture-uuid-101",
            "id": 101,
            "tag": REPO_URL,
            "tag_name": "v1.0",
            "target_commitish": "main",
            "prerelease": False,
            "name": "First release",
            "body": "Release one",
            "author_login": "alice",
            "author_name": "Alice",
            "grimoire_creation_date": "2026-01-02T03:04:05Z",
        },
    },
    {
        "_index": "repo_release_enriched",
        "_id": "fixture-uuid-202",
        "_source": {
            "uuid": "fixture-uuid-202",
            "id": 202,
            "tag": REPO_URL,
            "tag_name": "v2.0-rc1",
            "target_commitish": "release/2",
            "prerelease": True,
            "name": "Second release",
            "body": "Release two\nDetails",
            "author_login": "bob",
            "author_name": None,
            "grimoire_creation_date": "2026-02-03T04:05:06Z",
        },
    },
]


class ReleaseIndexEntrypointTests(unittest.TestCase):
    @contextmanager
    def isolated_dependencies(self, releases):
        """Replace only imported service/UUID boundaries, not product functions."""
        source_before = SOURCE_PATH.read_bytes()
        source_sha = hashlib.sha256(source_before).hexdigest()
        client = mock.Mock(name="constructed_opensearch_client")
        client.search.return_value = {
            "hits": {"hits": [{"_source": {"releases": copy.deepcopy(releases)}}]}
        }
        constructor = mock.Mock(name="OpenSearch", return_value=client)
        bulk = mock.Mock(name="bulk", return_value=(len(releases), []))
        uuid_values = {"101": "fixture-uuid-101", "202": "fixture-uuid-202"}
        uuid = mock.Mock(name="perceval_uuid", side_effect=uuid_values.__getitem__)

        opensearch = types.ModuleType("opensearchpy")
        opensearch.__path__ = []
        opensearch.OpenSearch = constructor
        helpers = types.ModuleType("opensearchpy.helpers")
        helpers.bulk = bulk
        opensearch.helpers = helpers
        perceval = types.ModuleType("perceval")
        perceval.__path__ = []
        backend = types.ModuleType("perceval.backend")
        backend.uuid = uuid
        perceval.backend = backend

        temporary = Path(tempfile.mkdtemp(prefix="release-index-entrypoint-")).resolve()
        previous_cwd = Path.cwd()
        config_path = temporary / "opensearch_message.json"
        config_bytes = (json.dumps(CONFIG, sort_keys=True) + "\n").encode("utf-8")
        try:
            config_path.write_bytes(config_bytes)
            os.chdir(temporary)
            with mock.patch.dict(
                sys.modules,
                {
                    "opensearchpy": opensearch,
                    "opensearchpy.helpers": helpers,
                    "perceval": perceval,
                    "perceval.backend": backend,
                },
            ):
                yield types.SimpleNamespace(
                    client=client,
                    constructor=constructor,
                    bulk=bulk,
                    uuid=uuid,
                )
        finally:
            os.chdir(previous_cwd)
            try:
                self.assertEqual(SOURCE_PATH.read_bytes(), source_before)
                self.assertEqual(
                    hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest(), source_sha
                )
                self.assertEqual(config_path.read_bytes(), config_bytes)
            finally:
                target = temporary.resolve()
                temp_root = Path(tempfile.gettempdir()).resolve()
                relative = target.relative_to(temp_root)
                if not relative.parts:
                    raise RuntimeError("Refusing to remove the temporary root")
                shutil.rmtree(target)

    def assert_constructor_and_search(self, boundary):
        boundary.constructor.assert_called_once_with(
            hosts=[{"host": "search.invalid", "port": 443}],
            http_compress=True,
            http_auth=("fixture-user", "fixture-only"),
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )
        boundary.client.search.assert_called_once_with(
            index="gitee_repo-enriched", body=EXPECTED_QUERY
        )

    def test_entrypoint_imports_releases_with_the_constructed_client(self):
        with self.isolated_dependencies(RELEASES) as boundary:
            namespace = runpy.run_path(str(SOURCE_PATH), run_name="__main__")
            self.assertIs(namespace["opensearch_client"], boundary.client)
            self.assertEqual(namespace["query"], EXPECTED_QUERY)
            self.assert_constructor_and_search(boundary)
            boundary.bulk.assert_called_once()
            self.assertIs(boundary.bulk.call_args.kwargs["client"], boundary.client)
            self.assertEqual(
                boundary.bulk.call_args.kwargs["actions"], EXPECTED_ACTIONS
            )
            self.assertEqual(
                boundary.uuid.call_args_list,
                [mock.call("101"), mock.call("101"), mock.call("202"), mock.call("202")],
            )

    def test_entrypoint_preserves_the_empty_release_batch(self):
        with self.isolated_dependencies([]) as boundary:
            namespace = runpy.run_path(str(SOURCE_PATH), run_name="__main__")
            self.assertIs(namespace["opensearch_client"], boundary.client)
            self.assertEqual(namespace["query"], EXPECTED_QUERY)
            self.assert_constructor_and_search(boundary)
            boundary.bulk.assert_called_once_with(client=boundary.client, actions=[])
            self.assertIs(boundary.bulk.call_args.kwargs["client"], boundary.client)
            boundary.uuid.assert_not_called()

    def test_import_and_real_query_helper_do_not_contact_services(self):
        with self.isolated_dependencies(RELEASES) as boundary:
            namespace = runpy.run_path(
                str(SOURCE_PATH), run_name="release_index_regression_import"
            )
            self.assertEqual(namespace["newest_message"](REPO_URL), EXPECTED_QUERY)
            boundary.constructor.assert_not_called()
            boundary.client.search.assert_not_called()
            boundary.bulk.assert_not_called()
            boundary.uuid.assert_not_called()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--source", type=Path, default=SOURCE_PATH)
    options, unittest_args = parser.parse_known_args()
    SOURCE_PATH = options.source.resolve(strict=True)
    unittest.main(argv=[sys.argv[0]] + unittest_args)
