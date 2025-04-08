"""
健身系统综合测试数据生成脚本

这个脚本用于生成全面的测试数据，包括：
1. 用户数据 (管理员、教师、学生、家长)
2. 体测项目和标准
3. 测试计划和测试结果
4. 新闻公告和评论
5. 健康报告和通知

使用方法:
- 直接运行脚本: python fitness_test_data.py
- 可选参数:
  --clean: 清除所有现有数据后重新生成
  --students=50: 生成指定数量的学生
  --minimal: 仅生成最少量的基础数据
"""

import os
import sys
import django
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# 设置Django环境
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
django.setup()

# 导入Django模型
from django.db import transaction, connection
from django.utils import timezone
from django.contrib.auth import get_user_model
from fitness.models import (
    User, Student, TestPlan, TestResult,
    PhysicalStandard, SportsNews, Comment, NewsComment,
    HealthReport, MakeupNotification, NewsCategory
)

# 导入数据生成模块
from fitness_test_data_modules.users import create_users
from fitness_test_data_modules.students import create_students
from fitness_test_data_modules.fitness_items import create_fitness_standards
from fitness_test_data_modules.test_plans import create_test_plans
from fitness_test_data_modules.test_results import create_test_results
from fitness_test_data_modules.news import create_news
from fitness_test_data_modules.comments import create_comments
from fitness_test_data_modules.health_reports import create_health_reports
from fitness_test_data_modules.notifications import create_notifications

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='生成健身系统测试数据')
    parser.add_argument('--clean', action='store_true', help='清除所有现有数据后重新生成')
    parser.add_argument('--students', type=int, default=50, help='生成的学生数量')
    parser.add_argument('--minimal', action='store_true', help='仅生成最少量的基础数据')
    return parser.parse_args()

def clean_database():
    """清除数据库中的所有数据"""
    print("正在清除现有数据...")
    
    # 获取所有表名（排除Django系统表）
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name NOT LIKE 'django_%' 
            AND table_name NOT LIKE 'auth_%'
        """)
        tables = [row[0] for row in cursor.fetchall()]
    
    # 禁用外键约束
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    
    try:
        # 清空所有表
        with connection.cursor() as cursor:
            for table in tables:
                print(f"  清空 {table} 表")
                cursor.execute(f"TRUNCATE TABLE `{table}`;")
    finally:
        # 恢复外键约束
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    
    print("数据清除完成！")

def main():
    """主函数"""
    args = parse_args()
    
    # 如果指定了clean参数，先清除现有数据
    if args.clean:
        clean_database()
    
    print("开始生成测试数据...")
    
    # 使用事务包装所有数据库操作
    with transaction.atomic():
        # 创建用户数据
        print("1. 创建用户数据...")
        admins, parents, student_users = create_users(
            admin_count=2,
            parent_count=args.students // 3,  # 大约每3个学生对应1个家长
            student_count=args.students,
            minimal=args.minimal
        )
        
        # 创建学生数据
        print("2. 创建学生资料...")
        students = create_students(
            student_users=student_users,
            parents=parents,
            minimal=args.minimal
        )
        
        # 创建体测标准
        print("3. 创建体测标准...")
        standards = create_fitness_standards()
        
        # 创建测试计划
        print("4. 创建测试计划...")
        test_plans = create_test_plans(minimal=args.minimal)
        
        # 创建测试结果
        print("5. 创建测试结果...")
        test_results = create_test_results(
            students=students,
            test_plans=test_plans,
            minimal=args.minimal
        )
        
        # 创建新闻公告
        print("6. 创建新闻公告...")
        news_items = create_news(
            admin_users=admins,
            minimal=args.minimal
        )
        
        # 创建评论
        print("7. 创建评论...")
        comments = create_comments(
            students=students,
            test_results=test_results,
            news_items=news_items,
            minimal=args.minimal
        )
        
        # 创建健康报告
        print("8. 创建健康报告...")
        reports = create_health_reports(
            test_results=test_results,
            minimal=args.minimal
        )
        
        # 创建通知
        print("9. 创建通知...")
        notifications = create_notifications(
            students=students,
            test_plans=test_plans,
            test_results=test_results,
            minimal=args.minimal
        )
    
    print("\n测试数据生成完成！")
    print(f"创建了 {len(admins)} 个管理员用户")
    print(f"创建了 {len(parents)} 个家长用户")
    print(f"创建了 {len(students)} 个学生")
    print(f"创建了 {len(test_plans)} 个测试计划")
    print(f"创建了 {len(test_results)} 个测试结果")
    print(f"创建了 {len(news_items)} 条新闻公告")
    print(f"创建了 {len(comments)} 条评论")
    print(f"创建了 {len(reports)} 份健康报告")
    print(f"创建了 {len(notifications)} 条通知")
    
    # 显示登录信息
    print("\n可用的测试账号:")
    print("管理员: admin/admin123")
    print("学生: student1/student123")
    print("家长: parent1/parent123")

if __name__ == "__main__":
    main()
