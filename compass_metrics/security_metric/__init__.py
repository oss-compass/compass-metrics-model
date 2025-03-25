'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2025-03-04 11:16:48
LastEditors: zyx
LastEditTime: 2025-03-25 11:16:39
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

        ans = {
            "vul_detect_time": 0,
            "vul_detect_time_details": []
        }

        for key,avg_time in get_vul_detect_time.items():
            ans["vul_detect_time"] += avg_time.days / len(self.repo_list)

            ans.append(
                {
                    "repo_url": key,
                    "vul_detect_time_details": avg_time.days
                }
            )
            # if ans["vul_detect_time_details"].get(key) is None:
            #     ans["vul_detect_time_details"][key] = {}
            # ans["vul_detect_time_details"][key]["vul_detect_time"] = avg_time.days

        return ans #{"get_vul_detect_time": avg_time.days}

    
    def get_vulnerablity_feedback_channels(self):
        for repo_url in self.repo_list:
            self.vulnerablity_feedback_channels[repo_url] = vulnerablity_feedback_channels(repo_url)
        get_vulnerablity_feedback_channels = self.vulnerablity_feedback_channels
        ans = {
            "vulnerablity_feedback_channels": 0,
            "vulnerablity_feedback_channels_details": []
        }

        for key,feedback in get_vulnerablity_feedback_channels.items():
            ans["vulnerablity_feedback_channels"] += feedback["vulnerablity_feedback_channels"] / len(self.repo_list)

            ans["vulnerablity_feedback_channels_details"].append(
                {
                    "repo_url": key,
                    "vulnerablity_feedback_channels_details": feedback
                }
            )
            # if ans["vulnerablity_feedback_channels_details"].get(key) is None:
            #     ans["vulnerablity_feedback_channels_details"][key] = {}
            # ans["vulnerablity_feedback_channels_details"][key]["vulnerablity_feedback_channels"] = feedback["vulnerablity_feedback_channels"]
            # ans["vulnerablity_feedback_channels_details"][key]["vulnerablity_feedback_channels_details"] = feedback["vulnerablity_feedback_channels_details"]
            
        return ans #{"get_vulnerablity_feedback_channels":0, "vulnerablity_feedback_channels_details":[]}

    
    def get_vul_levels(self,client):
        for repo_url in self.repo_list:
            self.vul_levels_metrics[repo_url] = get_vul_levels_metrics(repo_url,client)
        get_vul_levels = self.vul_levels_metrics

        ans = {
            "vul_levels": 0,
            "vul_level_details": []
        }

        for key,vul_level in get_vul_levels.items():
            ans["vul_levels"] += vul_level["vul_levels"] / len(self.repo_list)
            ans["vul_level_details"].append(
                {
                    "repo_url": key,
                    "vul_level_details": vul_level
                }
            ) 
            # if ans["vul_level_details"].get(key) is None:
            #     ans["vul_level_details"][key] = {}
            # ans["vul_level_details"][key]["vul_levels"] = vul_level["vul_levels"]
            # ans["vul_level_details"][key]["vul_level_details"] = vul_level["vul_level_details"]
        return ans #{"get_vul_levels":0,"vul_levels":{"high": 0, "medium": 0, "low": 0},"vul_level_details":[]}

    
if __name__ == "__main__":
    repo_url =['https://github.com/numpy/numpy']
    metrics = VulnerabilityMetrics(x for x in repo_url).get_vul_levels("123")
    # print(metrics.get_vul_detect_time())
    # save_json(metrics.get_vul_detect_time(), 'vul_detect_time.json')
    # save_json(metrics.get_vulnerablity_feedback_channels(), 'vulnerablity_feedback_channels.json')
    # print(metrics.get_vulnerablity_feedback_channels())