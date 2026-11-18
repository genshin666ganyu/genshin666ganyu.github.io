import numpy as np

def main():
    # 打开文件
    with open("example.txt", "r") as dd, open("result.txt", "r") as qq, open("final_result.txt", "w") as fp:
        # 读取矩阵数量
        n = int(dd.readline().strip())
        
        # 存储矩阵信息
        row = [0] * n
        lie = [0] * n
        e = [None] * n  # 存储每个矩阵的数据
        
        # 读取所有矩阵
        for t in range(n):
            data = dd.readline().split()
            row[t] = int(data[0])
            lie[t] = int(data[1])
            
            # 初始化当前矩阵
            e[t] = np.zeros((row[t], lie[t]), dtype=int)
            
            # 读取矩阵数据
            for i in range(row[t]):
                row_data = list(map(int, dd.readline().split()))
                for j in range(lie[t]):
                    e[t][i][j] = row_data[j]
        
        # 读取结果文件中的矩阵数量
        n_result = int(qq.readline().strip())
        ans = row[0]  # 初始行数
        base_index = 0  # 当前矩阵的列偏移量
        bb = [None] * n  # 存储每个矩阵的行索引映射
        zh = {}  # 存储行索引映射
        
        # 处理每个矩阵
        for t in range(n_result):
            # 读取操作序列长度
            len_ops = int(qq.readline().strip())
            
            # 初始化当前矩阵的基础行
            yy = np.zeros((1000, lie[t]), dtype=int)
            for i in range(lie[t]):
                yy[base_index + i][i] = 1
            
            # 初始化当前矩阵的行索引映射
            bb[t] = [-1] * row[t]
            
            # 处理每个操作
            for _ in range(len_ops):
                # 读取三元组 (a, b, c)
                a, b, c = map(int, qq.readline().split())
                
                # 处理行索引映射
                b = zh.get(b, base_index + b)
                c = zh.get(c, base_index + c)
                zh[a] = ans
                
                # 计算新行：异或操作
                yy[ans] = yy[b] ^ yy[c]
                
                # 写入操作到输出文件
                fp.write(f"{ans} {b} {c}\n")
                
                # 检查是否匹配原始矩阵的行
                for i in range(row[t]):
                    if np.array_equal(yy[ans][:lie[t]], e[t][i]):
                        bb[t][i] = ans
                        break
                
                ans += 1
            
            # 更新列偏移量
            base_index += lie[t]
        
        # 处理所有矩阵的对应行
        for i in range(row[0]):
            # 第一个矩阵的行
            current = bb[0][i]
            
            # 组合所有矩阵的对应行
            for j in range(1, n):
                next_val = bb[j][i]
                # 写入组合操作
                fp.write(f"{ans} {current} {next_val}\n")
                current = ans
                ans += 1

if __name__ == "__main__":
    main()