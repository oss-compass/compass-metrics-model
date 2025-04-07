from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from typing import List

from compass_common.datetime import str_to_datetime
from .git_metrics import commit_count
from compass_metrics.document_metric.utils import get_gitee_token,get_github_token
import requests


def activity_quarterly_contribution(client, contributors_index: str, repo_list: List[str],
                                    version: str) -> dict:
    """
    获取最近一年中每季度的代码贡献量。

    参数：
        client: 数据库客户端
        contributors_index: 贡献者索引名称
        repo_list: 仓库列表
        date: 评估日期

    返回：
        dict: 包含季度贡献量的统计数据，包括：
            - activity_quarterly_contribution: 所有贡献量
            - activity_quarterly_contribution_bot: 机器人贡献量
            - activity_quarterly_contribution_without_bot: 非机器人贡献量
    """

    # 通过version查询时间
    repo = repo_list[0]
    date = get_github_versionPublishAt(repo, version)

    if date is None:
        return {
            'activity_quarterly_contribution': [],
            'activity_quarterly_contribution_bot': [],
            'activity_quarterly_contribution_without_bot': [],
            'activity_quarterly_contribution_info': "Failed to obtain version release time"
        }
    date = str_to_datetime(date)
    result = []
    result_bot = []
    result_without_bot = []

    # 获取当前季度的结束时间（将日期调整到季度末）
    current_quarter_end = date.replace(
        month=((date.month - 1) // 3 * 3 + 3),
        day=1
    )
    # 调整到月末
    if current_quarter_end.month == 3:
        current_quarter_end = current_quarter_end.replace(day=31)
    elif current_quarter_end.month == 6:
        current_quarter_end = current_quarter_end.replace(day=30)
    elif current_quarter_end.month == 9:
        current_quarter_end = current_quarter_end.replace(day=30)
    elif current_quarter_end.month == 12:
        current_quarter_end = current_quarter_end.replace(day=31)

    # 计算最近4个季度的贡献量
    for i in range(4):
        # 计算季度的起止时间
        quarter_end = current_quarter_end - relativedelta(months=3 * i)
        quarter_start = quarter_end - relativedelta(months=3) + timedelta(days=1)

        quarter_data = commit_count(
            client,
            contributors_index,
            quarter_end,
            repo_list,
            from_date=quarter_start
        )

        result.append(quarter_data['commit_count'])
        result_bot.append(quarter_data['commit_count_bot'])
        result_without_bot.append(quarter_data['commit_count_without_bot'])

    return {
        'activity_quarterly_contribution': result,
        'activity_quarterly_contribution_bot': result_bot,
        'activity_quarterly_contribution_without_bot': result_without_bot,
        'activity_quarterly_contribution_info': "success"
    }

def get_github_versionPublishAt(repo_url,version):
    api_url = repo_url.replace("github.com", "api.github.com/repos") + "/releases"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {get_github_token()}'
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        releases = response.json()
        for release in releases:
            if release['tag_name'] == version:
                return release['published_at']
    else:
        return None

def get_gitee_versionPublishAt(repo_url,version):
    api_url = repo_url.replace("gitee.com", "gitee.com/api/v5/repos") + "releases"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'token {get_gitee_token()}'
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        releases = response.json()
        for release in releases:
            if release['tag_name'] == version:
                return release['published_at']
    else:
        return None

if __name__ == '__main__':
    repo_name = "https://github.com/mathjax/MathJax"
    get_github_versionPublishAt("https://github.com/kotest/kotest","v5.9.0")