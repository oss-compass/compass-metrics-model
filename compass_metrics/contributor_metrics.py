from compass_metrics.db_dsl import get_contributor_query, get_uuid_count_query
from compass_common.datetime import get_time_diff_months, check_times_has_overlap
from datetime import timedelta
from itertools import groupby
import pandas as pd


def contributor_count(client, contributors_index, date, repo_list):
    """ Determine how many active code commit authors, pr authors, review participants, issue authors,
    and issue comments participants there are in the past 90 days """

    from_date = date - timedelta(days=90)
    to_date = date
    commit_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                   "code_commit_date_list")
    issue_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                  "issue_creation_date_list")
    issue_comment_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                          "issue_comments_date_list")
    pr_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                               "pr_creation_date_list")
    pr_comment_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                       "pr_review_date_list")
    D1_contributor_list = commit_contributor_list + issue_contributor_list + pr_contributor_list + \
                          issue_comment_contributor_list + pr_comment_contributor_list
    result = {
        "contributor_count": get_contributor_count(D1_contributor_list),
        "contributor_count_bot": get_contributor_count(D1_contributor_list, is_bot=True),
        "contributor_count_without_bot": get_contributor_count(D1_contributor_list, is_bot=False)
    }
    return result


def code_contributor_count(client, contributors_index, date, repo_list):
    """  Determine how many active pr creators, code reviewers, commit authors there are in the past 90 days. """
    from_date = date - timedelta(days=90)
    to_date = date
    commit_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                   "code_commit_date_list")
    pr_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                               "pr_creation_date_list")
    pr_comment_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                       "pr_review_date_list")
    contributor_list = commit_contributor_list + pr_contributor_list + pr_comment_contributor_list
    result = {
        "code_contributor_count": get_contributor_count(contributor_list),
        "code_contributor_count_bot": get_contributor_count(contributor_list, is_bot=True),
        "code_contributor_count_without_bot": get_contributor_count(contributor_list, is_bot=False)
    }
    return result


def commit_contributor_count(client, contributors_index, date, repo_list):
    """ Determine how many active code commit authors participants there are in the past 90 days """
    commit_contributor_list = get_contributor_list(client, contributors_index, date - timedelta(days=90), date,
                                                   repo_list, "code_commit_date_list")
    result = {
        "commit_contributor_count": get_contributor_count(commit_contributor_list),
        "commit_contributor_count_bot": get_contributor_count(commit_contributor_list, is_bot=True),
        "commit_contributor_count_without_bot": get_contributor_count(commit_contributor_list, is_bot=False)
    }
    return result


def pr_authors_contributor_count(client, contributors_index, date, repo_list):
    """ Determine how many active pr authors participants there are in the past 90 days """
    pr_contributor_list = get_contributor_list(client, contributors_index, date - timedelta(days=90), date, repo_list,
                                               "pr_creation_date_list")
    result = {
        "pr_authors_contributor_count": get_contributor_count(pr_contributor_list),
        "pr_authors_contributor_count_bot": get_contributor_count(pr_contributor_list, is_bot=True),
        "pr_authors_contributor_count_without_bot": get_contributor_count(pr_contributor_list, is_bot=False)
    }
    return result


def pr_review_contributor_count(client, contributors_index, date, repo_list):
    """ Determine how many active pr review participants there are in the past 90 days """
    pr_comment_contributor_list = get_contributor_list(client, contributors_index, date - timedelta(days=90), date,
                                                       repo_list, "pr_review_date_list")
    result = {
        "pr_review_contributor_count": get_contributor_count(pr_comment_contributor_list),
        "pr_review_contributor_count_bot": get_contributor_count(pr_comment_contributor_list, is_bot=True),
        "pr_review_contributor_count_bot": get_contributor_count(pr_comment_contributor_list, is_bot=True)
    }
    return result


