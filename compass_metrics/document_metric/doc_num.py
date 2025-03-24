'''
Descripttion: get file number from a folder and a README file
version: V1.0
Author: zyx
Date: 2025-01-16 17:31:20
LastEditors: zyx
LastEditTime: 2025-03-20 16:42:50
'''
import os
from utils import save_json,clone_repo,TMP_PATH,JSON_BASEPATH
import re

def count_documents_from_folder(path, extensions=None)->tuple:
    """
    Count documents in a folder with specified extensions and return their details.
    Args:
        path (str): The path to the folder to search for documents.
        extensions (list, optional): A list of file extensions to include in the count. 
                                        Defaults to [".md", ".yaml", ".pdf", ".yml", ".html", ".doc", ".docx", ".txt", ".rst"].
    Returns:
        tuple: A tuple containing:
            - document_count (int): The number of documents found.
            - document_details (list): A list of dictionaries, each containing:
                - "name" (str): The name of the document.
                - "path" (str): The full path to the document.
    """

    if extensions is None:
        extensions = [".md", ".yaml", ".pdf", ".yml", ".html", ".doc", ".docx",".txt",".rst"]
    
    document_count = 0
    document_details = []

    for root, dirs, files in os.walk(path):
        for file in files:
            if "requirements" in file:
                continue
            if any(file.endswith(ext) for ext in extensions):
                document_count += 1
                document_details.append({
                    "name": file,
                    "path": os.path.join(root, file).replace(TMP_PATH, "")[1:].replace("\\", "/")
                })
    return document_count, document_details

def count_documents_from_Readme(markdown)->tuple:
    """
    Counts the number of document links in a given markdown string, excluding video and image links.

    Args:
        markdown (str): The markdown content to be analyzed.

    Returns:
        tuple: A tuple containing:
            - link_count (int): The number of document links found.
            - links (list): A list of dictionaries, each containing:
                - "name" (str): The name of the link (URL without the protocol).
                - "path" (str): The full URL of the link.
    """

    link_count = 0
    links = []
    video_sites = ["youtube.com", "vimeo.com", "dailymotion.com","blibli.com","img","gif","jpg","jpeg","png","svg"]
    markdown_split = markdown.split('\n')
    for line in markdown_split:
        # Check for links in <a> tags
        if "<a href" in line:
            link = line.split('href="')[1].split('"')[0].replace(")", "")
            if not any(video_site in link for video_site in video_sites):
                link_count += 1
                links.append(
                    {
                    "name": link.replace("http://", "").replace("https://", ""),
                    "path" : link
                    }
                    )
        # Check for plain text links
        else:
            urls = re.findall(r'(https?://\S+)', line)
            for url in urls:
                url = url.split(')')[0]
                if not any(video_site in url for video_site in video_sites):
                    link_count += 1
                    links.append({
                    "name": url.replace("http://", "").replace("https://", ""),
                    "path" : url
                    })
    return link_count, links

def search_readme_in_folder(path)->tuple:
    """
    Searches for README files in the specified folder and returns their contents.
    Args:
        path (str): The path to the folder where the search will be conducted.
    Returns:
        tuple: A tuple containing a boolean flag and the contents of the README file.
               flag :The boolean flag is True if a README file is found, otherwise False.
               readme_content: The contents of the README file are returned as a string if found, otherwise an empty list.
    """

    readme_files = ["README.md", "README.txt", "README.rst","README","readme.md", "readme.txt", "readme.rst","readme"]
    readme_contents = ""
    flag = False

    for files in os.listdir(path):
        if not os.path.isfile(files):
            continue
        

        if files in readme_files:
            flag = True # README file found
            with open(os.path.join(path, files), 'r', encoding='utf-8') as f:
                readme_contents=f.read()
                break
    
    return flag,readme_contents

def get_documentation_links_from_repo(repo_url, platform='github'):
    """
    Clones a repository, searches for README files, counts documents, and saves the details to a JSON file.
    Args:
        repo_url (str): The URL of the repository to clone.
        platform (str, optional): The platform where the repository is hosted. Defaults to 'github'.
    Returns:
        dict: A dictionary containing the total number of documents, details of documents found in the folder, 
              and details of links found in the README file.
    Raises:
        ValueError: If the repository clone fails or if the README file is not found in the folder.
    """

    if os.path.basename(repo_url) not in os.listdir(TMP_PATH):
        flag,readme_path = clone_repo(repo_url)
        if not flag:
            ValueError("Repository clone failed.")
        else:
            print(f"Repository cloned to {readme_path}")

    
    readme_path = os.path.join(TMP_PATH, os.path.basename(repo_url))
    if readme_path:
        print(f"Repository has already cloned to {readme_path}")
        flag,readme = search_readme_in_folder(readme_path)
    else:
        ValueError("README file not found in folder.")
    

    document_count, document_details = count_documents_from_folder(readme_path)
    link_count, links = count_documents_from_Readme(readme)

    doc_number = {
        "get_doc_number": document_count+link_count,
        "folder_document_details": document_details,
        "links_document_details": links
    }

    save_json(doc_number,os.path.join(JSON_BASEPATH,f'{os.path.basename(repo_url)}.json'))
    return doc_number


if __name__ == '__main__':
    # path = r"C:\Users\zyx\Desktop\code_20\tmp\numpy"
    # total_docs, docs_info = count_documents_from_folder(path)
    # print(f"Total documents: {total_docs}")
    # for doc in docs_info:
    #     print(f"Document: {doc['name']}, Path: {doc['path']}")
    # save_json(docs_info, 'docs_info.json')
    # print(count_documents_from_Readme(search_readme_in_folder(r"C:\Users\zyx\Desktop\code_20\tmp\numpy")))
    # print(search_readme_in_folder(r"C:\Users\zyx\Desktop\code_20\tmp\numpy"))
    # print(get_documentation_links_from_repo('https://github.com/pytorch/pytorch'))
    # print(get_documentation_links_from_repo('https://gitee.com/mirrors/opencv'))
    print(get_documentation_links_from_repo('https://github.com/numpy/numpy'))
    # print(get_documentation_links_from_repo('https://github.com/git-lfs/git-lfs'))