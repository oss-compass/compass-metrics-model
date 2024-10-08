'''
Descripttion: 版本更新的稳定性，通过updates判定，采用接口https://deps.dev/_/s/pypi/p/{package_name}/versions
version: 1.0
Author: zyx
Date: 2024-08-18 16:49:32
LastEditors: zyx
LastEditTime: 2024-09-19 09:21:13
'''
import requests
from datetime import *

# #{'version': '2.4.1', 'symbolicVersions': [], 'createdAt': 1725477084, 'isDefault': True, 'dependentCount': 10262}
# def stability_of_version_updates(issue_time):
#     '''
#     issue_time：{version:time,1.0:5112}
#     '''
#     time_intervals = []
#     time_list = sorted(list(issue_time))
#     for i in range(1, len(time_list)):
#         interval_seconds = time_list[i] - time_list[i-1]
#         interval_days = interval_seconds / (60 * 60 * 24)  # 将秒转换为天
#         time_intervals.append(interval_days)
#     return time_intervals

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
    if package_name == "pytorch":
        package_name="torch"
    url = f"https://deps.dev/_/s/pypi/p/{package_name}/versions"
    response = requests.get(url)

    if response.status_code == 200:
        data =  response.json()
        if len(data["versions"])!=0:
            return cacluate_time(data["versions"])
        else:
             return ValueError(f"Error: {package_name} is unexisting")

if __name__=="__main__":
    print(stability_of_version_updates("requests"))


    

# package_name = "torch"  # 替换为你要查询的包名
# last_update = get_pypi_package_last_update(package_name)
# print(f"The last update of {package_name} on PyPI was on: {last_update}")