def issue_authors_contributor_count(client, contributors_index, date, repo_list):
    """ Determine how many active issue authors participants there are in the past 90 days """
    issue_contributor_list = get_contributor_list(client, contributors_index, date - timedelta(days=90), date,
                                                  repo_list, "issue_creation_date_list")
    result = {
        "issue_authors_contributor_count": get_contributor_count(issue_contributor_list),
        "issue_authors_contributor_count_bot": get_contributor_count(issue_contributor_list, is_bot=True),
        "issue_authors_contributor_count_without_bot": get_contributor_count(issue_contributor_list, is_bot=False)
    }
    return result


def issue_comments_contributor_count(client, contributors_index, date, repo_list):
    """ Determine how many active issue comments participants there are in the past 90 days """
    issue_comment_contributor_list = get_contributor_list(client, contributors_index, date - timedelta(days=90), date,
                                                          repo_list, "issue_comments_date_list")
    result = {
        "issue_comments_contributor_count": get_contributor_count(issue_comment_contributor_list),
        "issue_comments_contributor_count_bot": get_contributor_count(issue_comment_contributor_list, is_bot=True),
        "issue_comments_contributor_count_without_bot": get_contributor_count(issue_comment_contributor_list, is_bot=False)
    }
    return result


def org_contributor_count(client, contributors_index, date, repo_list):
    """ Number of active code contributors with organization affiliation in the past 90 days """
    from_date = date - timedelta(days=90)
    to_date = date
    commit_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                   "code_commit_date_list")
    from_date_str = from_date.strftime("%Y-%m-%d")
    to_date_str = to_date.strftime("%Y-%m-%d")
    org_contributor_set = set()
    org_contributor_bot_set = set()
    org_contributor_without_bot_set = set()
    org_contributor_detail_dict = {}

    for contributor in commit_contributor_list:
        for org in contributor["org_change_date_list"]:
            author_name = contributor["id_git_author_name_list"][0]
            if check_times_has_overlap(org["first_date"], org["last_date"], from_date_str, to_date_str):
                if org.get("org_name") is not None:
                    org_contributor_set.add(author_name)
                    if contributor["is_bot"]:
                        org_contributor_bot_set.add(author_name)
                    else:
                        org_contributor_without_bot_set.add(author_name)

                org_name = org.get("org_name") if org.get("org_name") else org.get("domain")
                is_org = True if org.get("org_name") else False
                org_contributor_detail_count_set = org_contributor_detail_dict.get(org_name, {}).get("org_contributor_count_set", set())
                org_contributor_detail_count_set.add(author_name)
                org_contributor_detail_dict[org_name] = {
                    "org_name": org_name,
                    "is_org": is_org,
                    "org_contributor_count_set": org_contributor_detail_count_set,
                    "org_contributor_count": len(org_contributor_detail_count_set)
                }
    org_contributor_count_list = []
    for x in org_contributor_detail_dict.values():
        if "org_contributor_count_set" in x:
            del x["org_contributor_count_set"]
        org_contributor_count_list.append(x)
    org_contributor_count_list = sorted(org_contributor_count_list, key=lambda x: x["org_contributor_count"], reverse=True)

    result = {
        'org_contributor_count': len(org_contributor_set),
        'org_contributor_count_bot': len(org_contributor_bot_set),
        'org_contributor_count_without_bot': len(org_contributor_without_bot_set),
        'org_contributor_count_list': org_contributor_count_list
    }
    return result


