"""
学生数据生成模块 - 创建学生档案信息，关联到学生用户
"""
import random
from datetime import datetime, timedelta
from django.utils import timezone
from fitness.models import Student

def create_students(student_users, parents, minimal=False):
    """
    为学生用户创建学生档案
    
    参数:
        student_users: 学生用户列表
        parents: 家长用户列表
        minimal: 是否仅创建最少量的数据
    
    返回:
        创建的学生档案列表
    """
    # 学院和专业数据
    colleges = ['计算机学院', '机械工程学院', '电子信息学院', '经济管理学院', '外国语学院']
    majors_by_college = {
        '计算机学院': ['计算机科学与技术', '软件工程', '人工智能', '数据科学与大数据技术'],
        '机械工程学院': ['机械设计制造及其自动化', '车辆工程', '工业设计', '机器人工程'],
        '电子信息学院': ['电子信息工程', '通信工程', '微电子科学与工程', '光电信息科学与工程'],
        '经济管理学院': ['工商管理', '市场营销', '会计学', '财务管理', '国际经济与贸易'],
        '外国语学院': ['英语', '日语', '德语', '法语', '翻译'],
    }
    grades = ['大一', '大二', '大三', '大四']
    
    students = []
    for i, user in enumerate(student_users):
        # 查找是否已存在
        try:
            student = Student.objects.get(user=user)
            print(f"  学生 {user.username} 的档案已存在")
            students.append(student)
            continue
        except Student.DoesNotExist:
            pass
        
        # 随机分配家长
        parent = parents[i % len(parents)] if parents else None
        
        # 随机选择学院和专业
        college = random.choice(colleges)
        major = random.choice(majors_by_college[college])
        
        # 随机性别
        gender = random.choice(['male', 'female'])
        
        # 随机年级和班级
        grade = random.choice(grades)
        class_name = f"{major}{random.randint(1, 3)}班"
        
        # 随机生日（18-24岁）
        years_ago = random.randint(18, 24)
        days_variation = random.randint(-180, 180)
        birth_date = timezone.now().date() - timedelta(days=365*years_ago + days_variation)
        
        # 随机身高体重
        if gender == 'male':
            height = random.randint(165, 185)
            weight = random.randint(55, 80)
        else:
            height = random.randint(155, 170)
            weight = random.randint(45, 65)
        
        # 生成学号
        student_id = f"2025{str(i+1).zfill(4)}"
        
        # 创建学生档案
        student = Student.objects.create(
            user=user,  # 关联到用户账号，遵循两模型认证结构
            student_id=student_id,
            name=user.first_name,
            gender='M' if gender == 'male' else 'F',
            class_name=class_name,
            parent=parent  # 关联到家长账号
        )
        
        students.append(student)
        print(f"  创建学生档案: {student.name} ({student_id})")
    
    return students
