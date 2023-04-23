from compass_metrics_model.metrics_model_lab import (StarterProjectHealthMetricsModel)
import yaml
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

if __name__ == '__main__':
   cofig_url = "./conf.yaml"
   CONF = yaml.safe_load(open(cofig_url))
   elastic_url = CONF['url']
   params = CONF['params']

   kwargs = {}
   for item in ['issue_index', 'pr_index', 'repo_index', 'json_file', 'git_index', 'out_index', 'from_date',
                'end_date', 'community', 'level', 'contributors_index', 'release_index']:
      kwargs[item] = None if params[item] == None or params[item] == 'None' else params[item]
   model_starter_project_health = StarterProjectHealthMetricsModel(**kwargs)
   model_starter_project_health.metrics_model_metrics(elastic_url)