import requests
from utils import get_github_token,get_gitee_token
import datetime
def get_github_versions(repo_url):
    api_url = repo_url.replace("github.com", "api.github.com/repos") + "/tags"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {get_github_token()}'
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        tags = response.json()
        versions = [tag['name'] for tag in tags]
        return versions
    else:
        return None

def get_gitee_versions(repo_url):
    api_url = repo_url.replace("gitee.com", "gitee.com/api/v5/repos") + "/tags"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'token {get_gitee_token()}'
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        tags = response.json()
        versions = [tag['name'] for tag in tags]
        return versions
    else:
        return None


def vul_detect_time(repo_url):
    '''evluate the average time of vulnerability repair in the latest 5 versions'''

    package = repo_url.split("/")[-1]
    if "github.com" in repo_url:
        versions = get_github_versions(repo_url)[:5]
    elif "gitee.com" in repo_url:
        versions = get_gitee_versions(repo_url)[:5]
    else:
        return ValueError("Unsupported url. Use 'github' or 'gitee'.")
    url = "https://api.osv.dev/v1/query"
    repair_time = []
    for version in versions:
        data = {
            "package": {"name": package},
            "version": version
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            vul_data = response.json()
            if len(vul_data)>0:
                for vulns in vul_data.values():
                    for vuln in vulns:
                        modified_time = datetime.datetime.strptime(vuln['modified'][:vuln['modified'].find("T")], "%Y-%m-%d")
                        published_time = datetime.datetime.strptime(vuln['published'][:vuln['published'].find("T")], "%Y-%m-%d")
                        if modified_time>published_time:
                            repair_time.append(modified_time-published_time)
                        # repair_time.append((modified_time-published_time).days)
    if len(repair_time)>0:
        avg_time = sum(repair_time, datetime.timedelta(0)) / len(repair_time)
        res = {"get_vul_detect_time": avg_time.days}
        return res
    else:
        return None
        
if __name__ == "__main__":
    github_repo_url = "https://github.com/mruby/mruby"
    gitee_repo_url = "https://gitee.com/mirrors/opencv"
    print("GitHub Versions:", get_github_versions(github_repo_url))
    print("Gitee Versions:", get_gitee_versions(gitee_repo_url))
    # print("Average Vulnerability Repair Time:", get_vul_avg_time(github_repo_url))
    print("Average Vulnerability Repair Time:", vul_detect_time(gitee_repo_url))
