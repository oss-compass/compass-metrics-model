'''
Descripttion: software universality，通过https://deps.dev/_/s/pypi/p/{package_name}/versions
version: 
Author: zyx
Date: 2024-08-17 16:39:45
LastEditors: zyx
LastEditTime: 2024-09-19 09:20:53
'''
import requests
import re

def get_pypi_dependentCount(package_name):
    '''
    return dependentCount
    '''
    if package_name == "pytorch":
        package_name="torch"
    
    api_url = f"https://deps.dev/_/s/pypi/p/{package_name}/versions"
    response = requests.get(api_url)
    if response.status_code==200:
        #print(response.text)
        data = response.json()
        # createdAt = data['versions'][0]['createdAt']
        dependentCount = data['versions'][0]['dependentCount']
        return dependentCount

    else:
        raise ValueError(f"{api_url} get {response.status_code}")
   



if __name__=="__main__":
    url = "https://gitee.com/luoxunzhao/JYH_OSSRPP"
    print(get_pypi_dependentCount("torch"))

