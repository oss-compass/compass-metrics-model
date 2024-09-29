'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2024-09-06 09:25:41
LastEditors: zyx
LastEditTime: 2024-09-29 11:24:07
'''


from pypi import PYPI_USER_MODEL
from npm import NPM_USER_MODEL
from ohpm import OHPM_USER_MODEL
import re
import requests

class USER_MODEL:

    def __init__(self,url) -> None:
        self.url = url
        self.owner,self.repo = self.extract_repo_info()
        self.language = self.get_main_language_from_github() or self.get_main_language_from_gitee()

    def extract_repo_info(self):
        '''获取包名和拥有者'''
        match = re.match(r'https://github.com/([^/]+)/([^/]+)', self.url) or re.match(r'https://gitee.com/([^/]+)/([^/]+)', self.url)
        if match:
            return match.group(1), match.group(2)
        else:
            return None, None
        
    def get_main_language_from_github(self):
        '''获取github主语言'''
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/languages"
        response = requests.get(url)

        if response.status_code == 200:
            languages = response.json()
            if languages:
                # 按照字节数排序，找到字节数最多的语言
                main_language = max(languages, key=languages.get)
                return f"{main_language}"
            else:
                return None
        else:
            return None
    
    def get_main_language_from_gitee(self):
        '''获取gitee主语言'''
        # return "XXXX"
        url = f"https://gitee.com/api/v5/repos/{self.owner}/{self.repo}/languages"
        response = requests.get(url)

        if response.status_code == 200:
            languages = response.json()
            if languages:
                # 按照字节数排序，找到字节数最多的语言
                main_language = max(languages, key=languages.get)
                return f"{main_language}"
            else:
                return None
        else:
            return None

    def user_model_score(self):
        "调整对应评分"

        if "openharmony" in self.url:
            return OHPM_USER_MODEL(self.url).get_user_score()
        else:
            if self.language == "Python":
                return PYPI_USER_MODEL(self.url).get_user_score()
                
            elif self.language == "JavaScript":
                return NPM_USER_MODEL(self.url).get_user_score()
            else:
                return "当前链接语言还未包含"

if __name__=="__main__":
    # a = USER_MODEL("https://github.com/jquery/jquery")
    
    # print(a.user_model_score())
    # PYPY = github_links = [
    #     "https://github.com/boto/boto3",
    #     "https://github.com/urllib3/urllib3",
    #     "https://github.com/psf/requests",
    #     "https://github.com/boto/botocore",
    #     "https://github.com/pypa/setuptools",
    #     "https://github.com/certifi/python-certifi",
    #     "https://github.com/kjd/idna",
    #     "https://github.com/python/charset-normalizer",
    #     "https://github.com/python/typing",
    #     "https://github.com/pypa/packaging",
    #     "https://github.com/dateutil/dateutil",
    #     "https://github.com/grpc/grpc",
    #     "https://github.com/benjaminp/six",
    #     "https://github.com/yaml/pyyaml",
    #     "https://github.com/boto/s3transfer",
    #     "https://github.com/pyca/cryptography",
    #     "https://github.com/aio-libs/aiobotocore",
    #     "https://github.com/numpy/numpy",
    #     "https://github.com/intake/filesystem_spec",
    #     "https://github.com/roncffe/cffi",
    #     "https://github.com/pytorch/pytorch",
    #     "https://github.com/lxml/lxml",
    #     "https://github.com/secdev/scapy"
    # ]

    # print(github_links)
    # for i in github_links:
    #     try:
    #         a = USER_MODEL(i)
    #         a.user_model_score()
    #     except:
            # continue
    
    a = USER_MODEL("https://ohpm.openharmony.cn/#/cn/detail/@piaojin%2Fpjtabbar")
    a.user_model_score()
