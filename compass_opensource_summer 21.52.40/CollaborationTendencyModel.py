import requests
import json
from datetime import datetime, timedelta

class CollaborationTendencyModel:
    def __init__(self, user_login, token):
        self.user_login = user_login
        self.token = token
        self.url = "https://api.github.com/graphql"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.fixed_today = datetime(2024, 9, 7)
        self.week_intervals = [(self.fixed_today - timedelta(weeks=i), self.fixed_today - timedelta(weeks=i+1)) for i in range(12)]
        self.start_date = self.fixed_today - timedelta(weeks=12)  # Start date for calculating PR contributions

    # Method to fetch commit contributions for each week
    def fetch_commits_for_week(self, start_date, end_date):
        query = """
        query($login: String!, $startDate: DateTime!, $endDate: DateTime!) {
          user(login: $login) {
            contributionsCollection(from: $endDate, to: $startDate) {
              totalCommitContributions
              commitContributionsByRepository(maxRepositories: 5) {
                repository {
                  nameWithOwner
                }
                contributions {
                  totalCount
                }
              }
            }
          }
        }
        """
        variables = {
            "login": self.user_login,
            "startDate": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "endDate": end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        response = requests.post(self.url, json={'query': query, 'variables': variables}, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(json.dumps(data['errors'], indent=4))
                return 0
            if data['data']['user']['contributionsCollection'] is None:
                return 0
            return data['data']['user']['contributionsCollection']['totalCommitContributions']
        else:
            print(f"Failed to fetch commit data: {response.status_code}")
            return 0

    # Method to fetch total PRs and calculate average per week for the last 3 months
    def fetch_prs_in_last_three_months(self):
        query = """
        query($login: String!) {
          user(login: $login) {
            pullRequests(first: 100, states: [OPEN, MERGED, CLOSED], orderBy: {field: CREATED_AT, direction: DESC}) {
              nodes {
                createdAt
              }
            }
          }
        }
        """
        variables = {"login": self.user_login}

        response = requests.post(self.url, json={'query': query, 'variables': variables}, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            pr_nodes = data['data']['user']['pullRequests']['nodes']
            pr_in_last_three_months = [pr for pr in pr_nodes if datetime.strptime(pr['createdAt'], "%Y-%m-%dT%H:%M:%SZ") >= self.start_date]
            total_prs = len(pr_in_last_three_months)
            average_prs_per_week = total_prs / 12
            print(f"Total PRs: {total_prs}, Average PRs per week: {average_prs_per_week:.2f}")
            return total_prs, average_prs_per_week
        else:
            print(f"Failed to fetch PR data: {response.status_code}")
            return 0, 0

    # Method to fetch PR contributions and compare them with total PRs in repositories
    def fetch_and_compare_pr_contributions(self):
        query_user_prs = """
        query($login: String!) {
          user(login: $login) {
            pullRequests(first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
              nodes {
                repository {
                  nameWithOwner
                }
                createdAt
              }
            }
          }
        }
        """
        response = requests.post(self.url, json={'query': query_user_prs, 'variables': {"login": self.user_login}}, headers=self.headers)

        if response.status_code == 200:
            user_prs = response.json()['data']['user']['pullRequests']['nodes']
            repo_total_prs = {}
            for pr in user_prs:
                repo_name = pr['repository']['nameWithOwner']
                repo_owner, repo_repo = repo_name.split('/')
                repo_total_prs[repo_name] = self.get_repo_total_prs(repo_owner, repo_repo)
            self.calculate_pr_percentage(user_prs, repo_total_prs)
        else:
            print(f"Failed to fetch user PRs: {response.status_code}")

    def get_repo_total_prs(self, repo_owner, repo_name):
        query_repo_prs = f"""
        query {{
          repository(owner: "{repo_owner}", name: "{repo_name}") {{
            pullRequests(states: [OPEN, MERGED, CLOSED]) {{
              totalCount
            }}
          }}
        }}
        """
        response = requests.post(self.url, json={'query': query_repo_prs}, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            return data['data']['repository']['pullRequests']['totalCount']
        else:
            return 0

    def calculate_pr_percentage(self, user_prs, repo_total_prs):
        user_pr_contributions = {}
        for pr in user_prs:
            repo_name = pr['repository']['nameWithOwner']
            pr_date = datetime.strptime(pr['createdAt'], "%Y-%m-%dT%H:%M:%SZ")
            if pr_date >= self.start_date:
                user_pr_contributions[repo_name] = user_pr_contributions.get(repo_name, 0) + 1
        percentage_contributions = {repo: (user_pr_contributions[repo] / repo_total_prs.get(repo, 1)) * 100 for repo in user_pr_contributions}
        for repo, percentage in percentage_contributions.items():
            print(f"{repo}: {percentage:.2f}% of total PRs")

    # Method to fetch and calculate dynamic issue contributions for each week
    def fetch_issues_for_week(self, start_date, end_date):
        query = """
        query($login: String!, $afterCursor: String) {
          user(login: $login) {
            issues(first: 100, after: $afterCursor) {
              nodes {
                title
                createdAt
                state
                repository {
                  nameWithOwner
                }
              }
              pageInfo {
                endCursor
                hasNextPage
              }
            }
          }
        }
        """
        issues = []
        variables = {"login": self.user_login, "afterCursor": None}
        has_next_page = True
        while has_next_page:
            response = requests.post(self.url, json={'query': query, 'variables': variables}, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                issues.extend(data['data']['user']['issues']['nodes'])
                has_next_page = data['data']['user']['issues']['pageInfo']['hasNextPage']
                if has_next_page:
                    variables['afterCursor'] = data['data']['user']['issues']['pageInfo']['endCursor']
            else:
                return []
        return [issue for issue in issues if start_date <= datetime.strptime(issue['createdAt'], "%Y-%m-%dT%H:%M:%SZ") <= end_date]

    # Method to compute weekly dynamic issues
    def compute_weekly_dynamic_issues(self):
        dynamic_issue_indications = []
        for i, (week_start, week_end) in enumerate(self.week_intervals):
            total_issues_for_week = len(self.fetch_issues_for_week(week_start, week_end))
            dynamic_issue_number = total_issues_for_week / 12 if total_issues_for_week > 0 else 0
            dynamic_issue_indications.append({
                "week": f"Week {12 - i} ({week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')})",
                "dynamic_issue_number": dynamic_issue_number
            })
        for week_info in dynamic_issue_indications:
            print(f"{week_info['week']}: {week_info['dynamic_issue_number']:.2f} average issues")


'''if __name__ == "__main__":
    model = CollaborationTendencyModel(user_login="posva", token="")

    # Fetch commits for each week
    model.compute_weekly_dynamic_issues()

    # Fetch PRs in the last three months and calculate averages
    model.fetch_prs_in_last_three_months()

    # Fetch and compare PR contributions with total PRs in repositories
    model.fetch_and_compare_pr_contributions()
'''