def bus_factor(client, contributors_index, date, repo_list):
    """Determine the smallest number of people that make 50% of contributions in the past 90 days."""
    from_date = date - timedelta(days=90)
    to_date = date
    commit_contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list,
                                                   "code_commit_date_list")
    bus_factor_count = 0
    author_name_dict = {}  # {"author_name:" commit_count}
    from_date_str = from_date.strftime("%Y-%m-%d")
    to_date_str = to_date.strftime("%Y-%m-%d")
    for item in commit_contributor_list:
        if item["is_bot"]:
            continue
        name = item["id_git_author_name_list"][0]
        commit_date_list = [x for x in sorted(item["code_commit_date_list"]) if from_date_str <= x < to_date_str]
        author_name_dict[name] = author_name_dict.get(name, 0) + len(commit_date_list)
    commit_count_list = [commit_count for commit_count in author_name_dict.values()]
    commit_count_list.sort(reverse=True)
    commit_count_threshold = sum(commit_count_list) * 0.5
    front_commit_count = 0
    for index, commit_count in enumerate(commit_count_list):
        front_commit_count += commit_count
        if commit_count_threshold < front_commit_count:
            bus_factor_count = index + 1
            break
    result = {
        'bus_factor': bus_factor_count
    }
    return result


def get_contributor_list(client, contributors_index, from_date, to_date, repo_list, date_field, page_size=500):
    """ Get the contributors who have contributed in the from_date,to_date time period. """
    result_list = []
    if isinstance(date_field, str):
        date_field_list = [date_field]
    elif isinstance(date_field, list):
        date_field_list = date_field
    for repo in repo_list:
        search_after = []
        while True:
            query = get_contributor_query(repo, date_field_list, from_date, to_date, page_size, search_after)
            contributor_list = client.search(index=contributors_index, body=query)["hits"]["hits"]
            if len(contributor_list) == 0:
                break
            search_after = contributor_list[len(contributor_list) - 1]["sort"]
            result_list = result_list + [contributor["_source"] for contributor in contributor_list]
    return result_list


def get_contributor_count(contributor_list, is_bot=None):
        contributor_set = set()
        for contributor in contributor_list:
            if is_bot is None or contributor["is_bot"] == is_bot:
                if contributor.get("id_platform_login_name_list") and len(
                        contributor.get("id_platform_login_name_list")) > 0:
                    contributor_set.add(contributor["id_platform_login_name_list"][0])
                elif contributor.get("id_git_author_name_list") and len(contributor.get("id_git_author_name_list")) > 0:
                    contributor_set.add(contributor["id_git_author_name_list"][0])
        return len(contributor_set)


