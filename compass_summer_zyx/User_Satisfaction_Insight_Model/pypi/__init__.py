'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2024-08-29 09:55:57
LastEditors: zyx
LastEditTime: 2024-09-29 11:13:14
'''
import sys
sys.path.append(".")#外部需要..
from utils import *
from pypi.bug_issue import bug_issue
from pypi.comprehensive_downloads import comprehensive_downloads
from pypi.software_universality import get_pypi_dependentCount
from pypi.star import pypi_star
from pypi.stability_of_version_updates import stability_of_version_updates
from datetime import *
import re
from math import log
import os

# 全局变量
SAVE_PATH_METRIC = r"save_metric"
SAVE_PATH_SCORE = r"save_score"
THRESHOLD_MATRIX = read_json_file(r"pypi/threshold.json")
WEIGHT_MATRIX = read_json_file(r"pypi/weight.json")
GITHUB_BENCHMARK_MATRIX =  read_json_file(r"pypi/github_normalize_json/benchmark.json")
GITHUB_MAX_SCORE = read_json_file(r"pypi/github_normalize_json/max_score.json")
GITHUB_MIN_SCORE =  read_json_file(r"pypi/github_normalize_json/min_score.json")
GITEE_BENCHMARK_MATRIX =  read_json_file(r"pypi/gitee_normalize_json/benchmark.json")
GITEE_MAX_SCORE = read_json_file(r"pypi/gitee_normalize_json/max_score.json")
GITEE_MIN_SCORE =  read_json_file(r"pypi/gitee_normalize_json/min_score.json")

#创建相关路径
if not os.path.exists(SAVE_PATH_METRIC):
    os.mkdir(SAVE_PATH_METRIC)
if not os.path.exists(SAVE_PATH_SCORE):
    os.mkdir(SAVE_PATH_SCORE)

class PYPI_USER_MODEL:
    
    def __init__(self,url) -> None:

        self.url = url
        self.flag,self.user,self.package_name = self.get_package_user()
        self.beginDate,self.endDate= self.get_time()
        
        
    def get_package_user(self):

        match = re.match(r'https://github.com/([^/]+)/([^/]+)', self.url) or re.match(r'https://gitee.com/([^/]+)/([^/]+)', self.url)
        if match:
            if "github" in  self.url:
                return "github",match.group(1),match.group(2)
            else:
                return "gitee",match.group(1),match.group(2)
        else:
            raise ValueError("提供链接有误，请输入github项目或gitee项目链接,例：https://github.com/pytorch/pytorch")

    def get_time(self) ->None:
        '''
        description: 获取当前时间
        return normalize_score
        '''
        
        # 获取当前 UTC 时间
        endDate = datetime.now(timezone.utc)

        beginDate = endDate - timedelta(days=90, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)

        # 转换为 ISO 8601 格式
        endDate = endDate.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        beginDate= beginDate.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

        # 输出时间字符串
        return beginDate,endDate  # 例如：2023-08-28T13:45:23.123Z
    
    def normalize_user_model(self,score,benchmark,min_score):

        '''
        description:
            @parm:score,指标当前值
            @parm:benchmark,指标基准值,在最大值的基础上提升
            @parm:max_score,指标最小值

        return normalize_score
        '''

        return 1+ ( log(score+1) - log(min_score+1) ) / ( log(benchmark) - log(min_score+1) ) *(100-1)
    
    def normalize_osscompass(self,score, min_score, max_score):
        """ score normalize """
 
        return (score - min_score) / (max_score - min_score)*100
        
    def get_user_score(self):
        '''获取user_model得分'''

        save_name_score = "py_score_"+self.flag+"_"+self.package_name+"_"+self.user+".json"
        save_name_metric = "py_metric_"+self.flag+"_"+self.package_name+"_"+self.user+".json"

        # 数据初始化
        metrics = {
            "bug_issue" : bug_issue(self.url, self.beginDate, self.endDate),
            "download" : comprehensive_downloads(self.package_name,self.beginDate),
            "software_universality" : get_pypi_dependentCount(self.package_name),
            "star" : pypi_star(self.flag,self.user,self.package_name),
            "version_update_stability": stability_of_version_updates(self.package_name)
        }
        write_json(metrics,os.path.join(SAVE_PATH_METRIC,save_name_metric))

        metrics["bug_issue"] = -metrics["bug_issue"]
        metrics["version_update_stability"] = -metrics["version_update_stability"]

        
        # 判断采用哪种指标
        threshold = THRESHOLD_MATRIX
        if self.flag == "github": 
            benchmark_score = GITHUB_BENCHMARK_MATRIX
            max_score = GITHUB_MAX_SCORE
            min_score = GITHUB_MIN_SCORE

        else: 
            benchmark_score = GITHUB_BENCHMARK_MATRIX
            max_score = GITHUB_MAX_SCORE
            min_score = GITHUB_MIN_SCORE


        # 归一化
        normalize2 = ["bug_issue","version_update_stability"] #需要osscompass的normalize的方法
        
        score = {"Overall_scoring":0}
        for key,value in metrics.items():

            if key in normalize2:
                if metrics[key]>threshold[key]:
                    score[key] = 100
                else:
                    score[key] = self.normalize_osscompass(metrics[key],min_score[key],max_score[key])
                score["Overall_scoring"] += score[key]*WEIGHT_MATRIX[key]
            else:
                if metrics[key]>threshold[key]:
                    score[key] = 100
                else:
                    score[key] = self.normalize_user_model(metrics[key],benchmark_score[key],min_score[key])
                score["Overall_scoring"] += score[key]*WEIGHT_MATRIX[key]
        
        write_json(score,os.path.join(SAVE_PATH_SCORE,save_name_score))
       

        return metrics,score

if __name__=="__main__":
    a = PYPI_USER_MODEL("https://github.com/pytorch/pytorch")
    a.get_user_score()
    