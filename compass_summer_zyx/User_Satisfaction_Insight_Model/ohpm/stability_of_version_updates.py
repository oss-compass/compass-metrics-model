'''
Descripttion: 版本更新的稳定性，通过updates判定 
version: 1.0
Author: zyx
Date: 2024-08-18 16:49:32
LastEditors: zyx
LastEditTime: 2024-09-19 03:43:43
'''
# import requests
from datetime import datetime

def stability_of_version_updates(date_strings):
    # 将字符串转换为datetime对象
    
    dates = [datetime.fromtimestamp(date_str/1000) for date_str in date_strings]
    dates.sort()

    # 计算每两项之间的时间间隔
    intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates) - 1)]

    average_interval = sum(intervals) / len(intervals)

    # 减去平均时间间隔的三分之一
    adjusted_intervals = [-(interval - average_interval - (average_interval / 3)) for interval in intervals if interval!=0] #修正量为average_interval / 3

    return adjusted_intervals[-1]


    
if __name__=="__main__":
    #ac = datetime.fromtimestamp(1716283409460/1000)


    package_name = "torch"  # 替换为你要查询的包名
    last_update = stability_of_version_updates({'1.0.0': 1716283409460, '1.0.1': 1716798123485, '1.0.2': 1716966931462, '1.0.3': 1720430775687, '1.0.4': 1721899578538, '1.0.5': 1722311522497, '1.0.6': 1722479194550, '1.0.7': 1724122731741, '1.0.8': 1724642269302, '1.0.9': 1725243860122, '1.1.0': 1726305485652})
    print(f"The last update of {package_name} on OHPM was on: {last_update}")