def contributor_eco_type_list(client, contributors_index, from_date, to_date, repo_list):
    """ Get an itemized list of contributors in the from_date, to_date time period. """

    def get_eco_contributor_dict(from_date, to_date, contributor_list):
        from_date_str = from_date.isoformat()
        to_date_str = to_date.isoformat()
        eco_contributor_dict = {}
        for contributor in contributor_list:
            is_admin = False
            if contributor.get("admin_date_list") and len(contributor.get("admin_date_list")) > 0 \
                    and contributor["admin_date_list"][0]["first_date"] <= to_date_str:
                is_admin = True
            is_org = False
            org_name = None
            for org in contributor["org_change_date_list"]:
                if check_times_has_overlap(org["first_date"], org["last_date"], from_date_str, to_date_str):
                    if org.get("org_name") is not None:
                        is_org = True
                        org_name = org.get("org_name")
                    break
            contributor_name = None
            if contributor.get("id_platform_login_name_list") and len(
                    contributor.get("id_platform_login_name_list")) > 0:
                contributor_name = contributor["id_platform_login_name_list"][0]
            elif contributor.get("id_git_author_name_list") and len(contributor.get("id_git_author_name_list")) > 0:
                contributor_name = contributor["id_git_author_name_list"][0]

            if is_admin and is_org:
                eco_contributor_dict[contributor_name] = {
                    "ecological_type": "organization manager",
                    "organization": org_name
                }
            elif is_admin and not is_org:
                eco_contributor_dict[contributor_name] = {
                    "ecological_type": "individual manager",
                    "organization": org_name
                }
            elif not is_admin and is_org:
                eco_contributor_dict[contributor_name] = {
                    "ecological_type": "organization participant",
                    "organization": org_name
                }
            elif not is_admin and not is_org:
                eco_contributor_dict[contributor_name] = {
                    "ecological_type": "individual participant",
                    "organization": org_name
                }
            eco_contributor_dict[contributor_name]["is_bot"] = contributor["is_bot"]
        return eco_contributor_dict

    def get_type_contributor_dict(from_date, to_date, contributor_list):
        from_date_str = from_date.isoformat()
        to_date_str = to_date.isoformat()
        type_contributor_dict = {} 
        for contributor in contributor_list:
            contributor_name = None
            type_list = []
            if contributor.get("id_platform_login_name_list") and len(
                    contributor.get("id_platform_login_name_list")) > 0:
                contributor_name = contributor["id_platform_login_name_list"][0]
            elif contributor.get("id_git_author_name_list") and len(contributor.get("id_git_author_name_list")) > 0:
                contributor_name = contributor["id_git_author_name_list"][0]
            
            for date_field in date_field_list:
                contribution_count = len(list(filter(lambda x: from_date_str <= x < to_date_str, contributor.get(date_field, []))))
                if contribution_count > 0:
                    type_list.append({
                        "contribution_type": date_field.replace("_date_list", ""),
                        "contribution": contribution_count
                    })

            type_contributor_dict[contributor_name] = type_list
        return type_contributor_dict


    observe_date_field = ["fork_date_list", "star_date_list"]
    issue_date_field = ["issue_creation_date_list", "issue_comments_date_list"]
    code_date_field = ["pr_creation_date_list", "pr_comments_date_list", "code_commit_date_list"]
    issue_admin_date_field = ["issue_labeled_date_list", "issue_unlabeled_date_list", "issue_closed_date_list", "issue_reopened_date_list",
        "issue_assigned_date_list", "issue_unassigned_date_list", "issue_milestoned_date_list", "issue_demilestoned_date_list",
        "issue_marked_as_duplicate_date_list", "issue_transferred_date_list", 
        "issue_renamed_title_date_list", "issue_change_description_date_list", "issue_setting_priority_date_list", "issue_change_priority_date_list",
        "issue_link_pull_request_date_list", "issue_unlink_pull_request_date_list", "issue_assign_collaborator_date_list", "issue_unassign_collaborator_date_list",
        "issue_change_issue_state_date_list", "issue_change_issue_type_date_list", "issue_setting_branch_date_list", "issue_change_branch_date_list",]
    code_admin_date_field = ["pr_labeled_date_list", "pr_unlabeled_date_list", "pr_closed_date_list", "pr_assigned_date_list",
        "pr_unassigned_date_list", "pr_reopened_date_list", "pr_milestoned_date_list", "pr_demilestoned_date_list", 
        "pr_marked_as_duplicate_date_list", "pr_transferred_date_list", 
        "pr_renamed_title_date_list", "pr_change_description_date_list", "pr_setting_priority_date_list", "pr_change_priority_date_list", 
        "pr_merged_date_list", "pr_review_date_list", "pr_set_tester_date_list", "pr_unset_tester_date_list", "pr_check_pass_date_list", 
        "pr_test_pass_date_list", "pr_reset_assign_result_date_list", "pr_reset_test_result_date_list", "pr_link_issue_date_list", 
        "pr_unlink_issue_date_list", "code_direct_commit_date_list"]
    date_field_list = observe_date_field + issue_date_field + code_date_field + issue_admin_date_field + code_admin_date_field

    contributor_list = get_contributor_list(client, contributors_index, from_date, to_date, repo_list, date_field_list)

    eco_contributor_dict = get_eco_contributor_dict(from_date, to_date, contributor_list)
    type_contributor_dict = get_type_contributor_dict(from_date, to_date, contributor_list)
    result_list = []
    for contributor_name in eco_contributor_dict:
        contribution_type_list = type_contributor_dict.get(contributor_name, [])
        contribution = 0
        contribution_without_observe = 0
        for contribution_type in contribution_type_list:
            count = contribution_type.get("contribution", 0)
            if contribution_type.get("contribution_type") not in "code_code_direct_commit":
                contribution += count
                if contribution_type.get("contribution_type") not in ["star", "fork"]:
                    contribution_without_observe += count
        if contribution == 0:
            continue
        result = {
            "contributor": contributor_name,
            "contribution": contribution,
            "contribution_without_observe": contribution_without_observe,
            "is_bot": eco_contributor_dict.get(contributor_name).get("is_bot"),
            "ecological_type": eco_contributor_dict.get(contributor_name).get("ecological_type"),
            "organization": eco_contributor_dict.get(contributor_name).get("organization"),
            "contribution_type_list": contribution_type_list
        }
        result_list.append(result)
    return {"contributor_eco_type_list": result_list}


