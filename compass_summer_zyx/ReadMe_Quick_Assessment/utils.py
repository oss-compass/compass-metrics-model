'''
Descripttion: read_md_file,save_markdown
version: V1.0
Author: zyx
Date: 2024-09-22 08:02:55
LastEditors: zyx
LastEditTime: 2024-09-24 08:56:23
'''
import json
import os
from langdetect import detect
def read_md_file(file_path):
    """
    打开并读取一个 Markdown 文件 (.md)。
    :param file_path: .md 文件的路径
    :return: 文件内容的字符串
    """
    try:
        # 以读取模式 ('r') 打开文件，并指定编码为 utf-8
        with open(file_path, 'r', encoding='utf-8') as file:
            # 读取文件内容并返回
            content = file.read()
            return content
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"
    
def save_markdown(content, file_path):
    """
    将Markdown内容保存到指定文件中

    :param content: Markdown格式的文本内容s
    :param file_path: 保存文件的路径（包括文件名）
    """
    try:
        # 以写入模式打开文件，指定UTF-8编码
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Markdown successfully saved to {file_path}")
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")



def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def detect_language(text):
    try:
        language = detect(text)
        return language
    except:
        raise ValueError("语言检测失败")

if __name__=="__main__":
    # 示例文本
    text = "English"
    language = detect_language(text)
    print(f"给定文本的语言是: {language}")