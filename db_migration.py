"""
数据库迁移脚本 - 将MySQL数据库从一个主机迁移到另一个主机
支持纯Python实现，不依赖mysqldump和mysql命令行工具
"""
import os
import sys
import subprocess
import argparse
import pymysql
import time
import re
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量（如果有）
load_dotenv()

def parse_args():
    parser = argparse.ArgumentParser(description="数据库迁移工具")
    
    # 源数据库配置
    parser.add_argument("--source-host", default="127.0.0.1", help="源数据库主机")
    parser.add_argument("--source-port", type=int, default=3306, help="源数据库端口")
    parser.add_argument("--source-user", default="root", help="源数据库用户名")
    parser.add_argument("--source-password", default="123456", help="源数据库密码")
    parser.add_argument("--source-db", default="fitness_db", help="源数据库名称")
    
    # 目标数据库配置
    parser.add_argument("--target-host", required=True, help="目标数据库主机")
    parser.add_argument("--target-port", type=int, default=3306, help="目标数据库端口")
    parser.add_argument("--target-user", default="root", help="目标数据库用户名")
    parser.add_argument("--target-password", required=True, help="目标数据库密码")
    parser.add_argument("--target-db", default="fitness_db", help="目标数据库名称")
    
    # 操作选项
    parser.add_argument("--dump-file", default="db_dump.sql", help="SQL转储文件名")
    parser.add_argument("--local-only", action="store_true", help="仅模拟本地迁移测试")
    parser.add_argument("--update-settings", action="store_true", help="更新Django设置文件")
    parser.add_argument("--pure-python", action="store_true", help="使用纯Python方法，不依赖mysqldump")
    
    return parser.parse_args()

def check_mysql_connection(host, port, user, password, database=None):
    """检查MySQL连接是否可用"""
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database if database else None,
            connect_timeout=5
        )
        connection.close()
        return True
    except Exception as e:
        print(f"连接错误: {e}")
        return False

def create_database_if_not_exists(host, port, user, password, database):
    """如果数据库不存在则创建"""
    try:
        # 先连接到MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        with connection.cursor() as cursor:
            # 使用正确的字符集创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        connection.close()
        print(f"数据库 '{database}' 已创建或已存在")
        return True
    except Exception as e:
        print(f"创建数据库错误: {e}")
        return False

def dump_database(host, port, user, password, database, dump_file):
    """将数据库导出到SQL文件"""
    try:
        # 尝试使用mysqldump命令（如果可用）
        cmd = [
            "mysqldump",
            f"--host={host}",
            f"--port={port}",
            f"--user={user}",
            f"--password={password}",
            "--single-transaction",
            "--set-gtid-purged=OFF",
            "--default-character-set=utf8mb4",
            database
        ]
        
        with open(dump_file, 'w', encoding='utf8') as f:
            process = subprocess.Popen(cmd, stdout=f)
            process.wait()
            if process.returncode == 0:
                print(f"数据库已成功导出到 {dump_file}")
                return True
            else:
                print(f"使用mysqldump导出失败，错误代码: {process.returncode}")
                return False
    except Exception as e:
        print(f"使用mysqldump导出出错: {e}")
        return False