def contributor_detail_list(client, contributors_enriched_index, date, repo_list, from_date=None, is_bot=False, filter_mileage=None):
    """ Get detailed list of contributors in from_date, to_date time range. 
    :param filter_mileage: Filter by mileage role, choose from core, regular
    """
    if from_date is None:
        from_date = (date - timedelta(days=90))
    # Largest year in time span
    if (from_date + timedelta(days=365)) < date:
        date = from_date + timedelta(days=365)
    
    def get_core_contributor(contributor_dict):
        """
            50% of all contributions in this timeframe, 
            done by the smallest group of contribution (excluding star, fork contributions)
        """
        contribution_count_dict = {k: v["contribution_without_observe"] for k, v in contributor_dict.items()}
        sorted_dict = {k: v for k, v in
                        sorted(contribution_count_dict.items(), key=lambda item: item[1], reverse=True)}
        target_sum = sum(sorted_dict.values()) * 0.5
        current_sum = 0
        core_contributor = {}
        for k, v in sorted_dict.items():
            current_sum += v
            core_contributor[k] = {**contributor_dict[k], "mileage_type": "core"}
            if current_sum >= target_sum:
                break
        return core_contributor
    
    def get_regular_contributor(contributor_dict, core_contributor):
        """
            Throw out the first 50% (core) of contributions, and the next 30% will be done by the smallest group 
            or the group that contributes 3/4 of the time in this timeframe (excluding star and fork contributions).
        """
        date_list = [x for x in list(pd.date_range(freq='W-MON', start=from_date, end=date))]
        if len(date_list) >= 4:
            weeks = len(date_list) * 3 / 4
        contribution_count_dict = {k: v["contribution_without_observe"] for k, v in contributor_dict.items()}
        sorted_dict = {k: v for k, v in
                        sorted(contribution_count_dict.items(), key=lambda item: item[1], reverse=True)}
        target_sum = sum(sorted_dict.values()) * 0.8
        current_sum = 0
        result_contributor = {}
        for k, v in sorted_dict.items():
            current_sum += v
            result_contributor[k] = {**contributor_dict[k], "mileage_type": "regular"}
            if current_sum >= target_sum:
                break
        for k, v in contributor_dict.items():
            if v["contribution_weeks"] >= weeks:
                result_contributor[k] = {**v, "mileage_type": "regular"}
        core_name = core_contributor.keys()
        return {k: result_contributor[k] for k in result_contributor.keys() if k not in core_name}

    contributor_list = get_contributor_list(client, contributors_enriched_index, from_date, date, \
            repo_list, ["grimoire_creation_date"], 1000)
    sorted_contributor_list = sorted(contributor_list, key=lambda x: x["contributor"])
    contributor_groups = groupby(sorted_contributor_list, key=lambda x: x["contributor"])
    contributor_dict = {}
    ecological_type_order = [
        "organization manager",
        "organization participant",
        "individual manager",
        "individual participant"
    ]
    for key, group in contributor_groups:
        contribution = 0
        contribution_without_observe = 0
        ecological_type_set = set()
        organization_set = set()
        contribution_type_dict = {}
        is_bot_set = set()
        repo_name_set = set()
        for item in list(group):
            contribution += item["contribution"]
            contribution_without_observe += item["contribution_without_observe"]
            ecological_type_set.add(item["ecological_type"])
            organization_set.add(item["organization"])
            is_bot_set.add(item["is_bot"])
            repo_name_set.add(item["repo_name"])
            for contribution_type in item["contribution_type_list"]:
                contribution_type_item = contribution_type_dict.get(contribution_type["contribution_type"], {})
                contribution_type_contribution = contribution_type_item.get("contribution", 0)
                contribution_type_item = {
                    "contribution_type": contribution_type["contribution_type"],
                    "contribution": contribution_type_contribution + contribution_type["contribution"]
                }
                contribution_type_dict[contribution_type["contribution_type"]] = contribution_type_item
        for type in ecological_type_order:
            if type in ecological_type_set:
                ecological_type = type
                break
        contributor_item = {
            "contributor": key,
            "contribution": contribution,
            "contribution_without_observe": contribution_without_observe,
            "ecological_type": ecological_type,
            "organization": list(organization_set)[0] if len(organization_set) > 0 else None,
            "contribution_type_list": list(contribution_type_dict.values()),
            "is_bot": True if True in is_bot_set else False,
            "repo_name": list(repo_name_set),
            "contribution_weeks": len(list(group))
        }
        if is_bot is contributor_item["is_bot"]:
            contributor_dict[key] = contributor_item

    core_contributor = get_core_contributor(contributor_dict)
    regular_contributor = get_regular_contributor(contributor_dict, core_contributor)
    if filter_mileage is None:
        contributor_detail_list = list(core_contributor.values()) + list(regular_contributor.values())
    elif filter_mileage is "core":
        contributor_detail_list = list(core_contributor.values())
    elif filter_mileage is "regular":
        contributor_detail_list = list(regular_contributor.values())

    return {
        "contributor_detail_list": contributor_detail_list,
        "core_count": len(core_contributor),
        "regular_count": len(regular_contributor),
        "casual_count": len(contributor_dict) - len(core_contributor) - len(regular_contributor)
    }
    

