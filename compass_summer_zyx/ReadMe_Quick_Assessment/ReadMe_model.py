'''
Descripttion: ReadmeFetcher,解析基本数据，并且爬取Readme最后评分。
version: V1.0
Author: zyx
Date: 2024-09-20 10:29:00
LastEditors: zyx
LastEditTime: 2024-09-29 09:01:12
'''
import requests
import re
import os
from prompt import prompt_case
import utils
SAVE_PATH = r"README"
if not os.path.exists(SAVE_PATH):
    os.mkdir(SAVE_PATH)


class ReadmeFetcher:

    def __init__(self, url):
        """
        初始化ReadmeFetcher对象，通过URL提取仓库所有者和仓库名。

        :param url: 仓库的完整URL (GitHub或Gitee)
        """
        self.url = url
        self.platform = self._detect_platform()

        # 根据平台和URL提取 owner 和 repo
        self.owner, self.repo = self._parse_url()

        if self.platform == 'github':
            self.api_url = f'https://api.github.com/repos/{self.owner}/{self.repo}/readme'
        elif self.platform == 'gitee':
            self.api_url = f'https://gitee.com/api/v5/repos/{self.owner}/{self.repo}/readme'
        else:
            raise ValueError("目前仅支持GitHub或Gitee平台的URL。")

    def _detect_platform(self):
        """
        检测平台是 GitHub 还是 Gitee。
        
        :return: 'github' 或 'gitee'
        """
        if 'github.com' in self.url:
            return 'github'
        elif 'gitee.com' in self.url:
            return 'gitee'
        else:
            raise ValueError("无法识别的URL平台，目前仅支持GitHub和Gitee。")

    def _parse_url(self):
        """
        从URL中提取owner和repo。
        
        :return: (owner, repo)
        """
        if self.platform == 'github':
            pattern = r"github\.com/([^/]+)/([^/]+)"
        elif self.platform == 'gitee':
            pattern = r"gitee\.com/([^/]+)/([^/]+)"
        
        match = re.search(pattern, self.url)
        if match:
            return match.group(1), match.group(2)
        else:
            raise ValueError("无法从URL中解析出仓库所有者和仓库名。")

    def get_readme(self):
        """
        获取仓库的README文件内容（以Markdown格式返回）。

        :return: README文件内容（字符串），如果仓库不存在或获取失败，则返回错误信息。
        """
        headers = {
            'Accept': 'application/vnd.github.v3.raw+json' if self.platform == 'github' else 'application/json'
        }
        
        try:
            response = requests.get(self.api_url, headers=headers)
            response.raise_for_status()  # 检查请求是否成功

            if self.platform == 'github':
                return response.text
            elif self.platform == 'gitee':
                readme_data = response.json()
                if 'content' in readme_data:
                    return readme_data['content']
                else:
                    return '未找到README文件。'
        
        except requests.exceptions.RequestException as e:
            return f'获取README失败: {str(e)}'
        
    def send_evaluate_readme_completeness(self):
        '''
        completeness评估接口
        '''
        url = 'http://127.0.0.1:5000/evaluate_readme_completeness'
        data = {"readme_documents":{self.repo:"If this indicator is not available, it is scored on a scale of 0-40，Readme is as follows: "+self.get_readme()+" Could you please rate it,Please give a detailed score for each indicator?"}}
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            content = response.json().get('evaluation_results')
            print("Evaluation Results:", content)
            utils.save_markdown(content[0],os.path.join(SAVE_PATH,self.repo+"_completeness.md"))
        else:
            print("Error:", response.json())


    def send_evaluate_readme_definition(self):
        '''
        completeness评估接口
        '''
        url = 'http://127.0.0.1:5000/evaluate_readme_definition'
        data = {"readme_documents":{self.repo:prompt_case("definition3")+"Readme is as follows: "+self.get_readme()+" Could you please rate it,Please give a detailed score for each indicator?"}}
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            content = response.json().get('evaluation_results')
            content1 = content[0][:content.find("Human: ")] + f"\n Flesch Reading Ease Score: {self.calculate_flesch_reading_ease(self.get_readme())}"
            print("Evaluation Results:", content1)
            utils.save_markdown(content1,os.path.join(SAVE_PATH,self.repo+"_definition.md"))
        else:
            print("Error:", response.json())

    def calculate_flesch_reading_ease(text):
        # 计算 Flesch Reading Ease Score
        fres_score = textstat.flesch_reading_ease(text)+50
        return fres_score


if __name__ == "__main__":
    url = 'https://github.com/CodeSpace-Academy/SDF_Portfolio_Piece_StudentNo_Classcode_Group_Name-Surname_SDF11'
    fetcher = ReadmeFetcher(url)
    fetcher.send_evaluate_readme_completeness()
    fetcher.send_evaluate_readme_definition()
