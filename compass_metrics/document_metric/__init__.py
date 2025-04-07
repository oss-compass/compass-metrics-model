'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2025-03-04 18:01:38
LastEditors: zyx
LastEditTime: 2025-03-26 17:04:36
'''
'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2025-03-04 10:23:24
LastEditors: zyx
LastEditTime: 2025-03-20 17:04:55
'''
from compass_metrics.document_metric.doc_quarty import doc_quarty_all
from compass_metrics.document_metric.doc_chinese_support import doc_chinexe_support_git
from compass_metrics.document_metric.doc_num import get_documentation_links_from_repo
from compass_metrics.document_metric.organizational_contribution import organizational_contribution


class Industry_Support:
    '''get the documentation quality, documentation number, Chinese documentation files, and organizational contribution of a repository'''

    def __init__(self,client,repo_list,version):
        self.repo_list = repo_list
        self.version = version
        self.client = client
        self.doc_number = {}
        self.doc_quarty = {}
        self.zh_files = {}
        for repo_url in self.repo_list:
            self.doc_number[repo_url] = get_documentation_links_from_repo(repo_url,version)
            

    
    def get_doc_quarty(self):
        for repo_url in self.repo_list:
            self.doc_quarty[repo_url] = doc_quarty_all(repo_url,self.version)
        get_doc_quarty = self.doc_quarty

        ans = {"doc_quarty":0, "doc_quarty_details":[]}
        for key,doc_quarty in get_doc_quarty.items():
            ans["doc_quarty"] += doc_quarty["doc_quarty"] / len(self.repo_list)
            ans["doc_quarty_details"].append(
                {
                    "repo_url": key,
                    "doc_quarty_details": doc_quarty
                }
            )
            # if ans["doc_quarty_details"].get(key) is None:
            #     ans["doc_quarty_details"][key] = {}
            # ans["doc_quarty_details"][key]["doc_quarty_details"] = doc_quarty["doc_quarty_details"]

        return ans # {"doc_quarty":0, "doc_quarty_details":{}}

    
    def get_doc_number(self):
        get_doc_number = self.doc_number
        ans = {"doc_number":0, "folder_document_details":[]}
        for key,doc_number in get_doc_number.items():
            ans["doc_number"] += doc_number["doc_number"] / len(self.repo_list)
            ans["folder_document_details"].append(
                {
                    "repo_url": key,
                    "folder_document_details": doc_number
                }
            )
            # if ans["folder_document_details"].get(key) is None:
            #     ans["folder_document_details"][key] = {}
            # ans["folder_document_details"][key]["folder_document_details"] = doc_number["folder_document_details"]
            # ans["folder_document_details"][key]["links_document_details"] = doc_number["links_document_details"]
        return ans #{"doc_number": document_count+link_count,"folder_document_details": document_details,"links_document_details": links}

    
    def get_zh_files_number(self):
        for repo_url in self.repo_list:
            self.zh_files[repo_url] = doc_chinexe_support_git(repo_url,self.version)
        get_zh_files_number = self.zh_files

        ans = {"zh_files_number":0, "zh_files_details":[]}
        for key,zh_files in get_zh_files_number.items():
            ans["zh_files_number"] += int(zh_files["zh_files_number"] / len(self.repo_list))

            ans["zh_files_details"].append(
                {
                    "repo_url": key,
                    "zh_files_details": zh_files
                }
            )
            # if ans["zh_files_details"].get(key) is None:
            #     ans["zh_files_details"][key] = {}
            # ans["zh_files_details"][key]["zh_files_details"] = zh_files["zh_files_details"]

        
        return ans #{"zh_files_number":0, "zh_files_details":{repo_url:zh_files_details}}

    
    def get_org_contribution(self):
        
        get_org_contribution = {}
        for repo_url in self.repo_list: 
            get_org_contribution[repo_url] = organizational_contribution(self.client,repo_url,self.version)

        ans = {"org_contribution":0, "org_contribution_details":[]}
        for key,org_contribution in get_org_contribution.items():
            ans["org_contribution"] += org_contribution["org_contribution"] / len(self.repo_list)
            
            ans["org_contribution_details"].append(
                {
                    "repo_url": key,
                    "org_contribution_details": org_contribution
                }
            )
        return ans #{"org_contribution":organization,"personal": persion, "organization": organization}
    
if __name__ == '__main__':
    a = ["https://github.com/git-lfs/git-lfs"]
    dm = Industry_Support(123,a,'v2.7.2')
    # print(dm.get_doc_quarty())
    # print(dm.get_doc_number())
    print(dm.get_zh_files_number())
    # print(dm.get_zh_files())