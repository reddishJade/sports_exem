import os
import sys
import django
import logging
from django.db import connection

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
django.setup()

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def execute_sql(sql):
    """执行SQL语句并处理异常"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
        logger.info(f"成功执行SQL: {sql}")
        return True
    except Exception as e:
        logger.error(f"执行SQL出错: {sql}")
        logger.error(f"错误信息: {e}")
        return False

def main():
    # 1. 添加 pub_date 列到 sports_news 表
    logger.info("1. 添加 pub_date 列到 sports_news 表")
    execute_sql("ALTER TABLE sports_news ADD COLUMN pub_date DATETIME NULL")
    
    # 2. 添加 featured_image 列到 sports_news 表
    logger.info("2. 添加 featured_image 列到 sports_news 表")
    execute_sql("ALTER TABLE sports_news ADD COLUMN featured_image VARCHAR(500) NULL")
    
    # 3. 添加 status, views, keywords, is_featured 列到 sports_news 表
    logger.info("3. 添加其他缺失的列到 sports_news 表")
    execute_sql("ALTER TABLE sports_news ADD COLUMN status VARCHAR(20) DEFAULT 'published'")
    execute_sql("ALTER TABLE sports_news ADD COLUMN views INTEGER DEFAULT 0")
    execute_sql("ALTER TABLE sports_news ADD COLUMN keywords VARCHAR(500) NULL")
    execute_sql("ALTER TABLE sports_news ADD COLUMN is_featured TINYINT(1) DEFAULT 0")
    
    # 4. 添加 student_id 列到 news_comment 表
    logger.info("4. 添加 student_id 列到 news_comment 表")
    execute_sql("ALTER TABLE news_comment ADD COLUMN student_id BIGINT NULL")
    
    # 5. 添加 is_approved 列到 news_comment 表
    logger.info("5. 添加 is_approved 列到 news_comment 表")
    execute_sql("ALTER TABLE news_comment ADD COLUMN is_approved TINYINT(1) DEFAULT 0")
    
    # 6. 添加外键约束从 news_comment.student_id 到 student.id
    logger.info("6. 添加外键约束从 news_comment.student_id 到 student.id")
    execute_sql("""
    ALTER TABLE news_comment
    ADD CONSTRAINT fk_news_comment_student
    FOREIGN KEY (student_id)
    REFERENCES student(id)
    """)
    
    logger.info("\n修复完成! 请重新访问管理页面查看效果。")

if __name__ == "__main__":
    main()
