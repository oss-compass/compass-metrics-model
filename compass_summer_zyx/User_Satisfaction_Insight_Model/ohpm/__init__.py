'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2024-09-05 02:13:52
LastEditors: zyx
LastEditTime: 2024-09-29 11:23:46
'''
import sys
sys.path.append(".")#外部需要..
from utils import *
from ohpm.bug_issue import bug_issue
from ohpm.ohpm import get_openharmony_package_info
from ohpm.star import ohpm_star
from ohpm.stability_of_version_updates import stability_of_version_updates
from datetime import datetime, timezone ,timedelta
# from ..utils import *
from math import *
import re
import os

        
# 全局变量
SAVE_PATH_METRIC = r"save_metric"
SAVE_PATH_SCORE = r"save_score"
THRESHOLD_MATRIX = read_json_file(r"ohpm/threshold.json")
WEIGHT_MATRIX = read_json_file(r"ohpm/weight.json")
GITHUB_BENCHMARK_MATRIX =  read_json_file(r"ohpm/github_normalize_json/benchmark.json")
GITHUB_MAX_SCORE = read_json_file(r"ohpm/github_normalize_json/max_score.json")
GITHUB_MIN_SCORE =  read_json_file(r"ohpm/github_normalize_json/min_score.json")
GITEE_BENCHMARK_MATRIX =  read_json_file(r"ohpm/gitee_normalize_json/benchmark.json")
GITEE_MAX_SCORE = read_json_file(r"ohpm/gitee_normalize_json/max_score.json")
GITEE_MIN_SCORE =  read_json_file(r"ohpm/gitee_normalize_json/min_score.json")

#创建相关路径
if not os.path.exists(SAVE_PATH_METRIC):
    os.mkdir(SAVE_PATH_METRIC)
if not os.path.exists(SAVE_PATH_SCORE):
    os.mkdir(SAVE_PATH_SCORE)
    
class OHPM_USER_MODEL:
    
    def __init__(self,url) -> None:
        '''
        
        '''
        self.url = url
        self.beginDate,self.endDate = self.get_time()
        self.ohpm_user,self.ohpm_package_name = self.get_ohpm_user_package_name()
        self.likes,self.downloads,self.popularity,self.dependent,self.version,self.repository= get_openharmony_package_info(self.ohpm_user,self.ohpm_package_name)
        self.flag,self.user,self.package_name = self.get_package_user()
    
    def get_ohpm_user_package_name(self):
        '''使用正则表达式匹配用户名和包名 '''
        
        pattern = r'@([^/]+)%2F(.+)$'
        match = re.search(pattern, self.url)

        if match:
            username = match.group(1)
            package_name = match.group(2)
            return "@"+username,package_name
        else:
            ValueError("未找到用户名和包名信息。")

    def get_time(self) ->None:
        '''获取要处理的时间'''

        # 获取当前 UTC 时间
        endDate = datetime.now(timezone.utc)

        beginDate = endDate - timedelta(days=300, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)

        # 转换为 ISO 8601 格式
        endDate = endDate.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        beginDate= beginDate.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

        # 输出时间字符串
        return beginDate,endDate  # 例如：2023-08-28T13:45:23.123Z

    def get_package_user(self):

        match = re.match(r'https://github.com/([^/]+)/([^/]+)', self.repository) or re.match(r'https://gitee.com/([^/]+)/([^/]+)', self.repository)
        if match:
            if "github" in  self.url:
                return "github",match.group(1),match.group(2)
            else:
                return "gitee",match.group(1),match.group(2)
        else:
            raise ValueError("提供链接有误，请输入github项目或gitee项目链接,例：https://github.com/pytorch/pytorch")
        
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
        '''获取最终结果'''
        
        metrics = {
            "bug_issue" : bug_issue(self.repository, self.beginDate, self.endDate),
            "download" : self.popularity,
            "software_universality" : self.dependent,
            "star" : self.likes + ohpm_star(self.flag,self.user,self.package_name),
            "version_update_stability": stability_of_version_updates(self.version)
        }

        save_name_metric = "ohpm_metric_"+self.flag+"_"+self.package_name+"_"+self.user+".json"
        save_name_score = "ohpm_score_"+self.flag+"_"+self.package_name+"_"+self.user+".json"

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
    import re
    a = OHPM_USER_MODEL("https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fmaterialprogressbar")
    metrics,score = a.get_user_score()

    # endDate = datetime.now(timezone.utc)

    # beginDate = endDate - timedelta(days=30, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)

    # # 转换为 ISO 8601 格式
    # endDate = endDate.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    # beginDate= beginDate.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    print()