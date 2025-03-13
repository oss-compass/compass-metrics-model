'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2025-03-04 11:16:48
LastEditors: zyx
LastEditTime: 2025-03-04 16:55:48
'''
from vul_detect_time import vul_detect_time
from vulnerability_feedback_channels import vulnerablity_feedback_channels
from get_vul_level import get_vul_levels_metrics
from utils import get_github_token,get_gitee_token,save_json

class VulnerabilityMetrics:
    def __init__(self, repo_url):
        self.repo_url = repo_url

        
    def get_vul_detect_time(self):
        return vul_detect_time(repo_url)
    
    def get_vulnerablity_feedback_channels(self):
        return vulnerablity_feedback_channels(repo_url)
    
    def get_vul_levels_metrics(self):
        return get_vul_levels_metrics(self.repo_url)
    
if __name__ == "__main__":
    repo_url ='https://github.com/numpy/numpy'
    metrics = VulnerabilityMetrics(repo_url)
    # print(metrics.get_vul_detect_time())
    # save_json(metrics.get_vul_detect_time(), 'vul_detect_time.json')
    save_json(metrics.get_vulnerablity_feedback_channels(), 'vulnerablity_feedback_channels.json')
    # print(metrics.get_vulnerablity_feedback_channels())