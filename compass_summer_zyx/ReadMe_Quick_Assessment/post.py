'''
Descripttion: 测试代码
version: V1.0
Author: zyx
Date: 2024-09-21 11:14:12
LastEditors: zyx
LastEditTime: 2024-09-23 07:38:37
'''
import requests
from prompt import prompt_case
# 发送请求生成文本
def send_generate_request():
    url = 'http://127.0.0.1:5000/generate'
    data = {"input_text": "你给我计算326562-56456151*859641231"}
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        print("Generated Text:", response.json().get('generated_text'))
    else:
        print("Error:", response.json())

# 发送请求评估README文档
def send_evaluate_readme_request():
    url = 'http://127.0.0.1:5000/evaluate_readme_definition'
    data = {"readme_documents": [prompt_case("definition3"),"# Sample README\nThis is a sample README for testing."]}
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        print("Evaluation Results:", response.json().get('evaluation_results'))
    else:
        print("Error:", response.json())

        
def send_evaluate_readme_request():
    url = 'http://127.0.0.1:5000/evaluate_readme_definition'
    data = {"readme_documents": [prompt_case("definition3"),"# Sample README\nThis is a sample README for testing."]}
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        print("Evaluation Results:", response.json().get('evaluation_results'))
    else:
        print("Error:", response.json())
# 调用函数
if __name__=="__main__":
    send_evaluate_readme_request()
