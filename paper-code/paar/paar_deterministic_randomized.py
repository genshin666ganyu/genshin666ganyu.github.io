import random
import time
from collections import defaultdict
from multiprocessing import Pool, cpu_count
import os

# 配置参数
INPUT_FILE = "example_matrix.txt"  # input matrix file
RESULTS_FILE = "paar_results.txt"
NUM_TRIALS_PER_MATRIX = 50  # randomized trials per matrix

def read_matrices_from_file(file_path):
    """从文件读取多个矩阵"""
    matrices = []
    with open(file_path, 'r') as file:
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

def paar_optimized(matrix):
    """改进的Paar算法实现"""
    rows = [[i for i, val in enumerate(row) if val] for row in matrix]
    steps = []
    current_var = len(matrix[0])  # 初始变量数
    
    while True:
        # 统计所有配对
        counter = defaultdict(int)
        for vars in rows:
            for i in range(len(vars)):
                for j in range(i+1, len(vars)):
                    a, b = sorted((vars[i], vars[j]))
                    counter[(a, b)] += 1

        if not counter:
            break
            
        # 找出所有最大出现次数的配对
        max_count = max(counter.values())
        candidates = [pair for pair, cnt in counter.items() if cnt == max_count]
        
        # 随机选择一个最优配对
        a, b = random.choice(candidates)
        
        # 记录步骤
        steps.append((current_var, a, b))
        
        # 更新所有行
        new_rows = []
        for vars in rows:
            if a in vars and b in vars:
                new_vars = [v for v in vars if v not in (a, b)]
                new_vars.append(current_var)
                new_rows.append(sorted(new_vars))
            else:
                new_rows.append(vars.copy())
        rows = new_rows
        current_var += 1
    
    return steps

def single_trial(args):
    """单次试验的包装函数"""
    matrix, trial_id = args
    try:
        steps = paar_optimized(matrix)
        return len(steps), steps
    except Exception as e:
        print(f"试验 {trial_id} 出错: {e}")
        return float('inf'), []

def optimize_single_matrix(matrix, matrix_index, total_matrices):
    """对单个矩阵进行优化（内部使用多进程）"""
    size = len(matrix)
    print(f"开始处理矩阵 {matrix_index + 1}/{total_matrices} ({size}×{size})...")
    
    start_time = time.time()
    best_step_count = float('inf')
    best_steps = []
    
    # 为当前矩阵创建100次试验任务
    tasks = [(matrix, i) for i in range(NUM_TRIALS_PER_MATRIX)]
    
    # 使用多进程并行运行100次试验
    with Pool(cpu_count()) as pool:
        completed = 0
        update_interval = max(1, NUM_TRIALS_PER_MATRIX // 10)  # 每10%更新一次进度
        
        for i, (step_count, steps) in enumerate(pool.imap_unordered(single_trial, tasks)):
            completed += 1
            
            # 更新最优结果
            if step_count < best_step_count:
                best_step_count = step_count
                best_steps = steps
                current_time = time.time() - start_time
                print(f"  矩阵 {matrix_index + 1} 发现新最优: {best_step_count}步 "
                      f"[进度: {completed}/{NUM_TRIALS_PER_MATRIX}, 耗时: {current_time:.1f}s]")
            
            # 定期打印进度
            if completed % update_interval == 0:
                current_time = time.time() - start_time
                progress = completed / NUM_TRIALS_PER_MATRIX * 100
                print(f"  矩阵 {matrix_index + 1} 进度: {completed}/{NUM_TRIALS_PER_MATRIX} "
                      f"({progress:.1f}%), 当前最优: {best_step_count}步")
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"完成矩阵 {matrix_index + 1}/{total_matrices}: 最优步数 = {best_step_count}, "
          f"总耗时 = {processing_time:.2f}s")
    
    return {
        'matrix_index': matrix_index,
        'size': size,
        'best_step_count': best_step_count,
        'best_steps': best_steps,
        'processing_time': processing_time
    }

