from compass_metrics_model.metrics_model import (ActivityMetricsModel,
                                                 CommunitySupportMetricsModel,
                                                 CodeQualityGuaranteeMetricsModel,
                                                 OrganizationsActivityMetricsModel)
import yaml

if __name__ == '__main__':
   cofig_url = "./conf.yaml"
   CONF = yaml.safe_load(open(cofig_url))
   elastic_url = CONF['url']
   params = CONF['params']

   kwargs = {}
   for item in ['issue_index', 'pr_index', 'repo_index', 'json_file', 'git_index',  'from_date', 'end_date', 'out_index', 'community', 'level', 'release_index','issue_comments_index', 'pr_comments_index']:
       kwargs[item] = params[item]
   model_activity = ActivityMetricsModel(**kwargs)
   model_activity.metrics_model_metrics(elastic_url)

   kwargs = {}
   for item in ['issue_index', 'pr_index', 'json_file', 'git_index', 'from_date', 'end_date', 'out_index', 'community', 'level']:
       kwargs[item] = params[item]
   model_community = CommunitySupportMetricsModel(**kwargs)
   model_community.metrics_model_metrics(elastic_url)

   kwargs = {}
   for item in ['issue_index', 'pr_index', 'json_file', 'git_index', 'from_date', 'end_date', 'out_index',
               'community', 'level', 'company', 'pr_comments_index']:
      kwargs[item] = params[item]
   model_code = CodeQualityGuaranteeMetricsModel(**kwargs)
   model_code.metrics_model_metrics(elastic_url)

   kwargs = {}
   for item in ['issue_index', 'pr_index', 'repo_index', 'json_file', 'git_index',  'from_date', 'end_date', 'out_index', 'community', 'level', 'company', 'issue_comments_index', 'pr_comments_index']:
       kwargs[item] = params[item]
   model_organizations = OrganizationsActivityMetricsModel(**kwargs)
   model_organizations.metrics_model_metrics(elastic_url)