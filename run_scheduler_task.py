from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from compass_contributor.contributor_org import ContributorOrgService
import yaml
import logging


logger = logging.getLogger(__name__)

def cncf_gitdm_contributor_org_task():
    contributor = ContributorOrgService(elastic_url, params['contributors_org_index'], "github")
    contributor.save_by_cncf_gitdm_url()


if __name__ == '__main__':
    config_url = './conf-github.yaml'
    CONF = yaml.safe_load(open(config_url))
    elastic_url = CONF['url']
    params = CONF['params']

    scheduler = BlockingScheduler()
    trigger = CronTrigger(day='1', hour='0', minute='0')  #Triggered once a month on the 1st
    scheduler.add_job(cncf_gitdm_contributor_org_task, trigger, id="cncf_gitdm_contributor_org_task")
    logger.info("scheduler start")
    scheduler.start()


    

