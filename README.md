## Metrics Model 
Metrics Model makes metrics combine  metrics together, you could find us [here](https://github.com/chaoss/wg-metrics-models) 

### Please create json file as following way:
    
    {
      "gitee-{community name}": {
          "gitee-software-artifact": [
                "https://gitee.com/{owner}/{repo}"
          ],
          "gitee-governance": [
                "https://gitee.com/{owner}/{repo}"
          ]
      }
    }

If it is a github repository, you need to change gitee to github
### Deployment and usage

This repository is the metrics model layer of OSS Compass: it reads the
enriched event indices produced by [grimoirelab](https://github.com/chaoss/grimoirelab)
(issues, pull requests, git, releases, stargazers, forks, ...) from an
Elasticsearch/OpenSearch cluster, combines them into CHAOSS metrics models and
writes the result back to Elasticsearch, where the Compass web service reads
it.  The sections below describe the whole deployment and usage path.

#### 1. Requirements

| Component | Version | Needed for |
| --- | --- | --- |
| Python | **3.8 - 3.11** | everything, see the note below |
| Elasticsearch / OpenSearch | 6.x or 7.x | reading the enriched indices and writing the metrics models |
| grimoirelab-elk | current release | `compass_metrics_model` imports `grimoire_elk` for the `ElasticSearch` helper and the enriched utils |
| gcc and Python headers | only for source builds | compiling `grimoirelab-elk` when no wheel exists for your interpreter |

**Which Python version?**  The models import `grimoire_elk`, and
`grimoirelab-elk` declares `requires-python = ">=3.8"`.  With Python 3.7 or
older, `pip install grimoirelab-elk` falls back to building the package from
source and stops with a `gcc` error, which looks like a broken toolchain but is
in fact an unsupported interpreter.  `setup.py` therefore announces
`python_requires='>=3.8'` and lists the supported versions, so that `pip`
reports the real problem.  Check the interpreter before installing anything:

    python --version                                  # want 3.8 ... 3.11
    python -c "import sys; print(sys.version_info)"   # the same information

#### 2. Installation

    git clone https://github.com/open-metrics-code/compass-metrics-model.git
    cd compass-metrics-model

    # 1. a dedicated interpreter; 3.8 is the safest choice
    python3.8 -m venv .venv
    source .venv/bin/activate        # Windows: .venv\Scripts\activate

    # 2. the dependencies pinned by this repository
    python -m pip install --upgrade pip
    pip install -r requirements.txt

    # 3. grimoirelab-elk separately, so that a build problem shows up here
    pip install grimoirelab-elk

    # 4. the packages of this repository
    pip install -e .

    # 5. smoke test
    python -c "from grimoire_elk.elastic import ElasticSearch; import compass_metrics_model; print('imports OK')"

Two remarks:

* `pip install -e .` honours `python_requires`, so an unsupported interpreter is
  rejected with a clear message instead of failing while a model runs.
* A virtual environment is strongly recommended: the pinned `numpy` and
  `pandas` releases are older than the ones a system interpreter carries, and
  they are not available for Python 3.12 at all.

#### 3. Data preparation

Two inputs have to exist before `run.py` can compute anything.

##### 3.1 The project file

The json file of the section above lists the repositories of the community,
grouped by the part of the ecosystem they belong to.  Ready to use examples are
`projects-github-pytorch.json`, `projects-gitee-mindspore.json` and
`projects-gitcode.json`; the file that is used is selected with the `json_file`
parameter of `conf.yaml`.

##### 3.2 The enriched indices

The metrics models do not read raw platform data: they expect the enriched
indices that a grimoirelab deployment creates (`github-issues_enriched`,
`github-pulls_enriched`, `github-git_enriched`, ...).  Their names are the
`params` of `conf.yaml`, together with the index that receives the result.
`out_index` and the contributor profile index are created automatically when
they do not exist yet.

#### 4. Configuration

Start from one of the templates that ship with the repository:

    cp conf-github.yaml conf.yaml

`conf.yaml` has two sections:

    url:
        "https://user:password@ip:9200"

    params:
        {
            'json_file': 'projects-github-pytorch.json',
            'issue_index': 'github-issues_enriched',
            'pr_index': 'github-pulls_enriched',
            'git_index': 'github-git_enriched',
            'contributors_index': 'github-contributors_org_repo',
            'contributors_enriched_index': 'github-contributors_org_repo_enriched',
            'from_date': '2024-01-01',
            'end_date': '2024-12-31',
            'out_index': 'v2_metric_model_test',
            'community': 'pytorch',
            'level': 'repo'
        }

`url` points at the Elasticsearch/OpenSearch instance that holds the enriched
indices, credentials included (`https://user:password@host:port`).  `params` is
designed to init the metrics models; the entry scripts change the working
directory to the repository root, so `json_file` is resolved relative to it.

| Parameter | Required | Meaning |
| --- | --- | --- |
| `json_file` | yes | the project file of section 3.1 |
| `issue_index` | yes | enriched issue index |
| `pr_index` | yes | enriched pull request index |
| `git_index` | yes | enriched git (commit) index |
| `contributors_index` | yes | contributor profile index, written by the contributor step and created when it is missing |
| `contributors_enriched_index` | recommended | enriched contributor profile index, written by the contributor step |
| `from_date`, `end_date` | yes | analysis window, `YYYY-MM-DD`, both ends included |
| `out_index` | yes | index that receives the metrics models and their summaries |
| `community` | yes | community name stored in the produced documents |
| `level` | yes | `repo`, `project` or `community` |
| `repo_index` | optional | enriched repository index, used by the Activity and Organizations Activity models |
| `release_index` | optional | enriched release index, used by the Activity model |
| `issue_comments_index` | optional | enriched issue comment index |
| `pr_comments_index` | optional | enriched pull request comment index |
| `contributors_org_index` | optional | contributor to organization mapping; when it is omitted, the bundled `compass_contributor/conf_utils/*.json` data is used |
| `organizations_index` | optional | organization profiles, see `run_init.py` |
| `bots_index` | optional | bot accounts, see `run_init.py` |
| `stargazer_index` | optional | enriched stargazer index, used by the popularity metrics |
| `fork_index` | optional | enriched fork index |
| `event_index` | optional | enriched issue and pull request event index |
| `company` | optional | company whose contribution share is measured; omit the entry (or write `'None'`) to measure every organization |
| `git_branch` | optional | restrict the git metrics to a single branch |
| `source` | not used by `run.py` | `github`, `gitee` or `gitcode`; the models derive the source from the issue index name |
| `custom_fields` | optional | extra fields, for example `{'period': 'month'}`, used by the v2 models |

A parameter that `conf.yaml` does not mention is forwarded as `None`, which
makes the models fall back to their own default, and a warning names it.  The
required parameters above have to carry a value, otherwise the run stops with

    ERROR: conf.yaml has to provide a value for json_file, issue_index, ... in its 'params' section

instead of the `KeyError` that older revisions of `run.py` raised in the middle
of the script for a configuration written from the example above.

#### 5. Running

    python run.py

`run.py` performs the following steps, all of them against the cluster given by
`url`:

1. `ContributorDevOrgRepo` builds the contributor profile of every repository
   of the project file and stores it in `contributors_index` and
   `contributors_enriched_index`.
2. `ActivityMetricsModel`, `CommunitySupportMetricsModel`,
   `CodeQualityGuaranteeMetricsModel` and `OrganizationsActivityMetricsModel`
   compute the v1 metrics models of the analysis window and store them in
   `out_index`.
3. The four matching `*MetricsSummary` classes add the summarized document of
   each model to `out_index`.

Check the result with, for example:

    curl -u user:password "http://ip:9200/${OUT_INDEX}/_count?pretty"
    curl -u user:password "http://ip:9200/${OUT_INDEX}/_search?pretty&size=1"

The other entry points of the repository read a `config_url` constant that is
declared at the top of each file:

| Script | Purpose |
| --- | --- |
| `run.py` | contributor profile, v1 metrics models and their summaries |
| `run_test.py` | the v2 models of `compass_model` (Activity, Organizations Activity, Starter Project Health, Community Service and Support, Collaboration Development Index and the persona models) |
| `run_init.py` | loads the organization, bot and contributor-org data of the bundled configuration into Elasticsearch; run it once before the models |
| `run_scheduler_task.py` | refreshes the cncf gitdm contributor-org mapping once a month (needs `apscheduler`) |
| `prediction_test.py` | example for the models of `compass_prediction`, configured with `prediction_conf.yaml` |

#### 6. Troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| `KeyError: 'stargazer_index'` while starting `run.py` | the `conf.yaml` does not define every parameter; older revisions aborted here, while the current `run.py` only warns for the optional ones.  Add the missing entries from `conf-github.yaml`. |
| `ERROR: conf.yaml not found` | `run.py` looks for `conf.yaml` next to itself; copy `conf-github.yaml` and fill in `url` and `params`. |
| `ERROR: conf.yaml does not define 'url'` | the `url` entry is missing or empty, the template ships it commented out. |
| `gcc` error while installing `grimoirelab-elk` | Python 3.7 or older, or a source build without compiler and headers.  Use Python 3.8 - 3.11 and reinstall in a fresh virtual environment. |
| `ModuleNotFoundError: No module named 'grimoire_elk'` | `grimoirelab-elk` was not installed: `pip install grimoirelab-elk`. |
| `FileNotFoundError` for the project file | `json_file` is wrong, the path is resolved from the repository root. |
| `elasticsearch.exceptions.ConnectionError` | the cluster is unreachable or the credentials of `url` are wrong; check it with `curl -u user:password http://ip:9200/_cat/indices`. |
| the models finish but `out_index` stays empty | `from_date` and `end_date` do not overlap the enriched data, or the index names point at empty indices; check the counts with the curl commands of section 5. |
| `pip` cannot find a `numpy` or `pandas` release | the pins of `requirements.txt` target Python 3.8 - 3.11; use one of these interpreters or relax the pins for a newer one. |

Deployment problems that are not listed here are much easier to solve with the
output of `python --version` and `pip freeze` in the issue report.
