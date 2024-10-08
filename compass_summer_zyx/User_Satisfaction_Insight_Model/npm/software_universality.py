'''
Descripttion: software universality
version: 
Author: zyx
Date: 2024-08-17 16:39:45
LastEditors: zyx
LastEditTime: 2024-09-16 06:50:46
'''
import requests
import re
from math import *
import csv
def get_npm_dependentCount(package_name):
    '''
    return dependentCount
    '''
    api_url = f"https://deps.dev/_/s/npm/p/{package_name}/versions"
    response = requests.get(api_url)
    if response.status_code==200:
        #print(response.text)
        data = response.json()
        createdAt = data['versions'][0]['createdAt']
        dependentCount = data['versions'][0]['dependentCount']
        return dependentCount

    else:
        raise ValueError(f"{api_url} get {response.status_code}")
   
# def ans(package_name):
#     score = get_pypi_dependentCount(package_name)      
#     return package_name,(1+ ( log(score+1) - log(0+1) ) / ( log(700000) - log(0+1) ) *(100-1)),score

# def normalize(package_name, min_score, max_score):
#     """ score normalize """
#     score = get_pypi_dependentCount(package_name)   
#     return package_name,(score - min_score) / (max_score - min_score)*100,score


#69147 39816
if __name__=="__main__":
    #url = "https://gitee.com/luoxunzhao/JYH_OSSRPP"
    libraries = ['lodash', 'chalk', 'request', 'commander', 'react', 'express', 'debug', 'async', 'fs-extra', 'moment', 'prop', 'types', 'react', 'dom', 'bluebird', 'underscore', 'vue', 'axios', 'tslib', 'mkdirp', 'glob', 'yargs', 'colors']
    # for i in libraries:
    #     with open("npm_dependent_yuan.csv","a+",newline="") as f:
    #         writer = csv.writer(f)
    #         writer.writerow(normalize(i,0,665386))
    #     print(ans(i))
    # print(ans("chalk"))

