#ttps://gitee.com/api/v5/repos/changweizhang/ChatUI/subscribers?page=1&per_page=20

import requests
from datetime import datetime, timedelta

# GitHub API endpoint for listing stargazers of a repository
url = 'https://api.github.com/repos/pytorch/pytorch/stargazers'

# 替换为您要查询的 GitHub 仓库的所有者和仓库名称
owner = 'Owner_Name'
repo = 'Repo_Name'

# 计算过去 90 天的日期
ninety_days_ago = datetime.now() - timedelta(days=90)

# 初始化一个空列表来存储过去 90 天内的 star 记录
recent_stars = []

# 发起请求获取所有 star 记录
response = requests.get(url, params={'per_page': 100})
if response.status_code == 200:
    stargazers = response.json()
    recent_stars.extend([stargazer for stargazer in stargazers if datetime.fromisoformat(stargazer['starred_at']) > ninety_days_ago])

# 输出过去 90 天内的 star 记录
for stargazer in recent_stars:
    print(stargazer)