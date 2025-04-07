'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2025-02-17 09:30:38
LastEditors: zyx
LastEditTime: 2025-03-24 10:29:58
'''
import re
import os
from compass_metrics.document_metric.utils import TMP_PATH,JSON_REPO_PATH,clone_repo
from compass_metrics.document_metric.utils import save_json,load_json

REPO_PATH = TMP_PATH

class DocQuarty:
    def __init__(self, file_path):
        self.file_path = file_path
        self.content = self.read_file_content()
        self.words = self.count_words_in_markdown()
        self.pic_number = self.count_pic_number()
    
    def read_file_content(self):
        with open(self.file_path, 'r', encoding='utf-8',errors="ignore") as file:
            content = file.read()
        return content

    def remove_markdown_format(self,text):
        '''Remove markdown syntax from the text'''
        # 去除标题（# 标题）
        text = re.sub(r'^(#{1,6}\s*)', '', text, flags=re.MULTILINE)
        # 去除加粗 (**粗体** 或 __粗体__)
        text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)
        # 去除斜体 (*) 或 _ (*斜体* 或 _斜体_)
        text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)
        # 去除链接 ([链接文本](链接地址))
        text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1', text)
        # 去除图片 (![图片alt](图片地址))
        text = re.sub(r'!\[(.*?)\]\((.*?)\)', '', text)
        # 去除列表标记 (- 列表项 或 * 列表项)
        text = re.sub(r'^(\s*(?:-|\*)\s+)', '', text, flags=re.MULTILINE)
        # 去除引用标记 (> 引用)
        text = re.sub(r'^(\s*> \s*)', '', text, flags=re.MULTILINE)
        # 去除代码块 (``` 代码块 ```)
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        # 去除行内代码 (`代码`)
        text = re.sub(r'`(.*?)`', r'\1', text)
        # 去除多余的空行
        text = re.sub(r'\n{2,}', '\n', text)
        return text.strip()

    def count_words_in_markdown(self):
        '''Count the number of words in the markdown content'''
        # Remove markdown syntax using regex
        content = self.remove_markdown_format(self.content)    
        # Split the content into words
        words = re.findall(r'\b\w+\b', content)
        
        return len(words)
    
    def count_pic_number(self):
        '''Count the number of code blocks, images, videos, audios, and external links in the content'''

        code_blocks = len(re.findall(r'```.*?```', self.content, flags=re.DOTALL))
        images = len(re.findall(r'!\[.*?\]\(.*?\)', self.content))
        videos = len(re.findall(r'\[.*?\]\(.*?\.(mp4|webm|ogg)\)', self.content))
        audios = len(re.findall(r'\[.*?\]\(.*?\.(mp3|wav|ogg)\)', self.content))
        external_links = len(re.findall(r'\[.*?\]\(http.*?\)', self.content))
        
        return {
            'code_blocks': code_blocks,
            'images': images,
            'videos': videos,
            'audios': audios,
            'external_links': external_links
        }


def find_doc_quarty_files(json_path):
    
    ans = {"doc_quarty":0, "doc_quarty_details":[]}
    doc_details = load_json(json_path)["folder_document_details"]
    for doc_detail in doc_details:
        file_path = os.path.join(REPO_PATH,doc_detail["path"])
        doc_quarty = DocQuarty(file_path)
        res = {
            'name': doc_detail["name"],
            'path': doc_detail["path"],
            'Word_count': doc_quarty.words,
            'Picture_count': doc_quarty.pic_number
        }
        ans["doc_quarty_details"].append(res)
        ans["doc_quarty"] += 1

    return ans



def doc_quarty_all(url):
    '''document quarty'''
    repo_name = os.path.basename(url)
    
    if repo_name not in os.listdir(REPO_PATH):
        print(f"Cloning {repo_name} repository...")
        clone_repo(url)
        
    json_path = os.path.join(JSON_REPO_PATH, f"{repo_name}.json")

    if f"{repo_name}.json" not in os.listdir(JSON_REPO_PATH):
        return ValueError(f"Start by performing the document quantity metric...")

    zh_files = find_doc_quarty_files(json_path)
    return zh_files
    
if __name__ == '__main__':
    # file_path = r'C:\Users\zyx\Desktop\文档数量\tmp\numpy\README.md'
    # file_path = r'tmp\pytorch\README.md'
    # file_path = r'C:\Users\zyx\Desktop\文档数量\tmp\numpy\CONTRIBUTING.rst'
    # doc_quarty = DocQuarty(file_path)
    # # print(f"Word count: {doc_quarty.words}")
    # # print(f"Picture count: {doc_quarty.pic_number}")
    # ans = {
    #     'Word count': doc_quarty.words,
    #     'Picture count': doc_quarty.pic_number
    # }
    url = "https://github.com/numpy/numpy"
    ans = doc_quarty_all(url)
    save_json(ans, f'文档数量质量支持.json')

