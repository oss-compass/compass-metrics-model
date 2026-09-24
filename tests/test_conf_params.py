"""Tests for the conf.yaml handling of the entry scripts and for the
deployment documentation that goes with it.

The cases below mirror the two setup problems that were reported most often:

* a ``conf.yaml`` that does not define every parameter - the README used to
  show only a subset of them, and ``run.py`` aborted with a bare ``KeyError``;
* an installation on an interpreter that is too old for ``grimoirelab-elk``,
  which fails with a ``gcc`` error instead of a version message.

Both are covered here so that they cannot come back unnoticed: the behaviour of
``compass_common.conf_utils`` is asserted directly, and the README/setup.py
consistency checks fail as soon as the documentation and the code disagree.
"""
import ast
import logging
import os

import pytest

from compass_common.conf_utils import ConfError, build_kwargs, normalize_param, read_conf

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN_PY = os.path.join(REPO_ROOT, 'run.py')
README = os.path.join(REPO_ROOT, 'README.md')
SETUP_PY = os.path.join(REPO_ROOT, 'setup.py')
REQUIREMENTS = os.path.join(REPO_ROOT, 'requirements.txt')
CONF_TEMPLATE = 'conf-github.yaml'


def read_text(path):
    with open(path, encoding='utf-8') as handle:
        return handle.read()


class TestNormalizeParam:
    """conf.yaml spells "no value" in several ways; all of them mean None."""

    def test_none_stays_none(self):
        assert normalize_param(None) is None

    @pytest.mark.parametrize('value', ['None', 'none', 'NONE', 'null', '~', '', '   '])
    def test_empty_values_become_none(self, value):
        assert normalize_param(value) is None

    @pytest.mark.parametrize('value', ['github-issues_enriched', '2024-01-01', 'repo',
                                       'pytorch', 'Facebook'])
    def test_real_values_are_kept(self, value):
        assert normalize_param(value) == value

    def test_non_string_values_are_kept(self):
        assert normalize_param(0) == 0
        assert normalize_param(False) is False
        assert normalize_param({'period': 'month'}) == {'period': 'month'}


class TestBuildKwargs:
    """The keyword arguments handed over to a metrics model."""

    def test_every_requested_key_is_present(self):
        kwargs = build_kwargs({'issue_index': 'issues_enriched'}, ['issue_index', 'pr_index'])
        assert kwargs == {'issue_index': 'issues_enriched', 'pr_index': None}

    def test_short_configuration_does_not_raise(self):
        # run.py looked up params[item] for every key it knew about, so a
        # conf.yaml written from the README example aborted with a KeyError.
        params = {'json_file': 'projects-github-pytorch.json', 'from_date': '2024-01-01'}
        kwargs = build_kwargs(params, ['json_file', 'from_date', 'stargazer_index', 'fork_index'])
        assert kwargs['json_file'] == 'projects-github-pytorch.json'
        assert kwargs['from_date'] == '2024-01-01'
        assert kwargs['stargazer_index'] is None
        assert kwargs['fork_index'] is None

    def test_the_none_string_is_normalised(self):
        kwargs = build_kwargs({'company': 'None'}, ['company'])
        assert kwargs['company'] is None

    def test_missing_optional_parameters_are_logged(self, caplog):
        with caplog.at_level(logging.WARNING):
            build_kwargs({'issue_index': 'issues_enriched'}, ['issue_index', 'fork_index'],
                         conf_url='conf.yaml')
        assert 'fork_index' in caplog.text

    def test_unset_required_parameter_raises_a_readable_error(self):
        with pytest.raises(ConfError) as error:
            build_kwargs({'issue_index': 'issues_enriched'}, ['issue_index', 'json_file'],
                         required_keys=('issue_index', 'json_file'), conf_url='conf.yaml')
        assert 'json_file' in str(error.value)
        assert 'conf.yaml' in str(error.value)

    def test_required_parameter_written_as_none_raises(self):
        with pytest.raises(ConfError) as error:
            build_kwargs({'out_index': 'None'}, ['out_index'], required_keys=('out_index',))
        assert 'out_index' in str(error.value)

    def test_params_has_to_be_a_mapping(self):
        with pytest.raises(ConfError):
            build_kwargs(None, ['issue_index'])
        with pytest.raises(ConfError):
            build_kwargs(['issue_index'], ['issue_index'])


