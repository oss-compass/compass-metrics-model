'''
Descripttion: 
version: 
Author: zyx
Date: 2024-08-12 17:04:31
LastEditors: zyx
LastEditTime: 2024-08-12 17:04:39
'''
import matplotlib.pyplot as plt
import numpy as np

# 定义公式的变量
issue_num_max = 100  # 假设存在最多issue的版本数量
issue_num_min = 20   # 假设存在最少issue的版本数量
avg_issue_num = 60   # 假设所有版本的平均issue数量

# 计算公式值
formula_value = (issue_num_max - issue_num_min) / avg_issue_num

# 绘制公式的图形表示
fig, ax = plt.subplots()

# X轴表示公式的各部分
parts = ['Max Issue', 'Min Issue', 'Average Issue']
values = [issue_num_max, issue_num_min, avg_issue_num]

ax.bar(parts, values, color=['blue', 'orange', 'green'])

# 添加公式计算的结果
ax.text(1.5, max(values) - 10, f'Formula Value: {formula_value:.2f}', fontsize=12, color='red')

ax.set_ylabel('Issue Numbers')
ax.set_title('Formula Representation')

plt.show()
