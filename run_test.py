import os
import yaml
import logging

from compass_model.base_metrics_model import BaseMetricsModel
from compass_model.robustness.activity_metrics_model import ActivityMetricsModel

os.chdir(os.path.dirname(os.path.realpath(__file__)))

logger = logging.getLogger("compass_model.base_metrics_model")
logger.setLevel(logging.DEBUG)
logging.info('loggging info message')

if __name__ == '__main__':
    config_url = './conf-pytorch.yaml'
    CONF = yaml.safe_load(open(config_url))
    elastic_url = CONF['url']
    params = CONF['params']

    kwargs = {}
    for item in ["repo_index", "git_index", "issue_index", "pr_index", "issue_comments_index", "pr_comments_index",
                 "contributors_index", "release_index", "out_index", "from_date", "end_date", "level", "community",
                 "source", "json_file"]:
        kwargs[item] = None if params[item] is None or params[item] == 'None' else params[item]
    model_activity = ActivityMetricsModel(**kwargs)
    model_activity.metrics_model_metrics(elastic_url)
