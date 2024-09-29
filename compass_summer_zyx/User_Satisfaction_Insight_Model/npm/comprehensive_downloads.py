'''
Descripttion: 统计过去九十天的结果,只能更新到过去90天的
version: 
Author: zyx
Date: 2024-08-18 16:38:00
LastEditors: zyx
LastEditTime: 2024-09-20 02:55:00
'''
import requests
from datetime import *

def comprehensive_downloads(repo_url, beginDate, endDate):
    '''
    获取指定时间段内 npm 包的下载量
    repo_url: npm 包的 URL (例如: https://www.npmjs.com/package/express)
    beginDate: 下载统计的起始日期，格式为 YYYY-MM-DD,类型为str
    endDate: 下载统计的结束日期，格式为 YYYY-MM-DD,类型为str
    '''
    try:
        # 从 repo_url 中提取包名
        package_name = repo_url.split("/")[-1]

        # 格式化日期
        # date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        # 将 datetime 对象格式化为 '%Y-%m-%d' 格式的字符串
        # formatted_date = date_obj.strftime('%Y-%m-%d')
        
        from_date = datetime.strptime(beginDate, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
        until_date = datetime.strptime(endDate, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')

        # 构建 API 请求 URL
        API_url = f"https://npm-stat.com/api/download-counts?package={package_name}&from={from_date}&until={until_date}"
        response = requests.get(API_url)

        # 如果请求成功
        if response.status_code == 200:
            data = response.json()
            downloads = data.get(package_name, {})
            total_downloads = sum(downloads.values()) #针对请求求和

            return total_downloads
            # {
            #     "package": package_name,
            #     "from": str(from_date),
            #     "until": str(until_date),
            #     "total_downloads": total_downloads
            # }
        else:
            return ConnectionAbortedError(f"请求失败，状态码: {response.status_code}")
            # return None

    except Exception as e:
        ValueError(f"发生异常: {e}")
        return None

if __name__=="__main__":
    repo_url = "https://www.npmjs.com/package/express"
    beginDate = "2024-07-04"
    endDate = "2024-09-04"
    result = comprehensive_downloads(repo_url, beginDate, endDate)
    if result:
        print(f"包名: {result['package']}")
        print(f"时间段: {result['from']} 到 {result['until']}")
        print(f"下载量: {result['total_downloads']}")

