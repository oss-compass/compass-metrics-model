'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2025-03-04 10:23:24
LastEditors: zyx
LastEditTime: 2025-03-18 17:54:08
'''
from doc_quarty import doc_quarty_all
from doc_chinese_support import doc_chinexe_support_git
from doc_num import get_documentation_links_from_repo
from organizational_contribution import organizational_contribution


class Industry_Support:
    '''get the documentation quality, documentation number, Chinese documentation files, and organizational contribution of a repository'''

    def __init__(self,client,repo_list):
        self.repo_list = repo_list
        self.client = client
        self.doc_number = {}
        self.doc_quarty = {}
        self.zh_files = {}
        for repo_url in self.repo_list:
            self.doc_number[repo_url] = get_documentation_links_from_repo(repo_url)
            
            # self.zh_files[repo_url] = doc_chinexe_support_git(repo_url)
    
    def get_doc_quarty(self):
        for repo_url in self.repo_list:
            self.doc_quarty[repo_url] = doc_quarty_all(repo_url)
        get_doc_quarty = self.doc_quarty
        return get_doc_quarty

    
    def get_doc_number(self):
        get_doc_number = self.doc_number
        return get_doc_number

    
    def get_zh_files(self):
        for repo_url in self.repo_list:
            self.zh_files[repo_url] = doc_chinexe_support_git(repo_url)
        get_zh_files = self.zh_files
        return get_zh_files

    
    def get_org_contribution(self):
        get_org_contribution = {}
        for repo_url in self.repo_list:
            get_org_contribution[repo_url] = organizational_contribution(self.client,repo_url)
        return get_org_contribution
    
if __name__ == '__main__':
    a = ['https://github.com/numpy/numpy']
    dm = Industry_Support(123,a)
    print(dm.get_doc_quarty())
    print(dm.get_doc_number())
    print(dm.get_zh_files())