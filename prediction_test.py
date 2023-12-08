from compass_prediction.oss_prediction import prediction_activity_start
from compass_common.opensearch_utils import get_client
import yaml
import logging

logger = logging.getLogger("compass_prediction.oss_prediction")
logger.setLevel(logging.DEBUG)
logging.info('loggging info message')

if __name__ == '__main__':
    cofig_url = "./prediction_conf.yaml"
    CONF = yaml.safe_load(open(cofig_url))
    params = CONF['params']
    client = get_client(CONF['url'])
    repo = params["repo"]
    activity_index = params["activity_index"]
    development_index = params["development_index"]
    community_index = params["community_index"]
    organizations_activity_index = params["organizations_activity_index"]
    
    prediction_result = prediction_activity_start(repo, client, activity_index, development_index, community_index, organizations_activity_index)
    print(prediction_result)
    