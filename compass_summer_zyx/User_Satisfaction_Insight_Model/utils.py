'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2024-09-18 12:43:48
LastEditors: zyx
LastEditTime: 2024-09-23 11:25:39
'''
import json
import re


def read_json_file(file_path):
    '''
    file_path:读取文件的路径
    '''

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print("文件未找到，请检查文件路径是否正确。")
    except json.JSONDecodeError:
        print("JSON文件解析错误，请确保文件内容为有效的JSON格式。")


def write_json(data, filename):
    '''
    data:数据
    filename:路径
    '''
    
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"JSON数据成功写入到文件 {filename} 中。")
    except Exception as e:
        print(f"写入JSON数据时出现错误：{e}")