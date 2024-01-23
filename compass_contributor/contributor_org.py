from compass_common.opensearch_utils import get_client, get_helpers as helpers
from compass_common.datetime import datetime_utcnow
from compass_common.uuid_utils import get_uuid
from compass_metrics.db_dsl import get_base_index_mapping
from datetime import datetime
from compass_common.list_utils import split_list
import requests
import re
import logging

logger = logging.getLogger(__name__)


def convert_datestring(date_string):
    date_obj = datetime.strptime(date_string, "%Y-%m-%d")
    formatted_date = date_obj.strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
    return formatted_date


class ContributorOrgService:
    def __init__(self, opensearch_url, contributors_org_index, source):
        """
            To store contributor organization information, including user-defined, administrator-defined,
            and other defined organization information

        Args:
            opensearch_url: The url to the opensearch database, including username and password.
            contributor_org_conf_index: Indexes for storing contributor organization data
            source: Is the contributor organization data source gitee or github
        """
        self.client = get_client(opensearch_url)
        self.contributors_org_index = contributors_org_index
        self.source = source

        es_exist = self.client.indices.exists(index=self.contributors_org_index)
        if not es_exist:
            self.client.indices.create(index=self.contributors_org_index,
                                       body=get_base_index_mapping())

    def save_by_user_individual(self, contributor, org_change_date_list, operator_id):
        contributor = contributor
        org_change_date_list = org_change_date_list
        level = None
        label = None
        modify_type = "User Individual"
        modify_by = operator_id
        platform_type = self.source
        is_bot = False
        contributor_org = ContributorOrg(contributor, org_change_date_list, level, label, modify_type, modify_by,
                                         platform_type, is_bot)
        self.save(contributor_org)


    def save_by_system_admin(self, contributor, org_change_date_list, level, label, operator_id):
        contributor = contributor
        org_change_date_list = org_change_date_list
        modify_type = "System Admin"
        modify_by = operator_id
        platform_type = self.source
        is_bot = False
        contributor_org = ContributorOrg(contributor, org_change_date_list, level, label, modify_type, modify_by,
                                            platform_type, is_bot)
        self.save(contributor_org)


    def save_by_repo_admin(self, contributor, org_change_date_list, level, label, pr_url):
        contributor = contributor
        org_change_date_list = org_change_date_list
        modify_type = "Repo Admin"
        modify_by = pr_url
        platform_type = self.source
        is_bot = False
        contributor_org = ContributorOrg(contributor, org_change_date_list, level, label, modify_type, modify_by,
                                         platform_type, is_bot)
        self.save(contributor_org)


    def save_by_cncf_gitdm_url(self):

        def analytic_company_developers(content):
            analytic_result = {}
            lines = content.splitlines()
            for line in lines:
                line = line.strip()
                if len(line) == 0 or line.startswith("#"):
                    continue
                if line.endswith(":"):
                    org_name = line[:-1]
                else:
                    contributor_info = line.split(":")
                    if len(contributor_info) > 1:
                        contributor = contributor_info[0].strip()
                        time_list = []
                        for item in contributor_info[1].strip().split(","):
                            item = item.strip()
                            string_split = item.split(" ")
                            domain = string_split[0]
                            if "from" in string_split and (string_split.index("from") + 1) < len(string_split):
                                first_date = string_split[string_split.index("from") + 1]
                            else:
                                first_date = "1970-01-01"
                            if "until" in string_split and (string_split.index("until") + 1) < len(string_split):
                                last_date = string_split[string_split.index("until") + 1]
                            else:
                                last_date = "2099-01-01"
                            time_list.append(first_date)
                            time_list.append(last_date)
                        contributor_list = analytic_result.get(contributor, [])
                        contributor_list.append({
                            "org_name": org_name,
                            "first_date": convert_datestring(min(time_list)),
                            "last_date": convert_datestring(max(time_list))
                        })
                        analytic_result[contributor] = contributor_list
            return analytic_result

        def analytic_developers_affiliations(content):
            analytic_result = {}
            lines = content.splitlines()
            for line in lines:
                line = line.strip()
                if len(line) == 0 or line.startswith("#"):
                    continue
                if ":" in line:
                    contributor = line.split(":")[0]
                else:
                    pattern = r'^(.*?)(?:\s+from\s+(\d{4}-\d{2}-\d{2}))?(?:\s+until\s+(\d{4}-\d{2}-\d{2}))?$'
                    match = re.match(pattern, line)
                    if not match:
                        continue
                    company_name = match.group(1).strip()
                    first_date = match.group(2) if match.group(2) else "1970-01-01"
                    last_date = match.group(3) if match.group(3) else "2099-01-01"
                    if company_name is not None:
                        contributor_list = analytic_result.get(contributor, [])
                        contributor_list.append({
                            "org_name": company_name,
                            "first_date": convert_datestring(first_date),
                            "last_date": convert_datestring(last_date)
                        })
                        analytic_result[contributor] = contributor_list
            return analytic_result

        cncf_gitdm_url = "https://raw.githubusercontent.com/cncf/gitdm"

        content = None
        analytic_switch = {
            "company_developers": lambda: analytic_company_developers(content),
            "developers_affiliations": lambda: analytic_developers_affiliations(content),
        }
        all_developers = {}
        for file_url in analytic_switch.keys():
            i = 1
            while True:
                url = f"{cncf_gitdm_url}/master/{file_url}{i}.txt"
                logger.info(url)
                response = requests.head(url)
                if response.status_code != 200:
                    break
                content_response = requests.get(url)
                content = content_response.text
                developers = analytic_switch[file_url]()
                for contributor, org_info_list in developers.items():
                    contributor_org_info_list = all_developers.get(contributor, [])
                    all_developers[contributor] = contributor_org_info_list + org_info_list
                i += 1
        contributor_org_dao_list = []
        for contributor, org_info_list in all_developers.items():
            contributor = contributor
            if len(org_info_list) > 0:
                base_org_info_dict = {}
                for item in org_info_list:
                    org_info = base_org_info_dict.get(item["org_name"])
                    if org_info is not None:
                        data_list = [item["first_date"], item["last_date"], org_info["first_date"],
                                     org_info["last_date"]]
                    else:
                        data_list = [item["first_date"], item["last_date"]]
                    base_org_info_dict[item["org_name"]] = {
                        "org_name": item["org_name"],
                        "first_date": min(data_list),
                        "last_date": max(data_list)
                    }
                org_info_list = list(base_org_info_dict.values())
                sorted(org_info_list, key=lambda x: x["first_date"])
            org_change_date_list = org_info_list
            level = None
            label = None
            modify_type = "URL"
            modify_by = cncf_gitdm_url
            platform_type = self.source
            is_bot = "(Robots)" in {org_item["org_name"] for org_item in org_info_list}
            contributor_org = ContributorOrg(contributor, org_change_date_list, level, label, modify_type,
                                             modify_by, platform_type, is_bot)
            contributor_org_dao_list.append(contributor_org)
        logger.info(f"{cncf_gitdm_url} save contributor: {len(contributor_org_dao_list)}")
        self.batch_save(contributor_org_dao_list)

    def save(self, contributor_org):
        """ Save contributor organization information in the database """
        item_data = {
            "_index": self.contributors_org_index,
            "_id": contributor_org.id,
            "_source": {
                "uuid": contributor_org.id,
                **contributor_org.__dict__
            }
        }
        helpers().bulk(client=self.client, actions=[item_data])

    def batch_save(self, contributor_org_list):
        """ Batch save contributor organization information in the database """
        item_datas = []
        for contributor_org in contributor_org_list:
            item_data = {
                "_index": self.contributors_org_index,
                "_id": contributor_org.id,
                "_source": {
                    "uuid": contributor_org.id,
                    **contributor_org.__dict__
                }
            }
            item_datas.append(item_data)
            if len(item_datas) > 1000:
                helpers().bulk(client=self.client, actions=item_datas)
                item_datas = []
        helpers().bulk(client=self.client, actions=item_datas)

    def get_dict_by_contributor_name(self, contributor_name_list, level, label):
        """ Query contributor organization data by contributor name """
        contributor_org_dict = {}
        if len(contributor_name_list) == 0:
            return contributor_org_dict
        contributor_list_group = split_list(contributor_name_list)
        for contributors in contributor_list_group:
            query = {
                "size": 1000,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match_phrase": {
                                    "platform_type.keyword": self.source
                                }
                            },
                            {
                                "terms": {
                                    "contributor.keyword": contributors
                                }
                            }
                        ],
                        "should": [
                            {
                                "bool": {
                                    "must": [
                                        {
                                            "terms": {
                                                "modify_type.keyword": ["System Admin", "Repo Admin"]
                                            }
                                        },
                                        {
                                            "match_phrase": {
                                                "level.keyword": level
                                            }
                                        },
                                        {
                                            "match_phrase": {
                                                "label.keyword": label
                                            }
                                        }
                                    ]
                                }
                            },
                            {
                                "match_phrase": {
                                    "modify_type.keyword": "User Individual"
                                }
                            },
                            {
                                "match_phrase": {
                                    "modify_type.keyword": "URL"
                                }
                            }
                        ],
                        "minimum_should_match": 1
                    }
                }
            }
            hits = self.client.search(index=self.contributors_org_index, body=query)["hits"]["hits"]
            for hit in hits:
                hit_source = hit['_source']
                contributor_key = f"{hit_source.get('modify_type')}&&{hit_source.get('contributor')}"
                contributor_org_dict[contributor_key] = hit_source
        return contributor_org_dict


class ContributorOrg:
    def __init__(self, contributor, org_change_date_list, level, label, modify_type, modify_by,
                 platform_type, is_bot):
        """Contributor Organization Information

        Args:
            contributor (str): contributor name
            org_change_date_list (list[Dict[str, Any]]): List of organization changes, list with org_name, first_date, last_date
            level: choose from repo, community
            label: repo corresponds to the repository url, community corresponds to the community name.
            modify_type (str): The modify type contains 'User Individual', 'System Admin', 'Repo Admin', 'URL'
            modify_by (str): What has been modified, if the modify type is 'User Individual' and 'Repo Admin' then save operator user id, 
                if the modifYtype is 'URl' then save url address. 
            platform_type (str): Is the contributor data source gitee or github
            is_bot (bool): is bot
        """
        self.id = get_uuid(contributor, modify_type, level, label, platform_type)
        self.contributor = contributor
        self.org_change_date_list = org_change_date_list
        self.level = level
        self.label = label
        self.modify_type = modify_type
        self.modify_by = modify_by
        self.platform_type = platform_type
        self.is_bot = is_bot
        self.update_at_date = datetime_utcnow().isoformat()