class TestReadConf:
    """read_conf turns the usual setup mistakes into one clear message."""

    def write_conf(self, tmp_path, content):
        conf_file = tmp_path / 'conf.yaml'
        conf_file.write_text(content, encoding='utf-8')
        return str(conf_file)

    def test_missing_file_points_at_the_template(self, tmp_path):
        with pytest.raises(ConfError) as error:
            read_conf(str(tmp_path / 'conf.yaml'))
        assert CONF_TEMPLATE in str(error.value)
        assert 'README.md' in str(error.value)

    def test_valid_file_returns_url_and_params(self, tmp_path):
        conf_url = self.write_conf(tmp_path,
                                   'url: "http://localhost:9200"\n'
                                   'params:\n'
                                   '  {"issue_index": "issues_enriched"}\n')
        elastic_url, params = read_conf(conf_url)
        assert elastic_url == 'http://localhost:9200'
        assert params == {'issue_index': 'issues_enriched'}

    def test_broken_yaml_is_reported(self, tmp_path):
        conf_url = self.write_conf(tmp_path, 'url: "http://localhost:9200"\nparams: [\n')
        with pytest.raises(ConfError):
            read_conf(conf_url)

    def test_missing_params_section_is_reported(self, tmp_path):
        conf_url = self.write_conf(tmp_path, 'url: "http://localhost:9200"\n')
        with pytest.raises(ConfError) as error:
            read_conf(conf_url)
        assert 'params' in str(error.value)

    def test_missing_url_is_reported(self, tmp_path):
        conf_url = self.write_conf(tmp_path, 'url:\nparams:\n  {"issue_index": "issues"}\n')
        with pytest.raises(ConfError) as error:
            read_conf(conf_url)
        assert 'url' in str(error.value)


def elements_strings(node):
    """String constants of a tuple/list literal; empty for anything else."""
    if not isinstance(node, (ast.Tuple, ast.List)):
        return set()
    return set(element.value for element in node.elts
               if isinstance(element, ast.Constant) and isinstance(element.value, str))


def run_py_parameter_names():
    """Names of the conf.yaml parameters that run.py forwards to the models."""
    tree = ast.parse(read_text(RUN_PY))
    names = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, (ast.Tuple, ast.List)):
            continue
        targets = [target.id for target in node.targets if isinstance(target, ast.Name)]
        if any(target.endswith('_PARAMS') for target in targets):
            names.update(elements_strings(node.value))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'build_kwargs' \
                and len(node.args) > 1:
            names.update(elements_strings(node.args[1]))
    return names


def setup_py_arguments():
    """Keyword arguments of the setup() call of setup.py, as ast nodes."""
    tree = ast.parse(read_text(SETUP_PY))
    call = next(node for node in ast.walk(tree)
                if isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'setup')
    return dict((keyword.arg, keyword.value) for keyword in call.keywords)


class TestDeploymentDocumentation:
    """The documentation has to stay in sync with the code it describes."""

    def test_readme_documents_every_parameter_of_run_py(self):
        parameters = run_py_parameter_names()
        assert len(parameters) >= 20
        readme = read_text(README)
        assert sorted(name for name in parameters if name not in readme) == []

    def test_readme_explains_which_python_version_to_use(self):
        readme = read_text(README)
        assert '3.8' in readme
        assert 'grimoirelab-elk' in readme
        assert 'pip install -r requirements.txt' in readme

    def test_readme_documents_the_entry_scripts(self):
        readme = read_text(README)
        for script in ('run.py', 'run_init.py', 'run_test.py', 'run_scheduler_task.py'):
            assert script in readme

    def test_setup_py_requires_python_38(self):
        requires = setup_py_arguments()['python_requires']
        assert isinstance(requires, ast.Constant)
        assert requires.value.replace(' ', '') == '>=3.8'

    def test_setup_py_classifiers_list_the_supported_versions(self):
        classifiers = [element.value for element in setup_py_arguments()['classifiers'].elts]
        assert 'Programming Language :: Python :: 3.8' in classifiers
        assert 'Programming Language :: Python :: 3.4' not in classifiers
        assert 'Programming Language :: Python :: 3.5' not in classifiers

    def test_requirements_list_grimoirelab_elk(self):
        assert 'grimoirelab-elk' in read_text(REQUIREMENTS)
