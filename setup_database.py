"""
数据库初始化脚本 - 帮助新用户在克隆项目后设置数据库环境
"""
import os
import sys
import subprocess
import argparse
import pymysql
import time
import re
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量（如果有）
load_dotenv()

def parse_args():
    parser = argparse.ArgumentParser(description="数据库初始化工具")
    
    # 数据库配置
    parser.add_argument("--host", default="127.0.0.1", help="数据库主机")
    parser.add_argument("--port", type=int, default=3306, help="数据库端口")
    parser.add_argument("--user", default="root", help="数据库用户名")
    parser.add_argument("--password", required=True, help="数据库密码")
    parser.add_argument("--db-name", default="fitness_db", help="数据库名称")
    
    # 操作选项
    parser.add_argument("--schema-only", action="store_true", help="仅创建表结构，不导入示例数据")
    parser.add_argument("--update-settings", action="store_true", help="更新Django设置文件")
    parser.add_argument("--dump-file", default=None, help="从指定SQL文件导入（若不指定则使用内置的db_schema.sql）")
    
    return parser.parse_args()

def check_mysql_installed():
    """检查MySQL是否已安装"""
    try:
        # 尝试通过命令行检查MySQL版本
        process = subprocess.Popen(["mysql", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        
        if process.returncode == 0:
            print(f"检测到MySQL: {output.decode().strip()}")
            return True
        else:
            return False
    except:
        try:
            # 尝试连接到localhost
            connection = pymysql.connect(
                host="127.0.0.1",
                port=3306,
                user="root",
                password="",  # 尝试空密码连接
                connect_timeout=3
            )
            connection.close()
            print("检测到MySQL服务器运行中")
            return True
        except:
            return False

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

def create_schema_only(host, port, user, password, database):
    """创建数据库表结构（不含数据）"""
    try:
        # 连接到数据库
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        
        # 获取Django迁移SQL路径
        project_dir = Path(__file__).resolve().parent
        django_dir = project_dir / 'backend'
        
        if not django_dir.exists():
            print("找不到Django项目目录")
            return False
        
        # 运行Django迁移命令
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
        sys.path.insert(0, str(django_dir))
        
        try:
            import django
            django.setup()
            
            from django.core.management import call_command
            print("正在运行Django迁移...")
            call_command('migrate')
            print("Django迁移完成")
            return True
        except Exception as e:
            print(f"Django迁移错误: {e}")
            
            # 如果Django迁移失败，尝试创建基本表结构
            print("尝试创建基本表结构...")
            schema_sql = """
-- 这里可以放置基本的表结构SQL
-- 用户表
CREATE TABLE IF NOT EXISTS `user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `user_type` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 学生表
CREATE TABLE IF NOT EXISTS `student` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `student_id` varchar(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `gender` varchar(10) NOT NULL,
  `date_of_birth` date DEFAULT NULL,
  `grade` varchar(50) DEFAULT NULL,
  `class_name` varchar(50) DEFAULT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_id` (`student_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `student_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 测试结果表
CREATE TABLE IF NOT EXISTS `test_result` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `test_date` date NOT NULL,
  `height` decimal(5,2) DEFAULT NULL,
  `weight` decimal(5,2) DEFAULT NULL,
  `vital_capacity` int DEFAULT NULL,
  `fifty_run` decimal(5,2) DEFAULT NULL,
  `sit_and_reach` decimal(5,2) DEFAULT NULL,
  `standing_long_jump` decimal(5,2) DEFAULT NULL,
  `body_mass_index` decimal(5,2) DEFAULT NULL,
  `eight_hundred_run` varchar(10) DEFAULT NULL,
  `one_thousand_run` varchar(10) DEFAULT NULL,
  `pull_up` int DEFAULT NULL,
  `sit_up` int DEFAULT NULL,
  `student_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `student_id` (`student_id`),
  CONSTRAINT `test_result_student_id_fk` FOREIGN KEY (`student_id`) REFERENCES `student` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            
            with connection.cursor() as cursor:
                try:
                    # 执行基本表结构SQL
                    cursor.execute(schema_sql)
                    connection.commit()
                    print("已创建基本表结构")
                    return True
                except Exception as e:
                    print(f"创建表结构错误: {e}")
                    return False
        
        return False
    except Exception as e:
        print(f"数据库操作错误: {e}")
        return False

def import_from_sql_file(host, port, user, password, database, sql_file):
    """从SQL文件导入数据库"""
    try:
        # 尝试使用mysql命令
        cmd = [
            "mysql",
            f"--host={host}",
            f"--port={port}",
            f"--user={user}",
            f"--password={password}",
            "--default-character-set=utf8mb4",
            database
        ]
        
        with open(sql_file, 'r', encoding='utf8') as f:
            process = subprocess.Popen(cmd, stdin=f)
            process.wait()
            if process.returncode == 0:
                print(f"已从{sql_file}导入数据")
                return True
            else:
                print(f"使用mysql命令导入失败，错误代码: {process.returncode}")
                print("尝试使用Python方法导入...")
    except Exception as e:
        print(f"使用mysql命令导入失败: {e}")
        print("尝试使用Python方法导入...")
    
    # 如果MySQL命令行导入失败，使用Python方法
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        
        # 读取SQL文件
        with open(sql_file, 'r', encoding='utf8') as f:
            sql_content = f.read()
        
        # 将SQL文件分割成单独的语句
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
        print(f"数据已成功导入到 {database}")
        return True
    except Exception as e:
        print(f"Python导入数据库错误: {e}")
        return False

def update_django_settings(host, port, user, password, database):
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
        'NAME': '{database}',
        'USER': '{user}',
        'PASSWORD': '{password}',  
        'HOST': '{host}',
        'PORT': '{port}',
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

def create_admin_user(host, port, user, password, database):
    """创建一个管理员用户"""
    try:
        # Django方式创建超级用户
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
        project_dir = Path(__file__).resolve().parent
        django_dir = project_dir / 'backend'
        sys.path.insert(0, str(django_dir))
        
        try:
            import django
            django.setup()
            
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # 检查是否已存在超级用户
            if User.objects.filter(is_superuser=True).exists():
                print("管理员用户已存在，跳过创建")
                return True
            
            # 创建超级用户
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                user_type='admin'
            )
            print(f"已创建管理员用户: admin (密码: admin123)")
            return True
        except Exception as e:
            print(f"创建Django管理员用户错误: {e}")
            
            # 如果Django方式失败，尝试直接SQL方式
            connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                charset='utf8mb4'
            )
            
            with connection.cursor() as cursor:
                # 检查用户表中是否已有管理员
                cursor.execute("SELECT COUNT(*) FROM user WHERE is_superuser = 1")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    print("管理员用户已存在，跳过创建")
                    return True
                
                # 创建管理员用户 (密码是 'admin123' 的哈希值)
                cursor.execute("""
                INSERT INTO user (password, is_superuser, username, first_name, last_name, 
                                email, is_staff, is_active, date_joined, user_type)
                VALUES (
                    'pbkdf2_sha256$720000$l5gpxzkbdIeM0OvUi8qfAP$q8+XaFDJOUZ+/VgLXWfd/Mb6uaTxhQhVQ42WdVQ19lA=', 
                    1, 'admin', '', '', 'admin@example.com', 1, 1, NOW(), 'admin'
                )
                """)
                connection.commit()
                
                print(f"已创建管理员用户: admin (密码: admin123)")
                return True
            
    except Exception as e:
        print(f"创建管理员用户错误: {e}")
        return False

def prompt_mysql_installation():
    """提示用户安装MySQL"""
    print("\n=== MySQL安装指南 ===")
    if sys.platform == 'win32':
        print("Windows系统安装MySQL:")
        print("1. 下载MySQL安装程序: https://dev.mysql.com/downloads/installer/")
        print("2. 运行安装程序并按照向导操作")
        print("3. 安装完成后，确保MySQL服务已启动")
        print("4. 记住您设置的root密码")
    elif sys.platform == 'darwin':
        print("macOS系统安装MySQL:")
        print("1. 使用Homebrew安装: brew install mysql")
        print("2. 启动MySQL服务: brew services start mysql")
        print("3. 设置root密码: mysql_secure_installation")
    else:
        print("Linux系统安装MySQL:")
        print("Ubuntu/Debian: sudo apt install mysql-server")
        print("CentOS/RHEL: sudo yum install mysql-server")
        print("启动服务: sudo systemctl start mysqld")
        print("设置root密码: sudo mysql_secure_installation")
    
    print("\n安装完成后，请重新运行此脚本")
    print("===================\n")

def main():
    args = parse_args()
    
    # 检查MySQL是否已安装
    if not check_mysql_installed():
        print("未检测到MySQL服务。请先安装MySQL数据库。")
        prompt_mysql_installation()
        return
    
    # 检查数据库连接
    print("正在检查数据库连接...")
    if not check_mysql_connection(args.host, args.port, args.user, args.password):
        print("无法连接到MySQL服务器，请检查连接信息")
        return
    
    # 创建数据库（如果不存在）
    print(f"正在确保数据库 {args.db_name} 存在...")
    if not create_database_if_not_exists(args.host, args.port, args.user, args.password, args.db_name):
        print("无法创建数据库，脚本终止")
        return
    
    # 根据参数选择操作
    if args.dump_file:
        # 从指定SQL文件导入
        if not os.path.isfile(args.dump_file):
            print(f"找不到SQL文件: {args.dump_file}")
            return
        
        print(f"正在从{args.dump_file}导入数据...")
        if not import_from_sql_file(args.host, args.port, args.user, args.password, args.db_name, args.dump_file):
            print("导入数据失败")
            return
    elif args.schema_only:
        # 仅创建表结构
        print("正在创建数据库表结构...")
        if not create_schema_only(args.host, args.port, args.user, args.password, args.db_name):
            print("创建表结构失败")
            return
    else:
        # 检查是否有默认的SQL文件
        default_dump = Path(__file__).resolve().parent / 'db_dump.sql'
        if default_dump.exists():
            print(f"找到默认数据库转储文件: {default_dump}")
            print("正在导入默认数据...")
            if not import_from_sql_file(args.host, args.port, args.user, args.password, args.db_name, default_dump):
                print("导入默认数据失败")
                # 尝试只创建表结构
                print("尝试只创建表结构...")
                if not create_schema_only(args.host, args.port, args.user, args.password, args.db_name):
                    print("创建表结构失败")
                    return
        else:
            # 没有默认SQL文件，只创建表结构
            print("未找到默认数据库转储文件，将只创建表结构")
            if not create_schema_only(args.host, args.port, args.user, args.password, args.db_name):
                print("创建表结构失败")
                return
    
    # 尝试创建管理员用户
    print("正在创建管理员用户...")
    create_admin_user(args.host, args.port, args.user, args.password, args.db_name)
    
    # 如果指定了更新Django设置
    if args.update_settings:
        print("正在更新Django设置...")
        update_django_settings(args.host, args.port, args.user, args.password, args.db_name)
    
    print("\n=== 数据库设置完成! ===")
    print(f"数据库名称: {args.db_name}")
    print(f"主机: {args.host}")
    print(f"端口: {args.port}")
    print("管理员用户: admin (如果创建成功)")
    print("管理员密码: admin123")
    print("现在可以启动Django应用了")
    print("=====================")

if __name__ == "__main__":
    main()
