"""
补考通知数据生成模块 - 为不及格的测试结果创建补考通知
"""
import random
from django.utils import timezone
from datetime import timedelta
from fitness.models import MakeupNotification, TestResult, Student, TestPlan

def create_makeup_notifications(test_results, test_plans, minimal=False):
    """
    创建补考通知数据
    
    参数:
        test_results: 测试结果列表
        test_plans: 测试计划列表
        minimal: 是否仅创建最少量的数据
    
    返回:
        创建的补考通知列表
    """
    # 检查是否已存在
    existing_notifications = MakeupNotification.objects.all()
    if existing_notifications.exists():
        print(f"  已存在 {existing_notifications.count()} 条补考通知，使用现有数据")
        return list(existing_notifications)
    
    notifications = []
    
    # 查找已完成的测试计划中的不及格结果
    failed_results = []
    for result in test_results:
        # 使用is_passed属性或判断总分<60
        if hasattr(result, 'is_passed'):
            if not result.is_passed and not result.is_makeup:
                failed_results.append(result)
        elif result.total_score < 60 and not result.is_makeup:
            failed_results.append(result)
    
    # 对于minimal模式，限制结果数量
    if minimal and len(failed_results) > 5:
        failed_results = random.sample(failed_results, 5)
    
    # 找出类型为补考的测试计划
    makeup_plans = [plan for plan in test_plans if plan.plan_type == 'makeup']
    
    # 如果没有找到补考计划，创建一个
    if not makeup_plans:
        future_date = timezone.now().date() + timedelta(days=14)  # 两周后
        makeup_plan = TestPlan.objects.create(
            title="体测补考",
            description="本次为体测不及格学生提供的补考机会，请相关学生按时参加。",
            start_date=future_date,
            end_date=future_date + timedelta(days=2),
            location="体育馆",
            status="upcoming",
            plan_type="makeup",
            is_makeup=True
        )
        makeup_plans = [makeup_plan]
        print(f"  创建补考计划: {makeup_plan.title}")
    
    # 为每个不及格结果创建补考通知
    for result in failed_results:
        # 随机选择一个补考计划
        makeup_plan = random.choice(makeup_plans)
        
        # 创建补考通知
        notification = MakeupNotification.objects.create(
            student=result.student,
            test_plan=makeup_plan,
            original_result=result,
            is_read=random.choice([True, False]),
            sent_at=timezone.now() - timedelta(days=random.randint(1, 7))
        )
        
        notifications.append(notification)
        print(f"  为学生 {result.student.name} 创建补考通知")
    
    return notifications
