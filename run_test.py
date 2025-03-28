'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2025-03-04 17:59:54
LastEditors: zyx
LastEditTime: 2025-03-26 22:20:30
'''
import os
import yaml
import logging

from compass_model.base_metrics_model import BaseMetricsModel
from compass_model.collaboration.robustness.activity_metrics_model import ActivityMetricsModel 
from compass_model.collaboration.niche_creation.organizations_activity_metrics_model import OrganizationsActivityMetricsModel
from compass_model.lab.starter_project_health_metrics_model import StarterProjectHealthMetricsModel 
from compass_model.collaboration.productivity.collaboration_development_index_metrics_model import CollaborationDevelopmentIndexMetricsModel 
from compass_model.collaboration.productivity.community_service_and_support_metrics_model import CommunityServiceAndSupportMetricsModel
from compass_model.contributor.productivity.domain_persona_metrics_model import DomainPersonaMetricsModel
from compass_model.contributor.productivity.milestone_persona_metrics_model import MilestonePersonaMetricsModel
from compass_model.contributor.productivity.role_persona_metrics_model import RolePersonaMetricsModel

os.chdir(os.path.dirname(os.path.realpath(__file__)))

logger = logging.getLogger("compass_model.base_metrics_model")
logger.setLevel(logging.DEBUG)
logging.info('loggging info message')

if __name__ == '__main__':
    config_url = './conf-github.yaml'
    CONF = yaml.safe_load(open(config_url))
    elastic_url = CONF['url']
    params = CONF['params']

    kwargs = {}
    for item in ["repo_index", "git_index", "issue_index", "pr_index", "issue_comments_index", "pr_comments_index",
                 "contributors_index", "release_index", "out_index", "from_date", "end_date", "level", "community",
                 "source", "json_file", "contributors_enriched_index"]:
        kwargs[item] = None if params[item] is None or params[item] == 'None' else params[item]

    model_activity = ActivityMetricsModel(**kwargs)
    model_activity.metrics_model_metrics(elastic_url)

    org_activity = OrganizationsActivityMetricsModel(**kwargs)
    org_activity.metrics_model_metrics(elastic_url)

    starter = StarterProjectHealthMetricsModel(**kwargs)
    starter.metrics_model_metrics(elastic_url)

    community = CommunityServiceAndSupportMetricsModel(**kwargs)
    community.metrics_model_metrics(elastic_url)

    collaboration = CollaborationDevelopmentIndexMetricsModel(**kwargs)
    collaboration.metrics_model_metrics(elastic_url)

    MilestonePersona = MilestonePersonaMetricsModel(**kwargs)
    MilestonePersona.metrics_model_metrics(elastic_url)

    RolePersona = RolePersonaMetricsModel(**kwargs)
    RolePersona.metrics_model_metrics(elastic_url)

    DomainPersona = DomainPersonaMetricsModel(**kwargs)
    DomainPersona.metrics_model_metrics(elastic_url)

