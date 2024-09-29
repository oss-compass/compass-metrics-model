import requests
import json

class TechnicalSkillModel:
    def __init__(self, user_login, token):
        self.user_login = user_login
        self.token = token
        self.url = "https://api.github.com/graphql"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    # Method to fetch watched repositories
    def fetch_watched_repositories():
        query = """
        query {
          user(login: "%s") {
            watching(first: 10) {
              nodes {
                nameWithOwner
                url
              }
            }
          }
        }
        """ % self.user_login

        response = requests.post(self.url, json={'query': query}, headers=self.headers)

        if response.status_code == 200:
            data = response.json()

            if 'errors' in data:
                print("Errors returned by the API:")
                print(json.dumps(data['errors'], indent=4))
                return

            if data.get('data') is None or data['data'].get('user') is None:
                print("Error: 'user' data is missing from the response.")
                return

            watched_repos = []
            for repo in data['data']['user']['watching']['nodes']:
                watched_repos.append({
                    "nameWithOwner": repo["nameWithOwner"],
                    "url": repo["url"]
                })

            
            print("\nWatched Repositories:")
            #for repo in watched_repos:
                #print(f"Repo: {repo['nameWithOwner']}, URL: {repo['url']}")

            # Save to a JSON file
            output_file = "./data_request/watched_repos.json"
            with open(output_file, "w") as file:
                json.dump(watched_repos, file, indent=4)

            print(f"Output saved to {output_file}")
        else:
            print(f"Failed to fetch watched repositories: {response.status_code}")

    # fetch the repositories user contributed to
    def fetch_contributed_repositories(self):
        output_file = "./data_request/contributed_repos.json"
    
        query = """
        query {
          user(login: "%s") {
            repositoriesContributedTo(first: 100, contributionTypes: [COMMIT, PULL_REQUEST, ISSUE]) {
              nodes {
                nameWithOwner
                url
                stargazers {
                  totalCount
                }
                forkCount
                createdAt
                updatedAt
                isFork
                description
              }
            }
          }
        }
        """ % self.user_login

        # Send the POST request to the GitHub API
        response = requests.post(self.url, json={'query': query}, headers=self.headers)

        if response.status_code == 200:
            data = response.json()

            if 'errors' in data:
                print("Errors returned by the API:")
                print(json.dumps(data['errors'], indent=4))
                return

            if data.get('data') is None or data['data'].get('user') is None:
                print("Error: 'user' data is missing from the response.")
                return

            contributed_repos = []
            for repo in data["data"]["user"]["repositoriesContributedTo"]["nodes"]:
                contributed_repos.append({
                    "nameWithOwner": repo["nameWithOwner"],
                    "url": repo["url"],
                    "stargazersCount": repo["stargazers"]["totalCount"],
                    "forkCount": repo["forkCount"],
                    "description": repo["description"],
                    "createdAt": repo["createdAt"],
                    "updatedAt": repo["updatedAt"],
                    "isFork": repo["isFork"]
                })

            # print out contributed repositories
            print("\nRepositories Contributed To:")
            
            # save the output to a JSON file
            with open(output_file, "w") as file:
                json.dump(contributed_repos, file, indent=4)

            print(f"Output saved to {output_file}")
        else:
            print(f"Failed to fetch contributed repositories: {response.status_code}")

    # fetch topics for contributed repositories
    def fetch_repo_topics(self, contributed_repos_file):
        output_file = "./data_request/contributed_repo_topics.json"
        
        # load contributed repos from file
        with open(contributed_repos_file, 'r') as file:
            contributed_repos = json.load(file)

        query = """
        query($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) {
            repositoryTopics(first: 10) {
              edges {
                node {
                  topic {
                    name
                  }
                }
              }
            }
          }
        }
        """

        repo_topics = []
        for repo in contributed_repos:
            name_with_owner = repo['nameWithOwner']
            owner, name = name_with_owner.split('/')
            variables = {
                "owner": owner,
                "name": name
            }

            response = requests.post(self.url, json={'query': query, 'variables': variables}, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                topics = data['data']['repository']['repositoryTopics']['edges']
                topic_names = [topic['node']['topic']['name'] for topic in topics]

                repo_topics.append({
                    "nameWithOwner": name_with_owner,
                    "topics": topic_names
                })

                print(f"Repository: {name_with_owner}")
                print(f"Topics: {', '.join(topic_names)}\n")
            else:
                print(f"Failed to fetch topics for {name_with_owner}: {response.status_code}")

        # save to a JSON file
        with open(output_file, "w") as file:
            json.dump(repo_topics, file, indent=4)

        print(f"Output saved to {output_file}")

    # fetch the user's owned repositories
    def fetch_user_owned_repositories(self):
        query = """
        query($login: String!) {
          user(login: $login) {
            repositories(first: 100, ownerAffiliations: OWNER, orderBy: {field: CREATED_AT, direction: DESC}) {
              nodes {
                nameWithOwner
                url
                description
                stargazerCount
                forkCount
                isPrivate
                createdAt
                updatedAt
              }
              pageInfo {
                hasNextPage
                endCursor
              }
            }
          }
        }
        """

        variables = {
            "login": self.user_login
        }

        response = requests.post(self.url, json={'query': query, 'variables': variables}, headers=self.headers)

        if response.status_code == 200:
            data = response.json()

            if 'errors' in data:
                print("Errors returned by the API:")
                print(json.dumps(data['errors'], indent=4))
                return

            # Get the list of repositories
            repositories = data['data']['user']['repositories']['nodes']

            for repo in repositories:
                print(f"Repo: {repo['nameWithOwner']}, URL: {repo['url']}, Stars: {repo['stargazerCount']}, Forks: {repo['forkCount']}")

            # Save to a JSON file
            output_file = "./data_request/user_owned_repositories.json"
            with open(output_file, "w") as file:
                json.dump(repositories, file, indent=4)

            print(f"Output saved to {output_file}")
        else:
            print(f"Failed to fetch owned repositories: {response.status_code}")
