'''
Descripttion: 
version: 
Author: zyx
Date: 2024-08-18 16:38:00
LastEditors: zyx
LastEditTime: 2024-09-19 09:14:55
'''
import requests
from datetime import datetime
from math import *
import csv
from datetime import *
def binary_search(data, target_date):
    '''二分查找'''
    low, high = 0, len(data) - 1
    while low <= high:
        mid = (low + high) // 2
        if data[mid]['date'].replace(tzinfo=timezone.utc) > target_date:
            high = mid - 1
        else:
            low = mid + 1
    return low

def comprehensive_downloads(package_name,begin_Date):
    '''
    package_name:
    
    begin_Date:%Y-%m-%d
    '''
    API_URL = f"https://pypistats.org/api/packages/{package_name}/overall"
    response = requests.get(API_URL)
    if response.status_code == 200:
        repo_info = response.json()
        data = repo_info.get('data',[])
        for item in data:
            item['date'] = datetime.strptime(item['date'], '%Y-%m-%d')
        
        # 查找 begin_Date 之后的下载量
         
        target_date = datetime.fromisoformat(begin_Date.replace('Z', '+00:00'))
        start_index = binary_search(data, target_date)

        # 累加 'date' 大于 begin_Date 的 downloads
        total_downloads = sum(item['downloads'] for item in data[start_index:])

        # 输出结果
        return total_downloads
    
def normalize1(package_name,begin_Date):
    score = comprehensive_downloads(package_name,begin_Date)      
    return package_name,(1+ ( log(score+1) - log(0+1) ) / ( log(11020825309+1000) - log(0+1) ) *(100-1)),score


def normalize(package_name,begin_Date, min_score, max_score):
    """ score normalize """
    score = comprehensive_downloads(package_name,begin_Date)   
    return package_name,(score - min_score) / (max_score - min_score)*100,score


if __name__=="__main__":
    libraries = [
    "boto3",
    "urllib3",
    "requests",
    "botocore",
    "setuptools",
    "certifi",
    "idna",
    "charset-normalizer",
    "typing-extensions",
    "packaging",
    "python-dateutil",
    "grpcio-status",
    "six",
    "pyyaml",
    "s3transfer",
    "cryptography",
    "aiobotocore",
    "numpy",
    "fsspec",
    "cffi",
    "torch",
    "lxml",
    "xpath",
    "scapy"
    ]
    
    for i in libraries:
        with open("download_yuan.csv","a+",newline="") as f:
            writer = csv.writer(f)
            writer.writerow(normalize(i,'2024-7-16',0,11020825309))
        #print(ans(i,'2024-7-16'))

