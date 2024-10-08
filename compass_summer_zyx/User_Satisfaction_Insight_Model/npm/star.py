'''
Descripttion: 获取star信息
version: V1.0
Author: zyx
Date: 2024-08-24 08:57:02
LastEditors: zyx
LastEditTime: 2024-09-30 00:21:43
'''
import requests
from datetime import datetime, timedelta
from datetime import datetime
from dateutil import tz
from dateutil.parser import parse

GITHUB_HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}
GITEE_HEADERS = {'Authorization': f'token {GITEE_TOKEN}'} if GITEE_TOKEN else {}

TIME_DELTA = 90 #过去90天的star count结果


def get_recent_gitee_stars_count(owner, repo):
    '''采用倒叙方式进行查找'''

    url = f'https://gitee.com/api/v5/repos/{owner}/{repo}'

    response = requests.get(url,headers=GITEE_HEADERS)
    if response.status_code == 200:
        data = response.json()
        star = data.get('stargazers_count', 0)

    # star信息变量初始化
    url = f'https://gitee.com/api/v5/repos/{owner}/{repo}/stargazers?page=1&per_page=20'
    count = 0
    page = star//20+1
    begin_date= datetime.now(tz=tz.gettz('Asia/Shanghai')) - timedelta(days=TIME_DELTA)
    break_flag = 1


    while break_flag:
        params = {
            'page': str(page),
            'per_page': 20 # 每页数量，根据实际情况调整
        }
        response = requests.get(url, params=params,headers=GITEE_HEADERS)

        if response.status_code == 200:
            stargazers = response.json()
            if not stargazers:
                break

            for stargazer in stargazers:
                starred_at = datetime.fromisoformat(stargazer['star_at']).replace(tzinfo=tz.gettz('Asia/Shanghai'))#strptime(stargazer['star_at'], '%Y-%m-%dT%H:%M:%S%z'), tzinfo=tz.gettz('Asia/Shanghai')
                if starred_at > begin_date:
                    count += 1
                else:
                    break_flag = 0

            page -= 1
        else:
            print(f"Failed to fetch stargazers on page {page}. Status code: {response.status_code}")
            break

    return count

def get_recent_github_stars_count_rest_api(owner, repo):
    '''采用倒叙方式进行查找'''
    
    url = f'https://api.github.com/repos/{owner}/{repo}'

    headers = {
        'Accept': 'application/vnd.github.v3.star+json', # 获取包含 star 时间的数据
        'Authorization': f'token {GITHUB_TOKEN}'  # 使用 GitHub Token 进行身份验证
    }

    response = requests.get(url,headers=GITHUB_HEADERS)
    if response.status_code == 200:
        data = response.json()
        star = data.get('stargazers_count', 0)

    # star信息变量初始化
    url = f'https://api.github.com/repos/{owner}/{repo}/stargazers'
    count = 0
    page = star//30+1
    begin_date= datetime.now(tz=tz.gettz('Asia/Shanghai')) - timedelta(days=TIME_DELTA)
    break_flag = 1

    while break_flag:
        params = {
            'page': 1050,
            'per_page': 30 # 每页数量，根据实际情况调整
        }
        response = requests.get(url, params=params,headers=headers)

        if response.status_code == 200:
            stargazers = response.json()
            if not stargazers:
                break

            for stargazer in stargazers:
                starred_at = datetime.strptime(stargazer['starred_at'].replace('Z', '+00:00'), '%Y-%m-%dT%H:%M:%S%z').astimezone(tz.gettz('Asia/Shanghai'))
                if starred_at > begin_date:#datetime.fromisoformat(stargazer['starred_at']).replace(tzinfo=tz.gettz('Asia/Shanghai'))#
                    count += 1
                else:
                    break_flag = 0

            page -= 1
        else:
            print(f"Failed to fetch stargazers on page {page}. Status code: {response.status_code}")
            break

    return count


def get_recent_github_stars_count(owner, repo):
    '''采用倒叙方式进行查找'''
    query = """
        query {
        repository(owner: "%s", name: "%s") {
            stargazers(last: 100, before: %s) {
            edges {
                node {
                login
                }
                starredAt
            }
            pageInfo {
                hasPreviousPage
                startCursor
            }
            }
        }
        }
    """
    # GraphQL API URL
    url = 'https://api.github.com/graphql'

    # 请求头部
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'token {GITHUB_TOKEN}'  # 如果需要授权的话
    }

    # 发起 GraphQL 查询请求
    start_cursor = "null"
    total_stars = 0
    break_flag = 0
    begin_date= datetime.now(tz=tz.gettz('Asia/Shanghai')) - timedelta(days=TIME_DELTA)
    while True:
        response = requests.post(url, headers=headers, json={'query': query % (owner,repo,start_cursor)})
        #print(query % start_cursor)
        if break_flag:
            break

        if response.status_code != 200:
            print("Failed to retrieve data. Status code:", response.status_code)
            break

        data = response.json()
        stargazers = data['data']['repository']['stargazers']['edges']

        for star in stargazers:
            starred_at = datetime.strptime(star['starredAt'].replace('Z', '+00:00'), '%Y-%m-%dT%H:%M:%S%z').astimezone(tz.gettz('Asia/Shanghai'))#star['starredAt']#
            # 检查star是否在begin_date以后
            if starred_at >= begin_date:
                total_stars += 1

            else:
                # 已经到达早于指定日期的数据，结束循环
                break_flag = 1
        #print(starred_at)
        if not data['data']['repository']['stargazers']['pageInfo']['hasPreviousPage']:
            break

        start_cursor = '"'+str(data['data']['repository']['stargazers']['pageInfo']['startCursor'])+'"'

        #返回所有结果
    return total_stars

def npm_star(flag, owner, repo):
    '''
    flag: github or gitee
    owner:仓库所有者 
    repo:仓库名称
    '''
    if flag == "github":
        return get_recent_github_stars_count(owner, repo)
    elif flag == "gitee":
        return get_recent_gitee_stars_count(owner, repo)
    else:
        raise ValueError("链接github,gitee")

if __name__=="__main__":
    OWNER = 'pytorch'
    REPO = 'pytorch'
    recent_stars_count = get_recent_github_stars_count(OWNER, REPO)
    print(f"过去九十天的 star 数：{recent_stars_count}")