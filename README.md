# 项目名称（可选）

## 项目简介

这是一个简单的文件加密和解密工具，它接受命令行参数来指定加密或解密操作，输入文件，输出文件以及密钥。

## 使用说明

### 编译

确保你已经安装了GCC或任何支持C语言的编译器。使用以下命令编译项目：

```bash
gcc -o crypto_tool crypto.c -lcrypto

使用一下命令行格式运行程序

./crypto_tool <mode> <input_file> <output_file> <key>

mode: 操作模式，1 代表加密，2 代表解密。
input_file: 要加密或解密的文件路径。
output_file: 加密或解密后的文件输出路径。
key: 加密或解密使用的密钥

示例：
加密文件：./crypto_tool 1 example.txt encrypted.txt 1234
解密文件：./crypto_tool 2 encrypted.txt decrypted.txt 1234

作者信息
作者：hujunhui
