import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
django.setup()

# 导入必要的模块
from django.db import connection

def get_column_type(table_name, column_name):
    """获取列的数据类型"""
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT DATA_TYPE, COLUMN_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = '{table_name}' 
              AND COLUMN_NAME = '{column_name}'
        """)
        result = cursor.fetchone()
        if result:
            return result
        return None

def modify_column_type(table_name, column_name, new_type):
    """修改列的数据类型"""
    with connection.cursor() as cursor:
        cursor.execute(f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} {new_type}")
    print(f"已将表 {table_name} 中的列 {column_name} 类型修改为 {new_type}")

def main():
    try:
        # 获取源表ID列的数据类型
        sports_news_id_type = get_column_type('sports_news', 'id')
        news_comment_id_type = get_column_type('news_comment', 'news_id')
        
        if sports_news_id_type and news_comment_id_type:
            print(f"sports_news 表的 id 列类型: {sports_news_id_type}")
            print(f"news_comment 表的 news_id 列类型: {news_comment_id_type}")
            
            # 如果类型不匹配，修改 news_id 的类型
            if sports_news_id_type != news_comment_id_type:
                print("列类型不匹配，正在修改 news_id 列的类型...")
                # 获取sports_news.id的具体类型定义
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SHOW CREATE TABLE sports_news
                    """)
                    create_table = cursor.fetchone()[1]
                    import re
                    # 提取id列的完整定义
                    id_def_match = re.search(r'`id`\s+([^,\n]+)', create_table)
                    if id_def_match:
                        id_definition = id_def_match.group(1).strip()
                        print(f"sports_news.id 的完整定义: {id_definition}")
                        
                        # 修改 news_comment.news_id 的类型
                        modify_column_type('news_comment', 'news_id', id_definition)
                        
                        # 尝试添加外键约束
                        print("尝试添加外键约束...")
                        with connection.cursor() as cursor:
                            try:
                                cursor.execute("""
                                    ALTER TABLE news_comment 
                                    ADD CONSTRAINT fk_news_comment_news 
                                    FOREIGN KEY (news_id) 
                                    REFERENCES sports_news(id)
                                """)
                                print("外键约束添加成功！")
                            except Exception as e:
                                print(f"添加外键约束失败: {str(e)}")
            else:
                print("列类型匹配，可以直接添加外键约束")
                # 尝试添加外键约束
                with connection.cursor() as cursor:
                    try:
                        cursor.execute("""
                            ALTER TABLE news_comment 
                            ADD CONSTRAINT fk_news_comment_news 
                            FOREIGN KEY (news_id) 
                            REFERENCES sports_news(id)
                        """)
                        print("外键约束添加成功！")
                    except Exception as e:
                        print(f"添加外键约束失败: {str(e)}")
        else:
            print("无法获取列类型信息")
        
    except Exception as e:
        print(f"执行过程中出错: {str(e)}")

if __name__ == "__main__":
    main()
