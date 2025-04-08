"""
体测标准数据生成模块 - 创建体测项目和评分标准
"""
from fitness.models import PhysicalStandard

def create_fitness_standards():
    """
    创建体测标准数据
    
    返回:
        创建的体测标准字典 {'M': male_standard, 'F': female_standard}
    """
    # 检查是否已存在
    existing_standards = PhysicalStandard.objects.all()
    if existing_standards.exists():
        print("  体测标准已存在，使用现有数据")
        standards = {}
        for standard in existing_standards:
            standards[standard.gender] = standard
        return standards
    
    # 为男性创建标准
    male_standard = PhysicalStandard.objects.create(
        gender='M',
        bmi_min=18.5,
        bmi_max=23.9,
        vital_capacity_excellent=4000,
        vital_capacity_pass=3000,
        run_50m_excellent=7.0,
        run_50m_pass=8.0,
        sit_and_reach_excellent=20,
        sit_and_reach_pass=10,
        standing_jump_excellent=240,
        standing_jump_pass=200,
        run_800m_excellent=240,  # 由于模型中没有1000米，统一使用800米字段
        run_800m_pass=300
    )
    print("  创建男性体测标准")
    
    # 为女性创建标准
    female_standard = PhysicalStandard.objects.create(
        gender='F',
        bmi_min=17.8,
        bmi_max=23.9,
        vital_capacity_excellent=3000,
        vital_capacity_pass=2000,
        run_50m_excellent=8.0,
        run_50m_pass=9.0,
        sit_and_reach_excellent=25,
        sit_and_reach_pass=15,
        standing_jump_excellent=185,
        standing_jump_pass=155,
        run_800m_excellent=215,  # 3:35 转换为秒
        run_800m_pass=265  # 4:25 转换为秒
    )
    print("  创建女性体测标准")
    
    return {'M': male_standard, 'F': female_standard}
