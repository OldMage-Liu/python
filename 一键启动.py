import subprocess
import time
# 列出可用的模型
list_command = 'ollama list'
try:
    list_result = subprocess.run(list_command, shell=True, capture_output=True, text=True)
    print("可用的模型列表:")
    print(list_result.stdout)
except subprocess.CalledProcessError as e:
    print(f"列出模型失败: {e}")

# 获取用户输入的模型名
model_name = input('输入你想调用的模型: ')

# 构建要执行的命令
command = f'ollama run {model_name}'
kais=time.time()
try:
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print("命令执行结果:")
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print(f"执行模型失败: {e}")
