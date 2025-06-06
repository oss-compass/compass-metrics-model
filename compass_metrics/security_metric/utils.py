'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2025-01-16 17:34:10
LastEditors: zyx
LastEditTime: 2025-03-24 17:18:09
'''
import json
import os
import sys
import requests
import tqdm
import markdown
# from compass_metrics.resources.config.ini import GITEE_TOKEN, GITHUB_TOKEN
DATA_PATH = r"/data"
NOW_PATH =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_PATH = os.path.join(DATA_PATH,'repos_tmp')
JSON_REPOPATH = os.path.join(DATA_PATH,'json')

import configparser

config = configparser.ConfigParser()
config.read(os.path.join(NOW_PATH,r'resources/config.ini'))
# 获取 GITEE_TOKEN 和 GITHUB_TOKEN
GITEE_TOKEN = config.get('OPEN_CHECKService', 'GITEE_TOKEN')
GITHUB_TOKEN = config.get('OPEN_CHECKService', 'GITHUB_TOKEN')


if not os.path.exists(TMP_PATH):
    os.makedirs(TMP_PATH)


def get_github_readme(repo):
    url = f'https://api.github.com/repos/{repo}/readme'
    headers = {'Authorization': f'token {get_github_token()}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return markdown.markdown(response.json()['content'])
    
    else:
        response.raise_for_status()

def get_gitee_readme(repo):
    url = f'https://gitee.com/api/v5/repos/{repo}/readme'
    headers = {'Authorization': f'token {get_gitee_token()}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['content']
    else:
        response.raise_for_status()

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)
        return True

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)
    
def get_github_token():
    return os.getenv('GITHUB_TOKEN', GITHUB_TOKEN)

def get_gitee_token():
    return  os.getenv('GITEE_TOKEN', GITEE_TOKEN)

def clone_repo(repo_url,version):
    """
    Clone a repository from GitHub or Gitee.
    Args:
        repo_url (str): The URL of the repository to clone.
    Returns:
        tuple: A tuple containing a boolean and a string. The boolean indicates 
               whether the cloning was successful, and the string is the path 
               to the cloned repository if successful, otherwise None.
    Raises:
        ValueError: If the platform is not 'github' or 'gitee'.
    """
    repo_url = repo_url.replace('https://', '')
    platform = check_github_gitee(repo_url)
    
    if platform == 'github':
        token = get_github_token()
    elif platform == 'gitee':
        token = get_gitee_token()
    else:
        raise ValueError("Unsupported platform. Use 'github' or 'gitee'.")

    repo_name = repo_url.split('/')[-1]
    clone_path = os.path.join(TMP_PATH, repo_name)
    new_clone_path = os.path.join(TMP_PATH, repo_name + "-"+version)

    clone_command = f'git clone --branch {version} https://{token}@{repo_url} {clone_path}'


    result = os.system(clone_command)

    if result == 0:
        if os.path.exists(clone_path):
            os.rename(clone_path, new_clone_path)
        return True,new_clone_path
    else:
        return False, None
    
def check_github_gitee(url):
    if 'github.com' in url:
        return 'github'
    elif 'gitee.com' in url:
        return 'gitee'
    else:
        return None
    
if __name__ == '__main__':
    # print(get_github_readme('python/cpython'))
    # print(get_gitee_readme('python/cpython'))
    # save_json(get_github_readme('python/cpython'), 'github_readme.json')
    # save_json(get_gitee_readme('python/cpython'), 'gitee_readme.json')
    # print(load_json('github_readme.json'))
    # print(load_json('gitee_readme.json'))
    # print(get_all_github_files('python/cpython'))
    # print(clone_repo('https://github.com/numpy/numpy'))
    print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))