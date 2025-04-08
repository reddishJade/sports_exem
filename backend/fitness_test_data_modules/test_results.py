"""
测试结果数据生成模块 - 为学生创建体测结果数据
"""
import random
from django.utils import timezone
from datetime import datetime, timedelta
from fitness.models import TestResult

def create_test_results(students, test_plans, minimal=False):
    """
    创建测试结果数据
    
    参数:
        students: 学生列表
        test_plans: 测试计划列表
        minimal: 是否仅创建最少量的数据
    
    返回:
        创建的测试结果列表
    """
    # 检查是否已存在
    existing_results = TestResult.objects.all()
    if existing_results.exists():
        print(f"  已存在 {existing_results.count()} 条测试结果，使用现有数据")
        return list(existing_results)
    
    results = []
    
    # 找出已完成的测试计划（使用内部状态属性）
    completed_plans = [plan for plan in test_plans if hasattr(plan, 'status') and plan.status == 'completed']
    in_progress_plans = [plan for plan in test_plans if hasattr(plan, 'status') and plan.status == 'in_progress']
    
    # 如果没有完成的计划，至少要有一个
    if not completed_plans and not in_progress_plans:
        completed_plans = [test_plans[0]]  # 使用第一个计划
    
    # 如果是minimal模式，限制学生数量
    if minimal:
        students = students[:10]  # 只创建10个学生的结果
    
    # 为每个学生创建一条测试结果 - 先处理已完成的
    for student in students:
        # 已完成的测试计划都创建结果
        for plan in completed_plans:
            result = generate_test_result(student, plan)
            results.append(result)
            
        # 如果是完整模式，为20%的学生创建进行中计划的结果
        if not minimal and in_progress_plans and random.random() < 0.2:
            plan = random.choice(in_progress_plans)
            result = generate_test_result(student, plan)
            results.append(result)
            
        print(f"  为学生 {student.name} 创建测试结果")
    
    return results

def generate_test_result(student, plan):
    """为学生生成一条测试结果"""
    # 测试日期 - 使用计划日期或稍早
    test_date = plan.test_date.date()
    if hasattr(plan, 'status') and plan.status == 'completed':
        # 对于已完成的测试，日期应该在计划日期当天或之前的几天
        days_before = random.randint(0, 3)  # 最多提前3天测试
        test_date = test_date - timedelta(days=days_before)
    
    # 随机生成各项指标，根据性别有所不同
    gender = student.gender
    
    # 生成身高体重相关的指标
    if gender == 'M':  # 男生
        height = random.randint(165, 185)
        weight = random.randint(55, 80)
    else:  # 女生
        height = random.randint(155, 170)
        weight = random.randint(45, 65)
    
    # 计算BMI
    bmi = round(weight / ((height / 100) ** 2), 1)
    
    # 生成肺活量
    if gender == 'M':
        vital_capacity = random.randint(2800, 4500)
    else:
        vital_capacity = random.randint(2000, 3500)
    
    # 生成50米跑成绩
    if gender == 'M':
        fifty_run = round(random.uniform(6.5, 10.0), 1)
    else:
        fifty_run = round(random.uniform(7.5, 11.0), 1)
    
    # 生成坐位体前屈成绩
    if gender == 'M':
        sit_and_reach = round(random.uniform(5.0, 25.0), 1)
    else:
        sit_and_reach = round(random.uniform(8.0, 30.0), 1)
    
    # 生成立定跳远成绩
    if gender == 'M':
        standing_long_jump = round(random.uniform(180.0, 260.0), 1)
    else:
        standing_long_jump = round(random.uniform(150.0, 220.0), 1)
    
    # 生成长跑成绩（秒数）
    if gender == 'M':
        # 1000米跑（男生），但存储在800米字段中
        minutes = random.randint(3, 6)
        seconds = random.randint(0, 59)
        run_time_seconds = minutes * 60 + seconds
    else:
        # 800米跑（女生）
        minutes = random.randint(3, 5)
        seconds = random.randint(0, 59)
        run_time_seconds = minutes * 60 + seconds
    
    # 生成引体向上/仰卧起坐成绩
    if gender == 'M':
        pull_up = random.randint(0, 20)
        sit_up = None
    else:
        sit_up = random.randint(20, 50)
        pull_up = None
    
    # 计算总成绩（简化计算，实际情况可能更复杂）
    # 假设每个项目20分，总分100分
    score_items = [
        # BMI在正常范围内得满分，否则扣分
        20 if (18.5 <= bmi <= 24.9) else max(0, 20 - abs(bmi - 21.7) * 2),
        
        # 肺活量
        min(20, vital_capacity / (4000 if gender == 'M' else 3000) * 20),
        
        # 50米跑 - 越小越好
        min(20, max(0, 20 - (fifty_run - (7.0 if gender == 'M' else 8.0)) * 4)),
        
        # 坐位体前屈
        min(20, sit_and_reach / (20 if gender == 'M' else 25) * 20),
        
        # 立定跳远
        min(20, standing_long_jump / (240 if gender == 'M' else 185) * 20)
    ]
    total_score = round(sum(score_items))
    
    # 创建测试结果记录
    result = TestResult.objects.create(
        student=student,
        test_plan=plan,
        bmi=bmi,
        vital_capacity=vital_capacity,
        run_50m=fifty_run,
        sit_and_reach=sit_and_reach,
        standing_jump=standing_long_jump,
        run_800m=run_time_seconds,  # 统一使用秒为单位
        total_score=total_score,
        is_makeup=False
    )
    
    return result