def org_all_count(client, contributors_enriched_index, date, repo_list, from_date=None):
    """All organization counts(include commit, issue all actions, PR all actions) in the from_date, to_date time period."""
    if from_date is None:
        from_date = (date-timedelta(days=90))
    query = get_uuid_count_query(option="cardinality", repo_list=repo_list, field="organization.keyword", from_date=from_date, 
                        to_date=date, repo_field="repo_name.keyword")                      
    count = client.search(index=contributors_enriched_index, body=query)[
        'aggregations']['count_of_uuid']['value']
    return {"org_all_count": count}


def contributor_all_count(client, contributors_enriched_index, date, repo_list, from_date=None, is_bot=False):
    """All contributor counts(include commit, issue all actions, PR all actions) in the from_date, to_date time period."""
    if from_date is None:
        from_date = (date-timedelta(days=90))
    query = get_uuid_count_query(option="cardinality", repo_list=repo_list, field="contributor.keyword", from_date=from_date, 
                        to_date=date, repo_field="repo_name.keyword")     
    query["query"]["bool"]["must"].append({
            "match_phrase": {
                "is_bot": "true" if is_bot else "false"
            }
        })                  
    count = client.search(index=contributors_enriched_index, body=query)[
        'aggregations']['count_of_uuid']['value']
    return {"contributor_all_count": count}


def highest_contribution_organization(client, contributors_enriched_index, date, repo_list, from_date=None, is_bot=False):
    """ Name of the organization with the highest contribution in the range from_date and to_date """
    if from_date is None:
        from_date = (date-timedelta(days=90))
    query = get_uuid_count_query(option="terms", repo_list=repo_list, field="organization.keyword", from_date=from_date, 
                        to_date=date, repo_field="repo_name.keyword")
    query["query"]["bool"]["must"].append({
            "match_phrase": {
                "ecological_type": "organization"
            }
        })
    query["query"]["bool"]["must"].append({
            "match_phrase": {
                "is_bot": "true" if is_bot else "false"
            }
        })
    query["aggs"]["count_of_uuid"]["aggs"] = {
        "sum_contribution": {
          "sum": {
            "field": "contribution"
          }
        }
      }
    query["aggs"]["max_sum_contribution"] = {
        "max_bucket": {
            "buckets_path": "count_of_uuid>sum_contribution"
        }
    }
    keys = client.search(index=contributors_enriched_index, body=query)[
        'aggregations']['max_sum_contribution']['keys']
    organization = None
    if len(keys) > 0:
        organization = keys[0]
    return {"highest_contribution_organization": organization}


