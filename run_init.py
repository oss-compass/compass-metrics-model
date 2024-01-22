from compass_contributor.contributor_org import ContributorOrgService
from compass_contributor.organization import OrganizationService
from compass_contributor.bot import BotService
import yaml
import logging

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    config_url = './conf-github.yaml'
    CONF = yaml.safe_load(open(config_url))
    elastic_url = CONF['url']
    params = CONF['params']

    contributor = ContributorOrgService(elastic_url, params['contributors_org_index'], "github")
    contributor.save_by_cncf_gitdm_url()
    logger.info(f"finish init contributor org by cncf gitdm")

    organization = OrganizationService(elastic_url, params['organizations_index'])
    organization.save_by_config_file()
    logger.info(f"finish init organization by config")

    bot = BotService(elastic_url, params['bots_index'])
    bot.save_by_config_file()
    logger.info(f"finish init bot by config")


    

