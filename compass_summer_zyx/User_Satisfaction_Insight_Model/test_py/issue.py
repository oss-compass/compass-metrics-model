'''
Descripttion: 
version: 
Author: zyx
Date: 2024-08-13 18:21:32
LastEditors: zyx
LastEditTime: 2024-08-18 16:17:57
'''
import time
from datetime import timedelta
def Stability_of_version_updates(issue_time):
    '''
    issue_time：{version:time,1.0:5112}
    '''
    time_intervals = []
    time_list = sorted(list(issue_time.values()))
    for i in range(1, len(time_list)):
        interval_seconds = time_list[i] - time_list[i-1]
        interval_days = interval_seconds / (60 * 60 * 24)  # 将秒转换为天
        time_intervals.append(interval_days)
    print(time_intervals)
    
    return time_intervals
        
if __name__=="__main__":
    Stability_of_version_updates({
            "1.0.0": 1716283409460,
            "1.0.1": 1716798123485,
            "1.0.2": 1716966931462,
            "1.0.3": 1720430775687,
            "1.0.4": 1721899578538,
            "1.0.5": 1722311522497,
            "1.0.6": 1722479194550
        })