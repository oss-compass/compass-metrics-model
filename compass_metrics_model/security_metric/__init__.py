'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2025-03-04 11:16:48
LastEditors: zyx
LastEditTime: 2025-03-20 17:01:05
'''
from vul_detect_time import vul_detect_time
from vulnerability_feedback_channels import vulnerablity_feedback_channels
from get_vul_level import get_vul_levels_metrics
from utils import get_github_token,get_gitee_token,save_json

class VulnerabilityMetrics:
    def __init__(self, repo_list):
        self.repo_list = repo_list
        self.vul_detect_time = {}
        self.vulnerablity_feedback_channels = {}
        self.vul_levels_metrics = {}

        
    def get_vul_detect_time(self):
        for repo_url in self.repo_list:
            self.vul_detect_time[repo_url] = vul_detect_time(repo_url)
        get_vul_detect_time = self.vul_detect_time
        return get_vul_detect_time #{"get_vul_detect_time": avg_time.days}

    
    def get_vulnerablity_feedback_channels(self):
        for repo_url in self.repo_list:
            self.vulnerablity_feedback_channels[repo_url] = vulnerablity_feedback_channels(repo_url)
        get_vulnerablity_feedback_channels = self.vulnerablity_feedback_channels
        return get_vulnerablity_feedback_channels #{"get_vulnerablity_feedback_channels":0, "vulnerablity_feedback_channels":[]}

    
    def get_vul_levels(self):
        for repo_url in self.repo_list:
            self.vul_levels_metrics[repo_url] = get_vul_levels_metrics(repo_url)
        get_vul_levels = self.vul_levels_metrics
        return get_vul_levels #{"get_vul_levels":0,"vul_levels":{"high": 0, "medium": 0, "low": 0},"vul_level_details":[]}

    
if __name__ == "__main__":
    repo_url =['https://github.com/numpy/numpy']
    metrics = VulnerabilityMetrics(x for x in repo_url)
    # print(metrics.get_vul_detect_time())
    # save_json(metrics.get_vul_detect_time(), 'vul_detect_time.json')
    # save_json(metrics.get_vulnerablity_feedback_channels(), 'vulnerablity_feedback_channels.json')
    # print(metrics.get_vulnerablity_feedback_channels())