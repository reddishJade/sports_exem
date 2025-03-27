import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
django.setup()

# 导入必要的模块
from django.db import connection
from fitness.models import SportsNews, NewsComment

def check_column_exists(table_name, column_name):
    """检查列是否存在于表中"""
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = '{table_name}' 
              AND COLUMN_NAME = '{column_name}'
        """)
        return cursor.fetchone()[0] > 0

def add_column_if_not_exists(table_name, column_name, column_definition):
    """如果列不存在，则添加它"""
    if not check_column_exists(table_name, column_name):
        print(f"添加列 {column_name} 到表 {table_name}")
        with connection.cursor() as cursor:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")
        return True
    else:
        print(f"列 {column_name} 已存在于表 {table_name} 中")
        return False

def check_foreign_key_exists(table_name, constraint_name):
    """检查外键约束是否存在"""
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = '{table_name}' 
              AND CONSTRAINT_NAME = '{constraint_name}'
        """)
        return cursor.fetchone()[0] > 0

def add_foreign_key_if_not_exists(table_name, column_name, ref_table, ref_column, constraint_name):
    """如果外键约束不存在，则添加它"""
    if not check_foreign_key_exists(table_name, constraint_name):
        # 先确保列存在
        if not check_column_exists(table_name, column_name):
            print(f"列 {column_name} 不存在，无法添加外键约束")
            return False
        
        print(f"添加外键约束 {constraint_name} 到表 {table_name}")
        with connection.cursor() as cursor:
            cursor.execute(f"""
                ALTER TABLE {table_name} 
                ADD CONSTRAINT {constraint_name} 
                FOREIGN KEY ({column_name}) 
                REFERENCES {ref_table}({ref_column})
            """)
        return True
    else:
        print(f"外键约束 {constraint_name} 已存在于表 {table_name} 中")
        return False

def main():
    """执行主要修复操作"""
    try:
        # 添加source_name和source_url列到sports_news表
        source_name_added = add_column_if_not_exists('sports_news', 'source_name', 'VARCHAR(100) NULL')
        source_url_added = add_column_if_not_exists('sports_news', 'source_url', 'VARCHAR(500) NULL')
        
        # 确保news_comment表有news_id列和外键约束
        news_id_added = add_column_if_not_exists('news_comment', 'news_id', 'INTEGER NULL')
        fk_added = add_foreign_key_if_not_exists(
            'news_comment', 'news_id', 'sports_news', 'id', 'fk_news_comment_news'
        )
        
        # 总结
        print("\n修复摘要:")
        if source_name_added or source_url_added:
            print("- 已向sports_news表添加缺失的列")
        else:
            print("- sports_news表中的所有必要列均已存在")
            
        if news_id_added or fk_added:
            print("- 已向news_comment表添加缺失的列和/或外键约束")
        else:
            print("- news_comment表中的所有必要列和约束均已存在")
            
        print("\n数据库修复完成!")
        
    except Exception as e:
        print(f"修复过程中出错: {str(e)}")

if __name__ == "__main__":
    main()