def highest_contribution_contributor(client, contributors_enriched_index, date, repo_list, from_date=None, is_bot=False):
    """ Name of the contributor with the highest contribution in the range from_date and to_date """
    if from_date is None:
        from_date = (date-timedelta(days=90))
    query = get_uuid_count_query(option="terms", repo_list=repo_list, field="contributor.keyword", from_date=from_date, 
                        to_date=date, repo_field="repo_name.keyword")
    query["query"]["bool"]["must"].append({
            "match_phrase": {
                "is_bot": "true" if is_bot else "false"
            }
        })
    query["aggs"]["count_of_uuid"]["aggs"] = {
        "sum_contribution": {
          "sum": {
            "field": "contribution"
          }
        }
      }
    query["aggs"]["max_sum_contribution"] = {
        "max_bucket": {
            "buckets_path": "count_of_uuid>sum_contribution"
        }
    }
    keys = client.search(index=contributors_enriched_index, body=query)[
        'aggregations']['max_sum_contribution']['keys']
    individual = None
    if len(keys) > 0:
        individual = keys[0]
    return {"highest_contribution_contributor": individual}


def contribution_distribution(client, contributors_enriched_index, date, repo_list, from_date=None, is_bot=False, filter_mileage=None):
    """ Show the distribution of contributions for each ecologically role in the time range from_date, date. 
    :param filter_mileage: Filter by mileage role, choose from core, regular
    """
    if from_date is None:
        from_date = (date-timedelta(days=90))
    # Largest year in time span
    if (from_date + timedelta(days=365)) < date:
        date = from_date + timedelta(days=365)
    contributor_list = contributor_detail_list(client, contributors_enriched_index, date, repo_list, 
        from_date, is_bot, filter_mileage)["contributor_detail_list"]
    if len(contributor_list) == 0:
        return { "contribution_distribution": None}
    total_contribution = sum([item["contribution"] for item in contributor_list])
    sorted_contributor_list = sorted(contributor_list, key=lambda x: x["ecological_type"])
    contributor_groups = groupby(sorted_contributor_list, key=lambda x: x["ecological_type"])

    contribution_data = {}
    for key, group in contributor_groups:
        group = list(group)
        contribution = sum(item["contribution"] for item in group)
        sorted_group = sorted(group, key=lambda x: x["contribution"], reverse=True)
        top_contributor = sorted_group[:10]
        other_contributor = sorted_group[10:]
        detail = [{
            "contributor": item["contributor"],
            "contribution": item["contribution"]
        } for item in top_contributor]
        other_contribution = sum([item["contribution"] for item in other_contributor])
        if other_contribution > 0:
            detail.append({
                "other": "other",
                "contribution": other_contribution
            })

        contribution_data[key] = {
            "ecological_type": key,
            "contribution": contribution,
            "ratio": contribution / total_contribution,
            "detail": detail
        }

    contribution_distribution_data = {
        "total_contribution": total_contribution,
        "organization manager": contribution_data.get("organization manager", None),
        "organization participant": contribution_data.get("organization participant", None),
        "individual manager": contribution_data.get("individual manager", None),
        "individual participant": contribution_data.get("individual participant", None),
    }
    return { "contribution_distribution": contribution_distribution_data}


