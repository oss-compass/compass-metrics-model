from compass_common.opensearch_utils import get_client, get_helpers as helpers
from compass_common.datetime import datetime_utcnow
from compass_metrics.db_dsl import get_base_index_mapping
from compass_common.uuid_utils import get_uuid
from datetime import datetime
import json
import logging
import pkg_resources
logger = logging.getLogger(__name__)


class OrganizationService:
    def __init__(self, opensearch_url, organizations_index):
        """
            To store organization information
        Args:
            opensearch_url: The url to the opensearch database, including username and password.
            organizations_index: Indexes for storing organization data
        """
        self.client = get_client(opensearch_url)
        self.organizations_index = organizations_index

        es_exist = self.client.indices.exists(index=self.organizations_index)
        if not es_exist:
            self.client.indices.create(index=self.organizations_index,
                                       body=get_base_index_mapping())

    def save_by_user_id(self, org_name, user_id):
        organization = Organization(id, None, org_name, user_id)
        self.save(organization)

    def save_by_config_file(self):
        organization_list = []
        organizations_json_data = pkg_resources.resource_string('compass_contributor', 'conf_utils/organizations.json')
        organizations_config = json.loads(organizations_json_data.decode('utf-8'))
        for org_name in organizations_config["organizations"].keys():
            for domain in organizations_config["organizations"][org_name]:
                organization = Organization(domain["domain"], org_name, None)
                organization_list.append(organization)
        self.batch_save(organization_list)

    def save(self, organization):
        """ Save organization information in the database """
        item_data = {
            "_index": self.organizations_index,
            "_id": organization.id,
            "_source": {
                "uuid": organization.id,
                **organization.__dict__
            }
        }
        helpers().bulk(client=self.client, actions=[item_data])

    def batch_save(self, organization_list):
        """ Batch save organization information in the database """
        item_datas = []
        for organization in organization_list:
            item_data = {
                "_index": self.organizations_index,
                "_id": organization.id,
                "_source": {
                    "uuid": organization.id,
                    **organization.__dict__
                }
            }
            item_datas.append(item_data)
            if len(item_datas) > 1000:
                helpers().bulk(client=self.client, actions=item_datas)
                item_datas = []
        helpers().bulk(client=self.client, actions=item_datas)

    def get_dict_domain_exist(self):
        organizations_dict = {}
        query = {
          "size": 10000,
          "query": {
            "exists": {
                "field": "domain"
            }
          }
        }
        hits = self.client.search(index=self.organizations_index, body=query)["hits"]["hits"]
        for hit in hits:
            hit_source = hit['_source']
            organizations_dict[hit_source["domain"]] = hit_source["org_name"]
        return organizations_dict

class Organization:
    def __init__(self, domain, org_name, user_id):
        """Organization Information

        Args:
            domain (str): Email Suffix
            org_name (str): Name of the organization corresponding to the mailbox suffix
            user_id (str): OSS-Compass user id
        """
        self.id = get_uuid(domain, org_name)
        self.domain = domain
        self.org_name = org_name
        self.user_id = user_id
        self.update_at_date = datetime_utcnow().isoformat()