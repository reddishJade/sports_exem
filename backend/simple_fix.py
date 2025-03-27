import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
django.setup()

from django.db import connection

def execute_sql(sql):
    """执行SQL语句并打印结果"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
        print(f"成功执行SQL: {sql}")
        return True
    except Exception as e:
        print(f"SQL执行失败 ({sql}): {str(e)}")
        return False

def main():
    # 修改news_id列类型为bigint，与sports_news.id兼容
    execute_sql("ALTER TABLE news_comment MODIFY COLUMN news_id BIGINT NULL")
    
    # 删除可能存在的旧外键约束（如果存在）
    execute_sql("ALTER TABLE news_comment DROP FOREIGN KEY IF EXISTS fk_news_comment_news")
    
    # 尝试添加外键约束
    result = execute_sql("""
    ALTER TABLE news_comment 
    ADD CONSTRAINT fk_news_comment_news 
    FOREIGN KEY (news_id) 
    REFERENCES sports_news(id)
    """)
    
    if result:
        print("\n✅ 数据库修复成功! 外键关系已建立。")
    else:
        print("\n❌ 数据库修复失败。请检查错误信息。")

if __name__ == "__main__":
    main()
