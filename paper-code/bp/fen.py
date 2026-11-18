def read_matrices_from_file(filename):
    """从文件读取多个矩阵"""
    matrices = []
    with open(filename, 'r', encoding='utf-8') as file:
        total_matrices = int(file.readline().strip())  # 读取矩阵总数
        
        for _ in range(total_matrices):
            # 读取矩阵尺寸
            dimensions = file.readline().strip().split()
            if not dimensions:
                continue
            rows, cols = int(dimensions[0]), int(dimensions[1])
            
            # 读取矩阵数据
            matrix = []
            for i in range(rows):
                line = file.readline().strip()
                if line:
                    row = [int(x) for x in line.split()]
                    matrix.append(row)
            
            matrices.append(matrix)
    
    return matrices

def split_matrix_by_columns(matrix, num_blocks=2):
    """将矩阵尽可能均匀地分成指定数量的列块"""
    total_cols = len(matrix[0])
    sub_matrices = []
    
    # 计算每个块的大小
    base_size = total_cols // num_blocks
    remainder = total_cols % num_blocks
    
    split_points = []
    current_point = 0
    
    # 计算分割点
    for i in range(num_blocks):
        block_size = base_size + (1 if i < remainder else 0)
        current_point += block_size
        if i < num_blocks - 1:  # 最后一个分割点不需要添加
            split_points.append(current_point)
    
    # 根据分割点分割矩阵
    prev = 0
    for point in split_points:
        sub_matrix = [row[prev:point] for row in matrix]
        sub_matrices.append(sub_matrix)
        prev = point
    
    # 添加最后一个块
    if prev < total_cols:
        sub_matrix = [row[prev:] for row in matrix]
        sub_matrices.append(sub_matrix)
    
    return sub_matrices

def write_matrix_to_file(matrix, file):
    """将矩阵写入文件"""
    # 写入矩阵的行数和列数
    file.write(f"{len(matrix)} {len(matrix[0]) if matrix else 0}\n")
    # 写入矩阵内容
    for row in matrix:
        file.write(' '.join(map(str, row)) + '\n')

def main():
    input_filename = 'example_matrix.txt'  # 输入文件
    output_filename = 'example.txt'  # 输出文件
    num_blocks = 4  # split into 4 column blocks
    
    # 读取所有矩阵
    print("正在读取矩阵文件...")
    matrices = read_matrices_from_file(input_filename)
    print(f"成功读取 {len(matrices)} 个矩阵")
    
    # 对每个矩阵进行分块
    all_blocks = []
    block_info = []  # 记录每个原始矩阵分成了多少块
    
    print("开始分块处理...")
    for i, matrix in enumerate(matrices):
        rows = len(matrix)
        cols = len(matrix[0])
        print(f"处理矩阵 {i+1}/{len(matrices)}: {rows}×{cols}")
        
        # 分块
        sub_matrices = split_matrix_by_columns(matrix, num_blocks)
        all_blocks.extend(sub_matrices)
        block_info.append((rows, cols, len(sub_matrices)))
        
        # 打印分块信息
        block_sizes = [f"{len(sub[0])}×{len(sub)}" for sub in sub_matrices]
        print(f"  分成 {len(sub_matrices)} 块: {', '.join(block_sizes)}")
    
    # 写入输出文件
    print(f"写入结果到 {output_filename}...")
    with open(output_filename, 'w', encoding='utf-8') as f:
        # 第一行写入分块后的总矩阵个数
        f.write(f"{len(all_blocks)}\n")
        
        # 依次写入每个子矩阵
        for i, sub_matrix in enumerate(all_blocks, 1):
            write_matrix_to_file(sub_matrix, f)
    
    # 打印统计信息
    print(f"\n=== 分块完成 ===")
    print(f"原始矩阵数量: {len(matrices)}")
    print(f"分块后矩阵数量: {len(all_blocks)}")
    print(f"分块比例: {num_blocks}:1")
    
    print("\n各矩阵分块情况:")
    for i, (rows, cols, num_blocks_created) in enumerate(block_info):
        print(f"矩阵 {i+1} ({rows}×{cols}): 分成 {num_blocks_created} 块")

if __name__ == "__main__":
    main()