import os
import django
import MySQLdb

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
django.setup()

from django.conf import settings

def update_table_charset():
    """更新AI聊天相关表的字符集为UTF-8mb4"""
    print("正在连接到数据库...")
    db_settings = settings.DATABASES['default']
    
    # 连接到MySQL数据库
    connection = MySQLdb.connect(
        host=db_settings['HOST'],
        user=db_settings['USER'],
        passwd=db_settings['PASSWORD'],
        db=db_settings['NAME'],
        port=int(db_settings['PORT'])
    )
    
    cursor = connection.cursor()
    
    try:
        # 修改数据库字符集
        print("修改数据库字符集...")
        cursor.execute(f"ALTER DATABASE `{db_settings['NAME']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        
        # 获取并修改ai_chat应用的所有表
        print("正在查询AI聊天应用相关表...")
        cursor.execute(f"SHOW TABLES LIKE 'ai_chat_%';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"正在修改表 {table_name} 的字符集...")
            cursor.execute(f"ALTER TABLE `{table_name}` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            
            # 获取表中的文本/字符串列并修改它们的字符集
            cursor.execute(f"SHOW COLUMNS FROM `{table_name}`;")
            columns = cursor.fetchall()
            
            for column in columns:
                column_name = column[0]
                column_type = column[1].lower()
                
                # 检查是否为文本类型列
                if 'char' in column_type or 'text' in column_type:
                    print(f"  - 修改列 {column_name} 的字符集...")
                    cursor.execute(f"ALTER TABLE `{table_name}` MODIFY `{column_name}` {column_type.upper()} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        
        print("完成! 所有AI聊天相关表已更新为utf8mb4编码。")
        
    except Exception as e:
        print(f"错误: {str(e)}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    update_table_charset()
