"""
测试计划数据生成模块 - 创建体测计划和安排
"""
import random
from datetime import datetime, timedelta
from django.utils import timezone
from fitness.models import TestPlan

def create_test_plans(minimal=False):
    """
    创建测试计划数据
    
    参数:
        minimal: 是否仅创建最少量的数据
    
    返回:
        创建的测试计划列表
    """
    # 检查是否已存在
    existing_plans = TestPlan.objects.all()
    if existing_plans.exists():
        print("  测试计划已存在，使用现有数据")
        return list(existing_plans)
    
    # 设置创建数量
    if minimal:
        plan_count = 2  # 最少创建2个计划（1个常规，1个补考）
    else:
        plan_count = 6  # 创建6个计划（4个常规，2个补考）
    
    plans = []
    current_date = timezone.now().date()
    
    # 生成测试计划 - 过去、当前和未来的多个计划
    time_offsets = [
        -60,  # 60天前（已结束）
        -30,  # 30天前（已结束）
        -5,   # 5天前（刚刚结束）
        5,    # 5天后（即将开始）
        30,   # 30天后（未来计划）
        60    # 60天后（远期计划）
    ]
    
    # 如果是minimal模式，只用两个计划（一个过去，一个未来）
    if minimal:
        time_offsets = [-30, 30]
    
    for i, offset in enumerate(time_offsets[:plan_count]):
        # 创建常规测试
        test_date = current_date + timedelta(days=offset)
        
        # 确定测试状态（此处是内部状态跟踪，不影响数据库）
        if test_date < current_date:
            status = 'completed'
        elif test_date == current_date:
            status = 'in_progress'
        else:
            status = 'upcoming'
        
        # 不同的测试类型
        is_makeup = (i % 3 == 2)  # 每3个计划中的第3个是补考
        
        # 创建测试计划
        plan_type = 'makeup' if is_makeup else 'regular'
        semester = '春季' if test_date.month < 7 else '秋季'
        year = test_date.year
        
        title = f"{year}年{semester}{'体质测试补考' if is_makeup else '体质测试'}"
        location = random.choice(['田径场', '体育馆', '测试中心', '综合体育场'])
        description = (
            f"{'补测安排' if is_makeup else '常规测试安排'}，测试时间为{test_date.strftime('%Y年%m月%d日')}，"
            f"请同学们提前做好准备。"
            f"\n\n测试项目包括：身高体重、肺活量、立定跳远、坐位体前屈、50米跑、800米跑（女）/1000米跑（男）等。"
            f"\n\n请穿着运动服装准时参加。"
        )
        
        # 创建测试计划记录，匹配TestPlan模型的字段
        plan = TestPlan.objects.create(
            title=title,
            description=description,
            test_date=timezone.now() + timedelta(days=offset),  # 直接使用timezone.now()
            location=location,
            plan_type=plan_type
        )
        
        # 记录内部状态，用于其他模块判断测试状态
        plan.status = status  
        
        plans.append(plan)
        print(f"  创建测试计划: {plan.title} ({status})")
    
    return plans