def organization_distribution(client, contributors_enriched_index, date, repo_list, from_date=None, is_bot=False, filter_mileage=None):
    """ Show the distribution of contributions for each organization in the time range from_date, date. 
    :param filter_mileage: Filter by mileage role, choose from core, regular
    """
    if from_date is None:
        from_date = (date-timedelta(days=90))
    # Largest year in time span
    if (from_date + timedelta(days=365)) < date:
        date = from_date + timedelta(days=365)
    contributor_list = contributor_detail_list(client, contributors_enriched_index, date, repo_list, 
        from_date, is_bot, filter_mileage)["contributor_detail_list"]
    org_contributor_list = [item for item in contributor_list if item["organization"] is not None]
    if len(org_contributor_list) == 0:
        return { "organization_distribution": None}
    total_contribution = sum([item["contribution"] for item in contributor_list])
    sorted_contributor_list = sorted(org_contributor_list, key=lambda x: x["organization"])
    contributor_groups = groupby(sorted_contributor_list, key=lambda x: x["organization"])

    contribution_data = {}
    for key, group in contributor_groups:
        group = list(group)
        contribution = sum(item["contribution"] for item in group)
        sorted_group = sorted(group, key=lambda x: x["contribution"], reverse=True)
        top_contributor = sorted_group[:10]
        other_contributor = sorted_group[10:]
        detail = [{
            "contributor": item["contributor"],
            "contribution": item["contribution"]
        } for item in top_contributor]
        other_contribution = sum([item["contribution"] for item in other_contributor])
        if other_contribution > 0:
            detail.append({
                "other": "other",
                "contribution": other_contribution
            })

        contribution_data[key] = {
            "organization": key,
            "contribution": contribution,
            "ratio": contribution / total_contribution,
            "detail": detail
        }
    contribution_data = dict(sorted(contribution_data.items(), key=lambda x: x[1]["contribution"], reverse=True))
    organization_distribution_data = {
        "total_contribution": total_contribution,
        **contribution_data
    }
    return { "organization_distribution": organization_distribution_data}


def contributor_distribution(client, contributors_enriched_index, date, repo_list, from_date=None, is_bot=False, filter_mileage=None):
    """ Show the distribution of contributor for each ecologically role in the time range from_date, date. 
    :param filter_mileage: Filter by mileage role, choose from core, regular
    """
    if from_date is None:
        from_date = (date-timedelta(days=90))
    # Largest year in time span
    if (from_date + timedelta(days=365)) < date:
        date = from_date + timedelta(days=365)
    contributor_list = contributor_detail_list(client, contributors_enriched_index, date, repo_list, 
        from_date, is_bot, filter_mileage)["contributor_detail_list"]
    if len(contributor_list) == 0:
        return { "contributor_distribution": None}
    total_contributor_count = len(contributor_list)
    sorted_contributor_list = sorted(contributor_list, key=lambda x: x["ecological_type"])
    contributor_groups = groupby(sorted_contributor_list, key=lambda x: x["ecological_type"])

    contributor_data = {}
    for key, group in contributor_groups:
        group = list(group)
        contributor_count = len(group)
        sorted_group = sorted(group, key=lambda x: x["contribution"], reverse=True)
        top_contributor = sorted_group[:10]
        other_contributor = sorted_group[10:]
        detail = [{
            "contributor": item["contributor"],
            "contributor_count": 1
        } for item in top_contributor]
        other_contributor_count = len(other_contributor)
        if other_contributor_count > 0:
            detail.append({
                "other": "other",
                "contributor_count": other_contributor_count
            })

        contributor_data[key] = {
            "ecological_type": key,
            "contributor_count": contributor_count,
            "ratio": contributor_count / total_contributor_count,
            "detail": detail
        }

    contributor_distribution_data = {
        "total_contributor_count": total_contributor_count,
        "organization manager": contributor_data.get("organization manager", None),
        "organization participant": contributor_data.get("organization participant", None),
        "individual manager": contributor_data.get("individual manager", None),
        "individual participant": contributor_data.get("individual participant", None),
    }
    return { "contributor_distribution": contributor_distribution_data}