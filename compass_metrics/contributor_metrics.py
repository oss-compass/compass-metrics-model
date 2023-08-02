from compass_metrics.common import get_contributor_list
from compass_common.datetime import get_time_diff_months
from datetime import timedelta


def contributor_count(client, contributors_index, date, repo_list):
    """ Definition: Determine how many active code commit authors, pr authors, review participants, issue authors,
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
