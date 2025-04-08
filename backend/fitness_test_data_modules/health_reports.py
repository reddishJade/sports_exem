"""
健康报告数据生成模块 - 为测试结果创建健康评估报告
"""
import random
from django.utils import timezone
from datetime import timedelta
from fitness.models import HealthReport

def create_health_reports(test_results, admin_users, minimal=False):
    """
    创建健康报告数据
    
    参数:
        test_results: 测试结果列表
        admin_users: 管理员用户列表（用作报告创建者）
        minimal: 是否仅创建最少量的数据
    
    返回:
        创建的健康报告列表
    """
    # 检查是否已存在
    existing_reports = HealthReport.objects.all()
    if existing_reports.exists():
        print(f"  已存在 {existing_reports.count()} 份健康报告，使用现有数据")
        return list(existing_reports)
    
    reports = []
    
    # 如果是minimal模式，仅为部分结果创建报告
    if minimal:
        # 只为20%的测试结果创建报告
        result_sample = random.sample(test_results, k=max(1, int(len(test_results) * 0.2)))
    else:
        # 为80%的测试结果创建报告
        result_sample = random.sample(test_results, k=max(1, int(len(test_results) * 0.8)))
    
    for result in result_sample:
        # 随机选择一个管理员用户作为评估者
        evaluator = random.choice(admin_users)
        
        # 创建报告日期（测试日期后1-5天）
        report_date = result.test_date + timedelta(days=random.randint(1, 5))
        # 确保报告日期不超过当前日期
        current_date = timezone.now()
        if report_date > current_date:
            report_date = current_date
        
        # 生成健康评级
        score = result.total_score
        if score >= 90:
            health_rating = 'excellent'
        elif score >= 75:
            health_rating = 'good'
        elif score >= 60:
            health_rating = 'average'
        else:
            health_rating = 'poor'
        
        # 生成评估内容
        content = generate_health_evaluation(result, health_rating)
        
        # 生成建议
        recommendations = generate_health_recommendations(result, health_rating)
        
        # 创建健康报告
        report = HealthReport.objects.create(
            test_result=result,
            overall_assessment=content,
            health_suggestions=recommendations
        )
        
        reports.append(report)
        print(f"  为学生 {result.student.name} 创建健康报告: {health_rating}")
    
    return reports

def generate_health_evaluation(result, health_rating):
    """生成健康评估内容"""
    student = result.student
    
    # 基于BMI的评估
    bmi = result.bmi  # 修正为正确的字段名
    if bmi < 18.5:
        bmi_evaluation = f"体重过轻，BMI值为{bmi}，低于正常范围（18.5-24.9）。"
    elif bmi <= 24.9:
        bmi_evaluation = f"体重正常，BMI值为{bmi}，在健康范围内（18.5-24.9）。"
    elif bmi <= 29.9:
        bmi_evaluation = f"超重，BMI值为{bmi}，高于正常范围（>24.9）。"
    else:
        bmi_evaluation = f"肥胖，BMI值为{bmi}，远高于正常范围（>29.9）。"
    
    # 基于总体评价的评估
    overall_evaluation = ""
    if health_rating == 'excellent':
        overall_evaluation = f"{student.name}同学的体质状况非常优秀，测试成绩为{result.total_score}分，各项指标均表现良好。继续保持目前的体育锻炼习惯和健康生活方式。"
    elif health_rating == 'good':
        overall_evaluation = f"{student.name}同学的体质状况良好，测试成绩为{result.total_score}分，大部分指标表现良好，但仍有提升空间。"
    elif health_rating == 'average':
        overall_evaluation = f"{student.name}同学的体质状况一般，测试成绩为{result.total_score}分，部分指标需要改善。建议增加体育锻炼频率，提高身体素质。"
    else:
        overall_evaluation = f"{student.name}同学的体质状况较差，测试成绩为{result.total_score}分，多数指标表现不佳。需要制定科学的健身计划，改善体质状况。"
    
    # 组合评估内容
    evaluation = f"""体测结果综合评估：

{overall_evaluation}

身体质量评估：
{bmi_evaluation}

测试日期：{result.test_date}
评估日期：{timezone.now().date()}
"""
    
    return evaluation

def generate_health_recommendations(result, health_rating):
    """生成健康建议"""
    student = result.student
    
    # 基础建议
    base_recommendations = [
        "保持规律作息，每天保证7-8小时睡眠",
        "均衡饮食，增加蔬果摄入，减少高糖高脂食物",
        "每周至少进行3次中等强度的有氧运动，每次30分钟以上",
        "多喝水，保持充分的水分摄入",
        "保持良好的心态，学会调节压力"
    ]
    
    # 根据BMI给出的建议
    bmi = result.bmi  # 修正为正确的字段名
    bmi_recommendations = []
    if bmi < 18.5:
        bmi_recommendations = [
            "适当增加热量摄入，多吃高蛋白食物",
            "结合力量训练增加肌肉量",
            "建议每天增加300-500卡路里的摄入量"
        ]
    elif bmi <= 24.9:
        bmi_recommendations = [
            "保持当前的饮食结构和运动量",
            "定期监测体重变化",
            "继续保持健康的生活方式"
        ]
    elif bmi <= 29.9:
        bmi_recommendations = [
            "控制每日热量摄入，减少精制碳水化合物",
            "增加有氧运动时间，每周至少150分钟",
            "每天记录饮食日志，注意饮食结构"
        ]
    else:
        bmi_recommendations = [
            "在专业人士指导下制定减重计划",
            "增加有氧运动频率，每周至少5次，每次30分钟以上",
            "严格控制热量摄入，减少高热量食物",
            "建议寻求营养师的专业指导"
        ]
    
    # 根据健康评级给出的建议
    rating_recommendations = []
    if health_rating == 'excellent':
        rating_recommendations = [
            "继续保持当前的锻炼习惯",
            "尝试更多样化的运动方式，保持兴趣",
            "可以适当增加训练强度，提高竞技水平"
        ]
    elif health_rating == 'good':
        rating_recommendations = [
            "增加训练频率，每周4-5次有计划的锻炼",
            "增强耐力训练，提高心肺功能",
            "有针对性地改善薄弱项目"
        ]
    elif health_rating == 'average':
        rating_recommendations = [
            "制定科学的锻炼计划，坚持执行",
            "增加锻炼频率和强度，每周至少4次",
            "关注营养摄入，增加蛋白质和维生素的补充",
            "重点改善耐力和力量项目"
        ]
    else:
        rating_recommendations = [
            "寻求专业体育教师的指导，制定个性化锻炼计划",
            "从低强度运动开始，逐渐增加强度",
            "每天保证至少30分钟的有氧运动",
            "注重基础体能的提升，如耐力、力量和柔韧性",
            "定期复查，监测体质改善情况"
        ]
    
    # 组合所有建议
    all_recommendations = base_recommendations + bmi_recommendations + rating_recommendations
    
    # 随机选择其中的5-8条（避免太多）
    recommendation_count = random.randint(5, min(8, len(all_recommendations)))
    selected_recommendations = random.sample(all_recommendations, recommendation_count)
    
    # 格式化建议内容
    recommendations = "健康改善建议：\n\n"
    for i, rec in enumerate(selected_recommendations, 1):
        recommendations += f"{i}. {rec}\n"
    
    return recommendations
