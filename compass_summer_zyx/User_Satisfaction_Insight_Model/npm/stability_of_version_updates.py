'''
Descripttion: 版本更新的稳定性，通过updates判定 51778
version: 1.0
Author: zyx
Date: 2024-08-18 16:49:32
LastEditors: zyx
LastEditTime: 2024-09-30 00:45:12
'''
import requests
from datetime import datetime
import statistics
import re
import csv
# #github获取方式
# def get_platform_and_repo(url):
#     if 'github.com' in url:
#         platform = 'github'
#         repo = re.search(r'github\.com/([^/]+/[^/]+)', url).group(1)
#     elif 'gitee.com' in url:
#         platform = 'gitee'
#         repo = re.search(r'gitee\.com/([^/]+/[^/]+)', url).group(1)
#     else:
#         raise ValueError("Unsupported URL. Please provide a GitHub or Gitee repository URL.")
#     return platform, repo

# def get_release_dates(platform, repo, token=None):
#     headers = {}
#     if platform == 'github':
#         url = f'https://api.github.com/repos/{repo}/releases'
#         if token:
#             headers['Authorization'] = f'token {token}'
#     elif platform == 'gitee':
#         url = f'https://gitee.com/api/v5/repos/{repo}/releases'
#         if token:
#             headers['Authorization'] = f'token None'
    
#     response = requests.get(url, headers=headers)
#     response.raise_for_status()
#     releases = response.json()
    
#     release_dates = [datetime.strptime(release['created_at'], '%Y-%m-%dT%H:%M:%S%z') for release in releases]
#     return release_dates

# def calculate_time_diffs(dates):
#     dates.sort()
#     time_diffs = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
    
#     return [i for i in time_diffs if i !=0]

# def main(repo_url, token=None):
#     platform, repo = get_platform_and_repo(repo_url)
#     release_dates = get_release_dates(platform, repo, token)
    
#     if len(release_dates) < 2:
#         print("Not enough data to calculate intervals.")
#         return
    
#     time_diffs = calculate_time_diffs(release_dates)
#     avg_diff = statistics.mean(time_diffs)
#     last_diff = time_diffs[-1]
    
#     ans = {
#         "Average update interval:":avg_diff,
#         "Last update interval": last_diff,
#         "Difference between last and average": last_diff - avg_diff
#     }
#     with open(r"ans.csv","a+",newline="") as f:
#         writer = csv.writer(f)
#         writer.writerow([repo_url,avg_diff,last_diff,last_diff - avg_diff])
def cacluate_time(date_strings):
    # 将字符串转换为datetime对象
    
    dates = [datetime.fromtimestamp(date_str['createdAt']) for date_str in date_strings if 'createdAt' in date_str.keys()]
    dates.sort()

    # 计算每两项之间的时间间隔
    intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates) - 1)]

    average_interval = sum(intervals) / len(intervals)

    # 减去平均时间间隔的三分之一
    adjusted_intervals = [-(interval - average_interval - (average_interval / 3)) for interval in intervals if interval!=0] #修正量为average_interval / 3

    return adjusted_intervals[-1]

def stability_of_version_updates(package_name):
    '''
    package_name: 包名
    '''
    url = f"https://deps.dev/_/s/npm/p/{package_name}/versions"
    response = requests.get(url)

    if response.status_code == 200:
        data =  response.json()
        if len(data["versions"])!=0:
            return cacluate_time(data["versions"])
        else:
             return ValueError(f"Error: {package_name} is unexisting")

if __name__=="__main__":
    print(stability_of_version_updates("express"))

    # file_path = r"top500.csv"

    # #repo_url = "https://github.com/spring-projects/spring-security"

    # token = token if token else None

    # with open(file_path,"r") as file:
    #     reader = csv.reader(file)
    #     for read in reader:
    #         if read[0] == "项目":
    #             continue
    #         else:
    #             try:
    #                 main(read[0], token)
    #             except:
    #                 continue


    
