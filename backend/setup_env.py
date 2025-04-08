"""
此脚本将指导用户创建或更新.env文件，
设置DeepSeek API密钥环境变量
"""

import os
import sys

def setup_env():
    env_file = '.env'
    
    # 检查.env文件是否存在
    env_exists = os.path.exists(env_file)
    
    # 确定要写入的内容
    api_key = input("请输入您的DeepSeek API密钥 (sk-xxxxxxxx): ")
    if not api_key:
        print("错误: API密钥不能为空")
        return
    
    if not api_key.startswith('sk-'):
        print("警告: DeepSeek API密钥通常以'sk-'开头。请确认您输入的密钥是否正确。")
        confirm = input("是否继续? (y/n): ")
        if confirm.lower() != 'y':
            return
    
    # 读取现有.env文件内容（如果存在）
    env_content = {}
    if env_exists:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_content[key.strip()] = value.strip()
    
    # 更新或添加DeepSeek API密钥
    env_content['DEEPSEEK_API_KEY'] = api_key
    
    # 写入更新后的内容
    with open(env_file, 'w') as f:
        for key, value in env_content.items():
            f.write(f"{key}={value}\n")
    
    print(f"\n成功{'更新' if env_exists else '创建'} .env 文件，DeepSeek API密钥已设置。")
    print("您现在需要重启Django服务器以应用这些更改。")

if __name__ == "__main__":
    setup_env()