def main():
    print("开始读取矩阵文件...")
    matrices = read_matrices_from_file(INPUT_FILE)
    print(f"成功读取 {len(matrices)} 个矩阵")
    
    # 按矩阵尺寸分组
    size_groups = {}
    for i, matrix in enumerate(matrices):
        size = len(matrix)
        if size not in size_groups:
            size_groups[size] = []
        size_groups[size].append(i)
    
    print("矩阵尺寸分布:")
    for size in sorted(size_groups.keys()):
        print(f"  {size}×{size}: {len(size_groups[size])} 个矩阵")
    
    # 顺序处理所有矩阵（每个矩阵内部使用多进程）
    print(f"\n开始处理矩阵（每个矩阵使用 {cpu_count()} 个进程运行 {NUM_TRIALS_PER_MATRIX} 次试验）...")
    global_start_time = time.time()
    
    all_results = []
    for i, matrix in enumerate(matrices):
        result = optimize_single_matrix(matrix, i, len(matrices))
        all_results.append(result)
        
        # 打印当前总体进度
        elapsed_time = time.time() - global_start_time
        remaining_matrices = len(matrices) - i - 1
        if remaining_matrices > 0:
            avg_time_per_matrix = elapsed_time / (i + 1)
            estimated_remaining = avg_time_per_matrix * remaining_matrices
            print(f"\n=== 总体进度: {i + 1}/{len(matrices)} "
                  f"({(i + 1)/len(matrices)*100:.1f}%), "
                  f"预计剩余: {estimated_remaining/60:.1f}分钟 ===\n")
    
    total_time = time.time() - global_start_time
    print(f"\n所有矩阵处理完成！总耗时: {total_time/60:.2f}分钟")
    
    # 按尺寸统计结果
    size_stats = {}
    for result in all_results:
        size = result['size']
        if size not in size_stats:
            size_stats[size] = {
                'step_counts': [],
                'matrices': []
            }
        size_stats[size]['step_counts'].append(result['best_step_count'])
        size_stats[size]['matrices'].append(result)
    
    # 写入结果文件
    print(f"\n写入结果到 {RESULTS_FILE}...")
    with open(RESULTS_FILE, 'w') as f:
        # 写入每个矩阵的结果
        f.write(f"总矩阵数: {len(matrices)}\n")
        f.write(f"每个矩阵试验次数: {NUM_TRIALS_PER_MATRIX}\n")
        f.write(f"总耗时: {total_time/60:.2f}分钟\n\n")
        
        f.write("各矩阵详细结果:\n")
        f.write("矩阵索引\t尺寸\t最优步数\t处理时间(s)\n")
        f.write("-" * 50 + "\n")
        
        for result in sorted(all_results, key=lambda x: x['matrix_index']):
            f.write(f"{result['matrix_index'] + 1}\t\t"
                   f"{result['size']}×{result['size']}\t"
                   f"{result['best_step_count']}\t\t"
                   f"{result['processing_time']:.2f}\n")
        
        # 写入各尺寸统计结果
        f.write("\n\n各尺寸统计结果:\n")
        f.write("尺寸\t矩阵数量\t平均步数\t最小步数\t最大步数\n")
        f.write("-" * 60 + "\n")
        
        for size in sorted(size_stats.keys()):
            stats = size_stats[size]
            step_counts = stats['step_counts']
            avg_steps = sum(step_counts) / len(step_counts)
            min_steps = min(step_counts)
            max_steps = max(step_counts)
            
            f.write(f"{size}×{size}\t{len(step_counts)}\t\t{avg_steps:.2f}\t\t{min_steps}\t\t{max_steps}\n")
    
    # 打印最终汇总
    print("\n=== 最终统计结果 ===")
    for size in sorted(size_stats.keys()):
        stats = size_stats[size]
        avg_steps = sum(stats['step_counts']) / len(stats['step_counts'])
        print(f"尺寸 {size}×{size}: {len(stats['step_counts'])}个矩阵, "
              f"平均步数 = {avg_steps:.2f}, "
              f"范围 = [{min(stats['step_counts'])}, {max(stats['step_counts'])}]")

if __name__ == "__main__":
    main()