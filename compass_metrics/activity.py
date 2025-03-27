from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from typing import List
from .git_metrics import commit_count_quarterly


def activity_quarterly_contribution(client, contributors_index: str, repo_list: List[str], date: datetime) -> dict:
    """
    获取指定季度的代码贡献量。

    参数：
        client: 数据库客户端
        contributors_index: 贡献者索引名称
        repo_list: 仓库列表
        date: 查询的季度的最后一天

    返回：
        dict: 包含季度贡献量的统计数据，包括：
            - activity_quarterly_contribution: 所有贡献量
            - activity_quarterly_contribution_bot: 机器人贡献量
            - activity_quarterly_contribution_without_bot: 非机器人贡献量
    """
    
    # 计算季度的起止时间
    quarter_end = date
    quarter_start = quarter_end - relativedelta(months=3) + timedelta(days=1)

    quarter_data = commit_count_quarterly(
        client,
        contributors_index,
        quarter_end,
        repo_list,
        from_date=quarter_start
    )

    result = quarter_data['commit_count_quarterly']
    result_bot = quarter_data['commit_count_quarterly_bot']
    result_without_bot = quarter_data['commit_count_quarterly_without_bot']

    return {
        'activity_quarterly_contribution': result,
        'activity_quarterly_contribution_bot': result_bot,
        'activity_quarterly_contribution_without_bot': result_without_bot
    }