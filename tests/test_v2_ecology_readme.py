from unittest.mock import Mock

from compass_metrics_v2.supply_chain_security_metrics_v2 import ecology_readme


def _client(readme_files=None, oat=None):
    def search(index, body):
        command = body["query"]["bool"]["must"][0]["match"]["command.keyword"]
        results = {
            "readme-checker": {"readme_file": readme_files} if readme_files is not None else None,
            "oat-scanner": oat,
        }
        result = results[command]
        return {"hits": {"hits": [{"_source": {"command_result": result}}] if result else []}}

    return Mock(search=Mock(side_effect=search))


def test_missing_readme_does_not_receive_full_credit():
    assert ecology_readme(_client([]), "opencheck", ["repo"])["ecology_readme"] == 0
    assert ecology_readme(_client(), "opencheck", ["repo"])["ecology_readme"] == 0


def test_root_readme_receives_credit():
    assert ecology_readme(_client(["repo/README.md"]), "opencheck", ["repo"])["ecology_readme"] == 10


def test_oat_failure_overrides_readme_checker():
    oat = {"status_code": 200, "No Readme": {"total_count": 1}}
    assert ecology_readme(_client(["repo/README.md"], oat), "opencheck", ["repo"])["ecology_readme"] == 0
