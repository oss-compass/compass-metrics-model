'''
Descripttion: 获取openharmony的数据
version: V1.0
Author: zyx
Date: 2024-08-24 08:57:02
LastEditors: zyx
LastEditTime: 2024-09-20 03:35:09
'''
import requests
import json

# url = r"https://ohpm.openharmony.cn/ohpmweb/registry/oh-package/openapi/v1/detail/@pura/harmony-utils"
# request = requests.get(url)
# content = json.loads(request.content)['body']
# downloads = content["downloads"]#下载量
# likes = content["likes"]
# dependencies = content["dependencies"]["total"]


def package_url_to_package(package_url):
    name_str = package_url.split('/')[-1].replace("%2F","/")
    return name_str

def get_openharmony_package_info(user="@pura",package_name="harmony-utils"):
    '''
    return likes,downloads_all,downloads_60,dependent,versions.values(),repository
    '''

    API_url = f"https://ohpm.openharmony.cn/ohpmweb/registry/oh-package/openapi/v1/detail/{user}/{package_name}"

    response = requests.get(API_url)

    if response.status_code == 200:
        # data_set = response.json()
        content = json.loads(response.content)['body']
        downloads_all = content["downloads"]
        downloads_60 = content["popularity"] # 过去六十天的下载量
        likes = content["likes"] # 点赞数
        dependent = content["dependent"]["total"] # 依赖数
        versions = content["versions"] # 版本更新时间
        repository = content["repository"]
        
        #print()

        return likes,downloads_all,downloads_60,dependent,versions.values(),repository
    else:
        return ConnectionError(f"{response.status_code} error")
        

       
if __name__=="__main__":
    # 要查询分析的OpenHarmony包的URL
    package_url = 'https://ohpm.openharmony.cn/#/cn/detail/@pura%2Fharmony-utils'
    get_openharmony_package_info()
