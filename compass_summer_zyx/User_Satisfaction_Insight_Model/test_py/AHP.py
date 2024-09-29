'''
Descripttion: 
version: 
Author: zyx
Date: 2024-08-12 11:26:20
LastEditors: zyx
LastEditTime: 2024-08-12 11:26:57
'''
import pandas as pd
import numpy as np
# 创建新的判断矩阵，按照指定顺序和重要性范围0-9
priority_matrix_custom = np.array([
    [1,   3,   7,   8,   5],  # star 相对于其他指标的重要性
    [1/3, 1,   6,   7,   4],  # 综合下载量
    [1/7, 1/6, 1,   3,   2],  # bug issue的处理时间
    [1/8, 1/7, 1/3, 1,   0.5],  # 软件普适性指标
    [1/5, 1/4, 0.5, 2,   1]   # 版本更新稳定性
])

# 矩阵按照顺序进行对称处理
for i in range(priority_matrix_custom.shape[0]):
    for j in range(i+1, priority_matrix_custom.shape[1]):
        priority_matrix_custom[j][i] = 1 / priority_matrix_custom[i][j]

# 将矩阵转换为DataFrame，并添加行列标签
priority_matrix_custom_df = pd.DataFrame(
    priority_matrix_custom,
    columns=["star", "综合下载量", "bug issue的处理时间", "软件普适性指标", "版本更新稳定性"],
    index=["star", "综合下载量", "bug issue的处理时间", "软件普适性指标", "版本更新稳定性"]
)

# 保存为Excel文件
file_path_custom = 'custom_priority_matrix.xlsx'
priority_matrix_custom_df.to_excel(file_path_custom)

file_path_custom
