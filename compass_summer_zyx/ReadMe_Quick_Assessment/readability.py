'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2024-09-23 09:12:00
LastEditors: zyx
LastEditTime: 2024-09-25 01:29:31
'''
import re

def calculate_fres(text):
    # 中文文档的 FRES 计算公式
    chinese_fres = 206.835 - 1.015 * len(re.findall(r'[\u4e00-\u9fff]+', text)) / len(text) - 84.6
    return chinese_fres

def calculate_flesch_reading_ease(text):
    # 英文文档的 Flesch Reading Ease Score 计算公式
    words = re.findall(r'\b\w+\b', text)
    total_words = len(words)
    total_sentences = text.count('.') + text.count('!') + text.count('?')
    total_syllables = sum([len(re.findall(r'[aeiouyAEIOUY]+', word)) for word in words])

    english_fres = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
    return english_fres

# # 示例中文文档
# chinese_text = "这是一个中文文档的示例，用于计算可读性指标。"
# chinese_fres = calculate_fres(chinese_text)
# print(f"中文文档的 FRES 为: {chinese_fres}")

# # 示例英文文档
# english_text = "Hi,who are you"
# english_fres = calculate_flesch_reading_ease(english_text)
# print(f"英文文档的 Flesch Reading Ease Score 为: {english_fres}")

import textstat

import utils

def calculate_flesch_reading_ease(text):
    # 计算 Flesch Reading Ease Score
    fres_score = textstat.flesch_reading_ease(text)+50
    return fres_score


def calculate_flesch_kincaid(text):
    # 计算 Flesch-Kincaid 指数
    fk_score = textstat.flesch_kincaid_grade(text)
    return fk_score

# 示例文本
sample_text = utils.read_md_file("README.md")

# 计算并打印结果
fk_score = calculate_flesch_kincaid(sample_text)
print(f"Flesch-Kincaid Grade Level: {fk_score}")




# 计算并打印结果
fres_score = calculate_flesch_reading_ease(sample_text)
print(f"Flesch Reading Ease Score: {fres_score}")
