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

import yaml
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

if __name__ == '__main__':
   cofig_url = "./conf.yaml"
   CONF = yaml.safe_load(open(cofig_url))
   elastic_url = CONF['url']
   params = CONF['params']

   kwargs = {}
   for item in ['json_file', 'identities_config_file', 'organizations_config_file', 'issue_index', 'pr_index',
                'issue_comments_index', 'pr_comments_index', 'git_index', 'contributors_index', 'from_date',
                'end_date', 'company', 'bots_config_file', 'repo_index', 'event_index', 'stargazer_index', 
                'fork_index', 'contributors_enriched_index']:
      kwargs[item] = None if params[item] and params[item] == 'None' else params[item]
   contributor = ContributorDevOrgRepo(**kwargs)
   contributor.run(elastic_url)

   kwargs = {}
   for item in ['issue_index', 'pr_index', 'repo_index', 'json_file', 'git_index',  'from_date', 'end_date',
                'out_index', 'community', 'level', 'release_index', 'issue_comments_index', 'pr_comments_index',
                'contributors_index']:
       kwargs[item] = None if params[item] and params[item] == 'None' else params[item]
   model_activity = ActivityMetricsModel(**kwargs)
   model_activity.metrics_model_metrics(elastic_url)

   kwargs = {}
   for item in ['issue_index', 'pr_index', 'json_file', 'git_index', 'from_date', 'end_date', 'out_index', 'community',
                'level', 'contributors_index']:
       kwargs[item] = None if params[item] and params[item] == 'None' else params[item]
   model_community = CommunitySupportMetricsModel(**kwargs)
   model_community.metrics_model_metrics(elastic_url)

   kwargs = {}
   for item in ['issue_index', 'pr_index', 'json_file', 'git_index', 'from_date', 'end_date', 'out_index',
               'community', 'level', 'company', 'pr_comments_index', 'contributors_index']:
      kwargs[item] = None if params[item] and params[item] == 'None' else params[item]
   model_code = CodeQualityGuaranteeMetricsModel(**kwargs)
   model_code.metrics_model_metrics(elastic_url)

   kwargs = {}
   for item in ['issue_index', 'pr_index', 'repo_index', 'json_file', 'git_index',  'from_date', 'end_date',
                'out_index', 'community', 'level', 'company', 'issue_comments_index', 'pr_comments_index',
                'contributors_index']:
       kwargs[item] = None if params[item] and params[item] == 'None' else params[item]
   model_organizations = OrganizationsActivityMetricsModel(**kwargs)
   model_organizations.metrics_model_metrics(elastic_url)

   activity_summary = ActivityMetricsSummary(params['out_index'], 'Activity', params['from_date'], params['end_date'],
                                             params['out_index'])
   activity_summary.metrics_model_summary(elastic_url)

   community_summary = CommunitySupportMetricsSummary(params['out_index'], 'Community Support and Service',
                                                      params['from_date'], params['end_date'], params['out_index'])
   community_summary.metrics_model_summary(elastic_url)

   codequality_summary = CodeQualityGuaranteeMetricsSummary(params['out_index'], 'Code_Quality_Guarantee',
                                                            params['from_date'], params['end_date'],
                                                            params['out_index'])
   codequality_summary.metrics_model_summary(elastic_url)

   organizations_activity_summary = OrganizationsActivityMetricsSummary(params['out_index'], 'Organizations Activity',
                                                                        params['from_date'], params['end_date'],
                                                                        params['out_index'])
   organizations_activity_summary.metrics_model_summary(elastic_url)
