"""
健身系统综合测试数据生成脚本 (整合版)

这个脚本整合了原有测试数据生成脚本的功能，并修复了一些模型关联问题。包括：
1. 用户数据 (管理员、家长、学生)
2. 体测项目和标准
3. 测试计划和测试结果
4. 新闻公告和评论
5. 健康报告和补考通知

使用方法:
- 直接运行脚本: python fitness_test_data_consolidated.py
- 可选参数:
  --clean: 清除所有现有数据后重新生成
  --students=50: 生成指定数量的学生
  --minimal: 仅生成最少量的基础数据
  --test: 使用测试数据库 (db_test.sqlite3)
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

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='生成测试数据')
    parser.add_argument('--clean', action='store_true', help='清除现有数据')
    parser.add_argument('--students', type=int, default=50, help='生成的学生数量')
    parser.add_argument('--minimal', action='store_true', help='仅生成最少量的数据')
    parser.add_argument('--test', action='store_true', help='使用测试数据库')
    return parser.parse_args()

# 解析参数，设置适当的配置
args = parse_args()
if args.test:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings_test')
    print("使用测试数据库配置...")
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
    print("使用默认数据库配置...")

django.setup()

# 导入Django模型
from django.db import transaction, connection
from django.utils import timezone
from django.contrib.auth import get_user_model
from fitness.models import (
    User, Student, TestPlan, TestResult,
    PhysicalStandard, SportsNews, NewsComment,
    HealthReport, MakeupNotification
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
from fitness_test_data_modules.notifications import create_makeup_notifications

def clean_database():
    """清除数据库中的所有数据"""
    print("正在清除现有数据...")
    
    # 使用事务包装所有数据库操作
    with transaction.atomic():
        # 清除数据的顺序很重要，需要先清除有外键依赖的表
        MakeupNotification.objects.all().delete()
        print("  通知数据已清除")
        
        HealthReport.objects.all().delete()
        print("  健康报告数据已清除")
        
        NewsComment.objects.all().delete()
        print("  评论数据已清除")
        
        SportsNews.objects.all().delete()
        print("  新闻数据已清除")
        
        TestResult.objects.all().delete()
        print("  测试结果数据已清除")
        
        TestPlan.objects.all().delete()
        print("  测试计划数据已清除")
        
        PhysicalStandard.objects.all().delete()
        print("  体测标准数据已清除")
        
        # 清除学生和用户数据（需要保留超级管理员）
        Student.objects.all().delete()
        print("  学生档案数据已清除")
        
        # 保留superuser
        User.objects.filter(is_superuser=False).delete()
        print("  普通用户数据已清除 (保留了超级管理员)")
    
    print("数据清除完成！")

def main():
    """主函数"""
    global args
    
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
            news_items=news_items,
            student_users=student_users,
            minimal=args.minimal
        )
        
        # 创建健康报告
        print("8. 创建健康报告...")
        reports = create_health_reports(
            test_results=test_results,
            admin_users=admins,
            minimal=args.minimal
        )
        
        # 创建补考通知
        print("9. 创建补考通知...")
        notifications = create_makeup_notifications(
            test_results=test_results,
            test_plans=test_plans,
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
    print(f"创建了 {len(notifications)} 条补考通知")
    
    # 显示登录信息
    print("\n可用的测试账号:")
    print("管理员: admin/admin123")
    print("学生: student1/student123")
    print("家长: parent1/parent123")

if __name__ == "__main__":
    main()
