'''
Descripttion: 版本更新的稳定性，通过updates判定 
version: 1.0
Author: zyx
Date: 2024-08-18 16:49:32
LastEditors: zyx
LastEditTime: 2024-09-29 10:28:35
'''
import requests

from datetime import datetime

import os
import matplotlib.pyplot as plt

# 给定的日期列表
date_strings1 = [
    '2018-12-07T18:56:01', '2019-02-05T13:41:09', '2019-04-30T23:21:02', '2021-10-21T14:45:53',
    '2021-12-15T21:58:45', '2022-01-27T20:04:52', '2022-03-10T16:41:49', '2022-06-28T16:25:48',
    '2022-08-05T17:26:39', '2022-10-28T16:35:37', '2022-12-15T20:15:37', '2019-08-08T16:01:26',
    '2019-10-10T15:16:45', '2019-11-07T17:45:55', '2020-01-15T23:22:37', '2020-04-21T16:01:10',
    '2020-06-18T16:31:41', '2020-07-28T15:52:16', '2020-10-27T15:58:18', '2020-12-10T16:22:02',
    '2021-03-04T20:36:11', '2021-03-25T15:54:32', '2021-06-15T15:09:35', '2021-09-20T22:30:00',
    '2023-03-17T22:43:08', '2023-05-08T16:35:32', '2023-10-04T16:53:01', '2023-11-15T16:42:26',
    '2023-12-14T21:46:00', '2024-01-30T17:30:06', '2024-02-22T19:16:58', '2024-03-27T21:06:46',
    '2024-04-24T15:44:27', '2024-06-05T16:40:40', '2024-07-24T15:27:17'
]
def cacluate_time(date_strings,save_name,name):
    # 将字符串转换为datetime对象
    
    dates = [datetime.fromisoformat(date_str) for date_str in date_strings][10:]
    dates.sort()

    # 计算每两项之间的时间间隔
    intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates) - 1)]

    average_interval = sum(intervals) / len(intervals)

    # 减去平均时间间隔的三分之一
    adjusted_intervals = [interval - (average_interval / 3) for interval in intervals if interval!=0]
        

    # 输出结果
    # for i, interval in enumerate(intervals):
    #     print(f"Interval between {date_strings[i]} and {date_strings[i+1]}: {interval}")
    plt.figure(figsize=(10, 6))
    plt.plot(adjusted_intervals, marker='o', linestyle='-', color='b')
    plt.xlabel("Interval Index")
    plt.ylabel("Days Between Releases")
    plt.title(os.path.basename(save_name.replace(".png",""))+" Time Intervals Between Dates")
    plt.grid(True)

    # 添加时间节点的标签
    for i, interval in enumerate(intervals):
        plt.text(i, interval, str(interval), ha='center', va='bottom')

    # # 设置横坐标轴的刻度标签
    # plt.xticks(ticks=range(len(name[10:])), labels=name[10:])

    #plt.show()
    plt.savefig(save_name)
def stability_of_version_updates(issue_time):
    '''
    issue_time：{version:time,1.0:5112}
    '''
    time_intervals = []
    time_list = sorted(list(issue_time))
    for i in range(1, len(time_list)):
        interval_seconds = time_list[i] - time_list[i-1]
        interval_days = interval_seconds / (60 * 60 * 24)  # 将秒转换为天
        time_intervals.append(interval_days)
    print(time_intervals)
    
    return time_intervals

def get_pypi_package_last_update(package_name,save_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)

    if response.status_code == 200:

        issue_time = []
        name = []

        data = response.json()
        a = data['releases']
        for key,value in data['releases'].items():
            if len(value)>0:
                issue_time.append(value[0]['upload_time'])
                name.append(key)


        return cacluate_time(issue_time,save_name,name)
    
    else:
        return None


    
python_libraries = [
    "NumPy",
    "Pandas",
    "Matplotlib",
    "Scikit-learn",
    "TensorFlow",
    "Keras",
    "Requests",
    "Flask",
    "Django",
    "BeautifulSoup"
]
npmLibraries = [
    "Express",
    "React",
    "Lodash",
    "Moment",
    "Axios",
    "Webpack",
    "Babel",
    "TypeScript",
    "Jest",
    "Next.js"
]
if not os.path.exists(r"test_all/update_issue1"):
    os.mkdir(r"test_all/update_issue1")
for package_name in python_libraries:
# package_name = "request"  # 替换为你要查询的包名

    last_update = get_pypi_package_last_update(package_name,os.path.join(r"test_all/update_issue1",package_name+".png"))

# print(f"The last update of {package_name} on PyPI was on: {last_update}")
