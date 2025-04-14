# Generated by Django 5.1.7 on 2025-03-23 20:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fitness', '0006_remove_sportsnews_category_remove_newscomment_news_and_more'),
    ]

    operations = [
        # 添加source_name列
        migrations.RunSQL(
            sql="""
            -- SQLite doesn't support IF NOT EXISTS for columns, so we need to check if column exists
            -- and add it only if it doesn't
            SELECT CASE 
                WHEN NOT EXISTS(SELECT 1 FROM pragma_table_info('sports_news') WHERE name='source_name') 
                THEN 'ALTER TABLE sports_news ADD COLUMN source_name VARCHAR(100) NULL;'
            END;
            """,
            reverse_sql="ALTER TABLE sports_news DROP COLUMN source_name;",
            elidable=True  # 忽略错误
        ),
        
        # 添加source_url列
        migrations.RunSQL(
            sql="""
            SELECT CASE 
                WHEN NOT EXISTS(SELECT 1 FROM pragma_table_info('sports_news') WHERE name='source_url') 
                THEN 'ALTER TABLE sports_news ADD COLUMN source_url VARCHAR(255) NULL;'
            END;
            """,
            reverse_sql="ALTER TABLE sports_news DROP COLUMN source_url;",
            elidable=True
        ),
        
        # 添加pub_date列
        migrations.RunSQL(
            sql="""
            SELECT CASE 
                WHEN NOT EXISTS(SELECT 1 FROM pragma_table_info('sports_news') WHERE name='pub_date') 
                THEN 'ALTER TABLE sports_news ADD COLUMN pub_date DATETIME NULL;'
            END;
            """,
            reverse_sql="ALTER TABLE sports_news DROP COLUMN pub_date;",
            elidable=True
        ),
        
        # 添加news_id列到news_comment表
        migrations.RunSQL(
            sql="""
            SELECT CASE 
                WHEN NOT EXISTS(SELECT 1 FROM pragma_table_info('news_comment') WHERE name='news_id') 
                THEN 'ALTER TABLE news_comment ADD COLUMN news_id INTEGER NULL REFERENCES sports_news(id);'
            END;
            """,
            reverse_sql="",  # 不需要反向操作
            elidable=True  # 忽略错误
        ),
        
        # 添加student_id列
        migrations.RunSQL(
            sql="""
            SELECT CASE 
                WHEN NOT EXISTS(SELECT 1 FROM pragma_table_info('news_comment') WHERE name='student_id') 
                THEN 'ALTER TABLE news_comment ADD COLUMN student_id BIGINT NULL REFERENCES student(id);'
            END;
            """,
            reverse_sql="",
            elidable=True
        ),
    ]