def dump_database_python(host, port, user, password, database, dump_file):
    """使用纯Python方法将数据库导出到SQL文件"""
    try:
        print("使用纯Python方法导出数据库...")
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 获取所有表
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            with open(dump_file, 'w', encoding='utf8') as f:
                # 写入SQL文件头部
                f.write("-- 由Python生成的数据库转储\n")
                f.write(f"-- 数据库: {database}\n")
                f.write(f"-- 日期: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("SET NAMES utf8mb4;\n")
                f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")
                
                # 处理每个表
                for table in tables:
                    table_name = table[0]
                    print(f"处理表: {table_name}")
                    
                    # 获取表结构
                    cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
                    table_structure = cursor.fetchone()[1]
                    
                    f.write(f"-- 表结构 `{table_name}`\n")
                    f.write(f"DROP TABLE IF EXISTS `{table_name}`;\n")
                    f.write(f"{table_structure};\n\n")
                    
                    # 获取表数据
                    cursor.execute(f"SELECT * FROM `{table_name}`")
                    rows = cursor.fetchall()
                    
                    if rows:
                        # 获取列名
                        cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
                        columns = [column[0] for column in cursor.fetchall()]
                        
                        f.write(f"-- 表数据 `{table_name}`\n")
                        f.write(f"INSERT INTO `{table_name}` (`{'`, `'.join(columns)}`) VALUES\n")
                        
                        # 写入数据行
                        row_values = []
                        for row in rows:
                            values = []
                            for value in row:
                                if value is None:
                                    values.append("NULL")
                                elif isinstance(value, (int, float)):
                                    values.append(str(value))
                                elif isinstance(value, bytes):
                                    # 处理二进制数据
                                    values.append(f"0x{value.hex()}")
                                else:
                                    # 转义字符串
                                    escaped = str(value).replace("'", "''").replace("\\", "\\\\")
                                    values.append(f"'{escaped}'")
                            row_values.append(f"({', '.join(values)})")
                        
                        f.write(",\n".join(row_values))
                        f.write(";\n\n")
                
                f.write("SET FOREIGN_KEY_CHECKS = 1;\n")
        
        connection.close()
        print(f"数据库已成功使用Python导出到 {dump_file}")
        return True
    except Exception as e:
        print(f"Python导出数据库错误: {e}")
        return False

def import_database(host, port, user, password, database, dump_file):
    """从SQL文件导入数据库"""
    try:
        cmd = [
            "mysql",
            f"--host={host}",
            f"--port={port}",
            f"--user={user}",
            f"--password={password}",
            "--default-character-set=utf8mb4",
            database
        ]
        
        with open(dump_file, 'r', encoding='utf8') as f:
            process = subprocess.Popen(cmd, stdin=f)
            process.wait()
            if process.returncode == 0:
                print(f"数据库已成功导入到 {database}")
                return True
            else:
                print(f"使用mysql命令导入失败，错误代码: {process.returncode}")
                return False
    except Exception as e:
        print(f"使用mysql命令导入出错: {e}")
        return False

def import_database_python(host, port, user, password, database, dump_file):
    """使用纯Python方法从SQL文件导入数据库"""
    try:
        print("使用纯Python方法导入数据库...")
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        
        # 读取SQL文件
        with open(dump_file, 'r', encoding='utf8') as f:
            sql_content = f.read()
        
        # 将SQL文件分割成单独的语句
        # 这里的分割逻辑比较简单，可能需要根据具体SQL文件结构调整
        statements = re.split(r';\s*\n', sql_content)
        
        with connection.cursor() as cursor:
            # 设置外键约束检查为0
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # 执行每个语句
            count = 0
            for statement in statements:
                statement = statement.strip()
                if statement:
                    try:
                        cursor.execute(statement)
                        count += 1
                    except Exception as e:
                        print(f"执行SQL语句错误: {e}")
                        print(f"问题语句: {statement[:100]}...")
            
            # 恢复外键约束检查
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            connection.commit()
        
        connection.close()
        print(f"已成功执行 {count} 条SQL语句")
        print(f"数据库已成功使用Python方法导入到 {database}")
        return True
    except Exception as e:
        print(f"Python导入数据库错误: {e}")
        return False

def update_django_settings(target_host, target_port, target_user, target_password, target_db):
    """更新Django的settings.py文件中的数据库配置"""
    settings_path = Path(__file__).resolve().parent / 'backend' / 'fitness_backend' / 'settings.py'
    
    if not settings_path.exists():
        print(f"未找到设置文件: {settings_path}")
        return False
    
    # 读取当前设置文件
    with open(settings_path, 'r', encoding='utf8') as f:
        settings_content = f.read()
    
    # 创建备份
    backup_path = settings_path.with_suffix('.py.bak')
    with open(backup_path, 'w', encoding='utf8') as f:
        f.write(settings_content)
    
    # 更新数据库配置
    import re
    
    # 使用正则表达式找到数据库配置部分并替换
    db_config_pattern = r"DATABASES\s*=\s*\{[^}]*'default':[^}]*\}[^}]*\}"
    new_db_config = f"""DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '{target_db}',
        'USER': '{target_user}',
        'PASSWORD': '{target_password}',  
        'HOST': '{target_host}',
        'PORT': '{target_port}',
        'OPTIONS': {{
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'; SET NAMES 'utf8mb4'; SET CHARACTER SET utf8mb4; SET character_set_connection=utf8mb4; SET collation_connection=utf8mb4_unicode_ci;",
        }}
    }}
}}"""
    
    updated_settings = re.sub(db_config_pattern, new_db_config, settings_content)
    
    # 保存更新后的设置文件
    with open(settings_path, 'w', encoding='utf8') as f:
        f.write(updated_settings)
    
    print(f"Django设置已更新。备份文件保存在 {backup_path}")
    return True

def main():
    args = parse_args()
    
    # 默认使用纯Python方法，避免依赖外部命令
    pure_python = True
    
    # 检查源数据库连接
    print("正在检查源数据库连接...")
    if not check_mysql_connection(args.source_host, args.source_port, args.source_user, args.source_password, args.source_db):
        print("无法连接到源数据库，迁移终止")
        return
    
    # 如果是本地模拟测试，创建一个新的本地数据库
    if args.local_only:
        print("正在进行本地迁移测试...")
        # 设置目标为本地主机，但使用不同的数据库名
        args.target_host = args.source_host
        args.target_port = args.source_port
        args.target_user = args.source_user
        args.target_password = args.source_password
        args.target_db = f"{args.source_db}_migrated"
    
    # 检查目标数据库连接（不指定数据库名）
    print("正在检查目标数据库服务器连接...")
    if not check_mysql_connection(args.target_host, args.target_port, args.target_user, args.target_password):
        print("无法连接到目标数据库服务器，迁移终止")
        return
    
    # 在目标服务器上创建数据库（如果不存在）
    print(f"正在确保目标数据库 {args.target_db} 存在...")
    if not create_database_if_not_exists(args.target_host, args.target_port, args.target_user, args.target_password, args.target_db):
        print("无法创建目标数据库，迁移终止")
        return
    
    # 导出源数据库
    print("正在导出源数据库...")
    if pure_python:
        dump_success = dump_database_python(args.source_host, args.source_port, args.source_user, args.source_password, args.source_db, args.dump_file)
    else:
        dump_success = dump_database(args.source_host, args.source_port, args.source_user, args.source_password, args.source_db, args.dump_file)
    
    if not dump_success:
        print("导出源数据库失败，迁移终止")
        return
    
    # 导入到目标数据库
    print("正在导入到目标数据库...")
    if pure_python:
        import_success = import_database_python(args.target_host, args.target_port, args.target_user, args.target_password, args.target_db, args.dump_file)
    else:
        import_success = import_database(args.target_host, args.target_port, args.target_user, args.target_password, args.target_db, args.dump_file)
    
    if not import_success:
        print("导入到目标数据库失败")
        return
    
    # 如果指定了更新Django设置
    if args.update_settings:
        print("正在更新Django设置...")
        update_django_settings(args.target_host, args.target_port, args.target_user, args.target_password, args.target_db)
    
    print("数据库迁移完成！")

if __name__ == "__main__":
    main()
