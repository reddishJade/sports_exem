from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from fitness.models import Student, TestPlan, TestResult, PhysicalStandard, HealthReport, Comment
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = '填充测试数据'

    def handle(self, *args, **kwargs):
        self.stdout.write('开始创建测试数据...')

        # 创建管理员用户
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin',
            user_type='admin',
            phone='13800138000'
        )

        # 创建家长用户
        parent_user = User.objects.create_user(
            username='parent1',
            email='parent1@example.com',
            password='123456',
            user_type='parent',
            phone='13800138001'
        )

        # 创建学生用户
        student_user = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='123456',
            user_type='student',
            phone='13800138002'
        )

        # 创建学生信息
        student = Student.objects.create(
            user=student_user,
            student_id='2025001',
            name='张三',
            gender='M',  # 添加性别字段
            class_name='计算机科学与技术1班',
            parent=parent_user
        )

        # 创建体测标准
        standard_male = PhysicalStandard.objects.create(
            gender='M',
            bmi_min=18.5,
            bmi_max=23.9,
            vital_capacity_excellent=4000,
            run_50m_excellent=7.0,
            sit_and_reach_excellent=20,
            standing_jump_excellent=240,
            run_800m_excellent=180,
            vital_capacity_pass=2000,
            run_50m_pass=9.0,
            sit_and_reach_pass=10,
            standing_jump_pass=180,
            run_800m_pass=240
        )

        standard_female = PhysicalStandard.objects.create(
            gender='F',
            bmi_min=18.5,
            bmi_max=23.9,
            vital_capacity_excellent=3000,
            run_50m_excellent=8.0,
            sit_and_reach_excellent=25,
            standing_jump_excellent=200,
            run_800m_excellent=210,
            vital_capacity_pass=1800,
            run_50m_pass=10.0,
            sit_and_reach_pass=15,
            standing_jump_pass=160,
            run_800m_pass=270
        )

        # 创建测试计划
        current_time = datetime.now()
        test_dates = [
            current_time - timedelta(days=14),  # 两周前
            current_time - timedelta(days=7),   # 一周前
            current_time + timedelta(days=7),   # 一周后
            current_time + timedelta(days=14)   # 两周后
        ]

        for test_date in test_dates:
            plan = TestPlan.objects.create(
                title=f'{test_date.strftime("%Y年%m月%d日")}体能测试',
                test_date=test_date,
                location='体育场',
                description='常规体能测试，包括50米跑、立定跳远、800米跑等项目',
                plan_type='regular'
            )

            # 为过去的测试创建成绩
            if test_date < current_time:
                result = TestResult.objects.create(
                    student=student,
                    test_plan=plan,
                    bmi=round(random.uniform(18.5, 23.9), 1),
                    vital_capacity=random.randint(3500, 4500),
                    run_50m=round(random.uniform(6.8, 7.5), 1),
                    sit_and_reach=random.randint(15, 25),
                    standing_jump=random.randint(230, 250),
                    run_800m=random.randint(170, 190),
                    total_score=random.randint(80, 95),
                    test_date=test_date,
                    is_makeup=False
                )

                # 创建评论
                Comment.objects.create(
                    test_result=result,
                    student=student,
                    content='这次测试发挥得不错，继续保持！',
                    created_at=test_date + timedelta(hours=1),
                    is_approved=True
                )

                # 创建健康报告
                HealthReport.objects.create(
                    test_result=result,
                    overall_assessment='身体素质良好，各项指标达标',
                    health_suggestions='建议继续保持规律运动习惯，每周进行3-4次有氧运动',
                    created_at=test_date + timedelta(hours=2)
                )

        self.stdout.write(self.style.SUCCESS('测试数据创建成功！'))
