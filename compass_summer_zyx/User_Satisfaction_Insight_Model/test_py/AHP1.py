'''
Descripttion: 
version: 
Author: zyx
Date: 2024-08-12 11:17:25
LastEditors: zyx
LastEditTime: 2024-09-27 11:44:41
'''
import numpy as np

# 定义判断矩阵
'''matrix = np.array([
    [1, 1, 5, 7, 4],
    [1, 1, 5, 7, 4],
    [0.2, 0.2, 1, 3, 0.5],
    [0.142857143, 0.142857143, 0.333333333, 1, 0.25],
    [0.25, 0.25, 2, 4, 1]
])'''

matrix = np.array([
       [1, 3, 5, 2, 4],
    [1/3, 1, 3, 1, 2],
    [1/5, 1/3, 1, 1/4, 1/2],
    [1/2, 1, 4, 1, 3],
    [1/4, 1/2, 2, 1/3, 1]
])
# 计算列和
column_sum = matrix.sum(axis=0)

# 归一化矩阵
normalized_matrix = matrix / column_sum

# 计算权重向量（每行的平均值）
weights = normalized_matrix.mean(axis=1)

# 计算 λ_max
lambda_max = np.dot(column_sum, weights)

# 一致性指标 CI
n = matrix.shape[0]
CI = (lambda_max - n) / (n - 1)

# 查找 RI（从已知层次分析法表格中查找，5阶矩阵的 RI 值为 1.12）
RI = 1.12

# 计算一致性比率 CR
CR = CI / RI

print(weights, CI, RI, CR)
