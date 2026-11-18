import numpy as np

def process_matrix(matrix):
    """处理矩阵：删除全0行和重复行，返回处理后的矩阵和新的行数"""
    n, m = matrix.shape
    
    # 删除全零行
    non_zero_rows = [i for i, row in enumerate(matrix) if not all(x == 0 for x in row)]
    matrix = matrix[non_zero_rows]
    
    # 删除重复行（保留第一次出现的行）
    unique_rows = []
    seen = set()
    
    for i, row in enumerate(matrix):
        row_tuple = tuple(row)
        if row_tuple not in seen:
            seen.add(row_tuple)
            unique_rows.append(row)
    
    if len(unique_rows) > 0:
        processed_matrix = np.array(unique_rows, dtype=int)
    else:
        processed_matrix = np.array([], dtype=int).reshape(0, m)
    
    return processed_matrix, processed_matrix.shape[0]

def read_and_process_matrices(filename):
    """从文件读取矩阵，处理并覆写原文件"""
    with open(filename, 'r') as file:
        num_matrices = int(file.readline().strip())  # 读取矩阵个数
        matrices_info = []
        
        for matrix_idx in range(1, num_matrices + 1):
            # 读取矩阵的行数n和列数m
            n, m = map(int, file.readline().strip().split(" "))
            
            # 读取矩阵数据
            matrix = []
            for _ in range(n):
                row = list(map(int, file.readline().strip().split(" ")))
                matrix.append(row)
            
            matrix = np.array(matrix, dtype=int)  # 转为NumPy数组
            matrices_info.append((n, m, matrix))
    
    # 处理所有矩阵
    processed_matrices = []
    for n, m, matrix in matrices_info:
        processed_matrix, new_n = process_matrix(matrix)
        processed_matrices.append((new_n, m, processed_matrix))
    
    # 覆写原文件
    with open(filename, 'w') as file:
        file.write(f"{num_matrices}\n")
        for new_n, m, matrix in processed_matrices:
            file.write(f"{new_n} {m}\n")
            for row in matrix:
                file.write(" ".join(map(str, row)) + "\n")

# 示例文件路径
filename = "example.txt"
read_and_process_matrices(filename)