from compass_metrics.db_dsl import get_contributor_query
from compass_common.datetime import get_time_diff_months, check_times_has_overlap
from datetime import timedelta


def contributor_count(client, contributors_index, date, repo_list):
    """ Determine how many active code commit authors, pr authors, review participants, issue authors,
    and issue comments participants there are in the past 90 days """

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
        "contributor_count_without_bot": get_contributor_count(D1_contributor_list, is_bot=False),
        "active_C2_contributor_count": get_contributor_count(commit_contributor_list),
        "active_C1_pr_create_contributor": get_contributor_count(pr_contributor_list),
        "active_C1_pr_comments_contributor": get_contributor_count(pr_comment_contributor_list),
        "active_C1_issue_create_contributor": get_contributor_count(issue_contributor_list),
        "active_C1_issue_comments_contributor": get_contributor_count(issue_comment_contributor_list),
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



def get_contributor_list(client, contributors_index, from_date, to_date, repo_list, date_field):
    """ Get the contributors who have contributed in the from_date,to_date time period. """
    result_list = []
    for repo in repo_list:
        search_after = []
        while True:
            query = get_contributor_query(repo, date_field, from_date, to_date, 500, search_after)
            contributor_list = client.search(index=contributors_index, body=query)["hits"]["hits"]
            if len(contributor_list) == 0:
                break
            search_after = contributor_list[len(contributor_list) - 1]["sort"]
            result_list = result_list + [contributor["_source"] for contributor in contributor_list]
    return result_list
