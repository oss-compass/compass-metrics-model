"""Run the CHAOSS metrics models against the indices listed in conf.yaml.

This is the entry point described in README.md: it builds the contributor
profile of every repository of the community, runs the four v1 metrics models
and finally stores the summary of each of them, so that the Compass web service
can read the result from a single index.  Every index name, the analysis window
and the community under study are read from the ``params`` section of
``conf.yaml``; ``conf-github.yaml`` is a complete example of that file.
"""
from compass_metrics_model.metrics_model import (ActivityMetricsModel,
                                                 CommunitySupportMetricsModel,
                                                 CodeQualityGuaranteeMetricsModel,
                                                 OrganizationsActivityMetricsModel)

from compass_metrics_model.metrics_model_summary import (
   ActivityMetricsSummary,
   CommunitySupportMetricsSummary,
   CodeQualityGuaranteeMetricsSummary,
   OrganizationsActivityMetricsSummary
)

from compass_contributor.contributor_dev_org_repo import ContributorDevOrgRepo
from compass_common.conf_utils import ConfError, build_kwargs, read_conf

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# Path of the configuration file, relative to this script.  Change it to run
# another deployment, e.g. './conf-gitee.yaml'.
CONF_URL = './conf.yaml'

# Parameters that have to carry a value: without them no model can query the
# cluster.  They are validated once, before the models are built, so that an
# incomplete configuration is reported in one message instead of aborting the
# run with a KeyError while the keyword arguments are collected.
REQUIRED_PARAMS = (
   'json_file', 'issue_index', 'pr_index', 'git_index', 'contributors_index',
   'from_date', 'end_date', 'out_index', 'community', 'level')

# Parameters understood by the contributor profile.  Entries that conf.yaml
# does not mention are forwarded as None, which makes the models fall back to
# their own default (the bundled organization/bot configuration, for example).
CONTRIBUTOR_MODEL_PARAMS = (
   'json_file', 'issue_index', 'pr_index', 'issue_comments_index', 'pr_comments_index',
   'git_index', 'contributors_index', 'contributors_enriched_index', 'from_date', 'end_date',
   'repo_index', 'event_index', 'company', 'stargazer_index', 'fork_index', 'level',
   'community', 'contributors_org_index', 'organizations_index', 'bots_index')

# Parameters understood by each metrics model of compass_metrics_model.
ACTIVITY_MODEL_PARAMS = (
   'issue_index', 'pr_index', 'repo_index', 'json_file', 'git_index', 'from_date', 'end_date',
   'out_index', 'community', 'level', 'release_index', 'issue_comments_index',
   'pr_comments_index', 'contributors_index')

COMMUNITY_MODEL_PARAMS = (
   'issue_index', 'pr_index', 'json_file', 'git_index', 'from_date', 'end_date', 'out_index',
   'community', 'level', 'contributors_index')

CODE_QUALITY_MODEL_PARAMS = (
   'issue_index', 'pr_index', 'json_file', 'git_index', 'from_date', 'end_date', 'out_index',
   'community', 'level', 'company', 'pr_comments_index', 'contributors_index')

ORGANIZATIONS_MODEL_PARAMS = (
   'issue_index', 'pr_index', 'repo_index', 'json_file', 'git_index', 'from_date', 'end_date',
   'out_index', 'community', 'level', 'company', 'issue_comments_index', 'pr_comments_index',
   'contributors_index')

# Parameters needed to locate the metrics models that are summarized.
SUMMARY_PARAMS = ('out_index', 'from_date', 'end_date')


def model_kwargs(params, keys):
   """Keyword arguments of one metrics model, read from conf.yaml.

   :param params: mapping read from the ``params`` section of conf.yaml.
   :param keys: the parameters the model that is about to be created accepts.
   :return: dict holding each key of ``keys``, with None for the entries that
       conf.yaml does not define.
   """
   return build_kwargs(params, keys, required_keys=REQUIRED_PARAMS, conf_url=CONF_URL)


if __name__ == '__main__':
   try:
      elastic_url, params = read_conf(CONF_URL)

      contributor = ContributorDevOrgRepo(**model_kwargs(params, CONTRIBUTOR_MODEL_PARAMS))
      contributor.run(elastic_url)

      model_activity = ActivityMetricsModel(**model_kwargs(params, ACTIVITY_MODEL_PARAMS))
      model_activity.metrics_model_metrics(elastic_url)

      model_community = CommunitySupportMetricsModel(**model_kwargs(params, COMMUNITY_MODEL_PARAMS))
      model_community.metrics_model_metrics(elastic_url)

      model_code = CodeQualityGuaranteeMetricsModel(**model_kwargs(params, CODE_QUALITY_MODEL_PARAMS))
      model_code.metrics_model_metrics(elastic_url)

      model_organizations = OrganizationsActivityMetricsModel(
         **model_kwargs(params, ORGANIZATIONS_MODEL_PARAMS))
      model_organizations.metrics_model_metrics(elastic_url)

      summary = model_kwargs(params, SUMMARY_PARAMS)
      out_index = summary['out_index']
      from_date = summary['from_date']
      end_date = summary['end_date']

      activity_summary = ActivityMetricsSummary(out_index, 'Activity', from_date, end_date,
                                               out_index)
      activity_summary.metrics_model_summary(elastic_url)

      community_summary = CommunitySupportMetricsSummary(out_index, 'Community Support and Service',
                                                        from_date, end_date, out_index)
      community_summary.metrics_model_summary(elastic_url)

      codequality_summary = CodeQualityGuaranteeMetricsSummary(out_index, 'Code_Quality_Guarantee',
                                                              from_date, end_date, out_index)
      codequality_summary.metrics_model_summary(elastic_url)

      organizations_activity_summary = OrganizationsActivityMetricsSummary(
         out_index, 'Organizations Activity', from_date, end_date, out_index)
      organizations_activity_summary.metrics_model_summary(elastic_url)
   except ConfError as error:
      # A missing or incomplete conf.yaml is a configuration mistake rather
      # than a crash: report it with a non zero exit code and without the
      # traceback that the old params[item] lookups produced.
      raise SystemExit("ERROR: %s" % error)
