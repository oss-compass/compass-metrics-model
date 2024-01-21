from compass_common.opensearch_utils import get_client, get_helpers as helpers
from compass_common.datetime import datetime_utcnow
from compass_metrics.db_dsl import get_base_index_mapping
from compass_common.uuid_utils import get_uuid
from datetime import datetime
import json
import logging
import pkg_resources
logger = logging.getLogger(__name__)


class BotService:
    def __init__(self, opensearch_url, bots_index):
        """
            To store bot information
        Args:
            opensearch_url: The url to the opensearch database, including username and password.
            bots_index: Indexes for storing bot data
        """
        self.client = get_client(opensearch_url)
        self.bots_index = bots_index

        es_exist = self.client.indices.exists(index=self.bots_index)
        if not es_exist:
            self.client.indices.create(index=self.bots_index,
                                       body=get_base_index_mapping())

    def save_by_config_file(self):
        bot_list = []
        bots_json_data = pkg_resources.resource_string('compass_contributor', 'conf_utils/bots.json')
        bots_config = json.loads(bots_json_data.decode('utf-8'))
        for source in bots_config.keys():
            if bots_config[source].get("contributor") and len(bots_config[source].get("contributor")) > 0:
                for source_contributor in bots_config[source].get("contributor"):
                    bot = Bot(source_contributor, source, None, None)
                    bot_list.append(bot)
            for community, community_values in bots_config[source]["community"].items():
                if community_values.get("contributor") and len(community_values.get("contributor")) > 0:
                    for community_contributor in community_values["contributor"]:
                        bot = Bot(community_contributor, source, community, None)
                        bot_list.append(bot)
                if community_values.get("repo"):
                    for repo, repo_values in community_values["repo"].items():
                        if repo_values.get("contributor") and len(repo_values.get("contributor")) > 0:
                            for repo_contributor in repo_values["contributor"]:
                                bot = Bot(repo_contributor, source, community, repo)
                                bot_list.append(bot)
        self.batch_save(bot_list)

    def save(self, bot):
        """ Save bot information in the database """
        item_data = {
            "_index": self.bots_index,
            "_id": bot.id,
            "_source": {
                "uuid": bot.id,
                **bot.__dict__
            }
        }
        helpers().bulk(client=self.client, actions=[item_data])

    def batch_save(self, bot_list):
        """ Batch save bot information in the database """
        item_datas = []
        for bot in bot_list:
            item_data = {
                "_index": self.bots_index,
                "_id": bot.id,
                "_source": {
                    "uuid": bot.id,
                    **bot.__dict__
                }
            }
            item_datas.append(item_data)
            if len(item_datas) > 1000:
                helpers().bulk(client=self.client, actions=item_datas)
                item_datas = []
        helpers().bulk(client=self.client, actions=item_datas)

    def get_dict_by_source(self, source):
        common = []
        community_dict = {}
        repo_dict = {}
        bots_dict = {
            "common": common,
            "community": community_dict,
            "repo": repo_dict
        }
        query = {
          "size": 10000,
          "query": {
            "match_phrase": {
              "plateform_type.keyword": source
            }
          }
        }
        hits = self.client.search(index=self.bots_index, body=query)["hits"]["hits"]
        for hit in hits:
            hit_source = hit['_source']
            if hit_source["community"] is None and hit_source["repo"] is None:
                common.append(hit_source["contributor"])
            elif hit_source["community"] and hit_source["repo"] is None:
                community_contributor_list = community_dict.get(hit_source["community"], [])
                community_contributor_list.append(hit_source["contributor"])
                community_dict[hit_source["community"]] = community_contributor_list
            elif hit_source["community"] and hit_source["repo"]:
                repo_contributor_list = repo_dict.get(hit_source["repo"], [])
                repo_contributor_list.append(hit_source["repo"])
                repo_dict[hit_source["repo"]] = repo_contributor_list
        return bots_dict


class Bot:
    def __init__(self, contributor, plateform_type, community, repo):
        """Bot Information

        Args:
            contributor (str): Contributor robot Name
            plateform_type (str): Is the contributor data source gitee or github
            community (str): Platform community address
            repo (str): Platform repo address
        """
        self.id = get_uuid(contributor, plateform_type)
        self.contributor = contributor
        self.plateform_type = plateform_type
        self.community = community
        self.repo = repo
        self.update_at_date = datetime_utcnow().isoformat()