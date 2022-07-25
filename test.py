
from open_metrics_model.metrics_model import ActivityMetricsModel
import yaml
if __name__ == '__main__':
    CONF = yaml.safe_load(open('conf.yaml'))
    elastic_url = CONF['url']
    params = CONF['params']
    kwargs = {}
    
    for item in ['issue_index', 'pr_index','json_file', 'git_index',  'from_date', 'end_date', 'out_index', 'community', 'level']:
        kwargs[item] = params[item]
    model_activity = ActivityMetricsModel(**kwargs)
    model_activity.metrics_model_metrics(elastic_url)
    
    # for item in ['issue_index', 'pr_index', 'json_file', 'git_index', 'from_date', 'end_date', 'out_index', 'community', 'level']:
    #     kwargs[item] = params[item]
    # model_community = CommunitySupportMetricsModel(**kwargs)
    # model_community.metrics_model_metrics(elastic_url)