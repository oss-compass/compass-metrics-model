'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2025-03-04 10:23:24
LastEditors: zyx
LastEditTime: 2025-03-04 11:22:47
'''
from doc_quarty import doc_quarty_all
from doc_chinese_support import doc_chinexe_support_git
from doc_num import get_documentation_links_from_repo
# from organizational_contribution import organizational_contribution


class Industry_Support:
    '''get the documentation quality, documentation number, Chinese documentation files, and organizational contribution of a repository'''

    def __init__(self,repo_url):
        self.repo_url = repo_url
        self.doc_number = get_documentation_links_from_repo(repo_url)
        self.doc_quarty = doc_quarty_all(repo_url)
        self.zh_files = doc_chinexe_support_git(repo_url)
    
    def get_doc_quarty(self):
        return self.doc_quarty
    
    def get_doc_number(self):
        return self.doc_number
    
    def get_zh_files(self):
        return self.zh_files
    
    # def get_org_contribution(self):
    #     return organizational_contribution(self.repo_url)
    
if __name__ == '__main__':
    dm = Industry_Support('https://github.com/numpy/numpy')
    print(dm.get_doc_quarty())
    print(dm.get_doc_number())
    print(dm.get_zh_files())