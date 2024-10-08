'''
Descripttion: software universality
version: 
Author: zyx
Date: 2024-08-17 16:39:45
LastEditors: zyx
LastEditTime: 2024-09-18 12:48:56
'''

import requests
import json

def get_software_universality(user,package_name):
    '''调用用户'''
    url = f"https://ohpm.openharmony.cn/ohpmweb/registry/oh-package/openapi/v1/detail/{user}/{package_name}"
    request = requests.get(url)
    content = json.loads(request.content)['body']
    downloads_all = content["downloads"]
    downloads_60 = content["popularity"] # 过去六十天的下载量
    likes = content["likes"] # 点赞数
    dependencies = content["dependencies"]["total"] # 依赖数
    versions = content["versions"] # 版本更新时间

    return dependencies
    


if __name__=="__main__":
    get_software_universality()