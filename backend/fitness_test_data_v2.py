#!/usr/bin/env python
"""
体育测试系统 - 测试数据生成脚本 (模块化版本)

该脚本用于生成体育测试系统所需的全部测试数据，包括：
- 用户数据（管理员、学生、家长）
- 学生档案信息
- 体测标准
- 测试计划
- 测试结果
- 新闻和公告
- 评论
- 健康报告
- 系统通知

使用方法:
python fitness_test_data_v2.py [--clean] [--minimal] [--student-count=数量]

参数:
--clean            清空现有数据后重新生成
--minimal          生成最少量的数据用于测试
--student-count=N  指定生成的学生数量，默认为50

例子:
python fitness_test_data_v2.py                # 生成完整测试数据
python fitness_test_data_v2.py --clean        # 清空现有数据并重新生成
python fitness_test_data_v2.py --minimal      # 生成最少量的测试数据
python fitness_test_data_v2.py --student-count=100  # 生成100个学生的测试数据
"""

import os
import sys
import django
import argparse
import time

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# 导入Django模型
from django.contrib.auth import get_user_model
from django.db import connection
from fitness.models import (
    Student, PhysicalStandard, TestPlan, TestResult,
    SportsNews, NewsCategory, Comment, HealthReport, Notification
)

# 导入各个模块
from fitness_test_data_modules.users import create_users
from fitness_test_data_modules.students import create_students
from fitness_test_data_modules.fitness_items import create_fitness_standards
from fitness_test_data_modules.test_plans import create_test_plans
from fitness_test_data_modules.test_results import create_test_results
from fitness_test_data_modules.news import create_news
from fitness_test_data_modules.comments import create_comments
from fitness_test_data_modules.health_reports import create_health_reports
from fitness_test_data_modules.notifications import create_notifications

User = get_user_model()

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='生成体育测试系统的测试数据')
    parser.add_argument('--clean', action='store_true', help='清空现有数据后重新生成')
    parser.add_argument('--minimal', action='store_true', help='生成最少量的数据用于测试')
    parser.add_argument('--student-count', type=int, default=50, help='指定生成的学生数量，默认为50')
    return parser.parse_args()

def clean_data():
    """清空现有数据"""
    print("正在清空现有数据...")
    
    # 删除数据的顺序很重要，需要考虑外键依赖关系
    print("  删除通知数据...")
    Notification.objects.all().delete()
    
    print("  删除健康报告数据...")
    HealthReport.objects.all().delete()
    
    print("  删除评论数据...")
    Comment.objects.all().delete()
    
    print("  删除新闻数据...")
    SportsNews.objects.all().delete()
    
    print("  删除新闻分类数据...")
    NewsCategory.objects.all().delete()
    
    print("  删除测试结果数据...")
    TestResult.objects.all().delete()
    
    print("  删除测试计划数据...")
    TestPlan.objects.all().delete()
    
    print("  删除体测标准数据...")
    PhysicalStandard.objects.all().delete()
    
    print("  删除学生档案数据...")
    Student.objects.all().delete()
    
    print("  删除用户数据...")
    # 保留超级用户
    User.objects.exclude(is_superuser=True).delete()
    
    print("数据清空完成")

def generate_test_data(clean=False, minimal=False, student_count=50):
    """生成测试数据"""
    start_time = time.time()
    
    print("\n=== 体育测试系统 - 测试数据生成 ===")
    print(f"模式: {'最小数据集' if minimal else '完整数据集'}")
    print(f"学生数量: {student_count if not minimal else '最小数量'}")
    
    # 清空现有数据（如果指定了--clean参数）
    if clean:
        clean_data()
    
    print("\n1. 创建用户数据...")
    admin_users, parent_users, student_users = create_users(
        admin_count=2,
        parent_count=15,
        student_count=student_count,
        minimal=minimal
    )
    
    print("\n2. 创建学生档案...")
    students = create_students(student_users, parent_users, minimal=minimal)
    
    print("\n3. 创建体测标准...")
    standards = create_fitness_standards()
    
    print("\n4. 创建测试计划...")
    test_plans = create_test_plans(minimal=minimal)
    
    print("\n5. 创建测试结果...")
    test_results = create_test_results(students, test_plans, minimal=minimal)
    
    print("\n6. 创建新闻和公告...")
    news_items = create_news(admin_users, minimal=minimal)
    
    print("\n7. 创建评论...")
    comments = create_comments(news_items, student_users, minimal=minimal)
    
    print("\n8. 创建健康报告...")
    health_reports = create_health_reports(test_results, admin_users, minimal=minimal)
    
    print("\n9. 创建系统通知...")
    notifications = create_notifications(students, test_plans, minimal=minimal)
    
    # 计算执行时间
    elapsed_time = time.time() - start_time
    
    # 打印数据统计
    print("\n=== 数据生成完成 ===")
    print(f"  用户: {len(admin_users) + len(parent_users) + len(student_users)} (管理员: {len(admin_users)}, 家长: {len(parent_users)}, 学生: {len(student_users)})")
    print(f"  学生档案: {len(students)}")
    print(f"  体测标准: {len(standards)}")
    print(f"  测试计划: {len(test_plans)}")
    print(f"  测试结果: {len(test_results)}")
    print(f"  新闻和公告: {len(news_items)}")
    print(f"  评论: {len(comments)}")
    print(f"  健康报告: {len(health_reports)}")
    print(f"  系统通知: {len(notifications)}")
    
    print(f"\n执行时间: {elapsed_time:.2f} 秒")
    print("测试数据生成完成！")

if __name__ == "__main__":
    # 解析命令行参数
    args = parse_arguments()
    
    # 生成测试数据
    generate_test_data(
        clean=args.clean,
        minimal=args.minimal,
        student_count=args.student_count
    )
