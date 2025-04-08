"""
用户数据生成模块 - 创建管理员、家长和学生用户
"""
import random
from django.contrib.auth import get_user_model

User = get_user_model()

def create_users(admin_count=2, parent_count=15, student_count=50, minimal=False):
    """
    创建用户数据
    
    参数:
        admin_count: 创建的管理员数量
        parent_count: 创建的家长数量
        student_count: 创建的学生数量
        minimal: 是否仅创建最少量的数据
    
    返回:
        (admin_users, parent_users, student_users) 元组
    """
    # 如果只需最少量数据，则减少创建数量
    if minimal:
        admin_count = min(admin_count, 1)
        parent_count = min(parent_count, 5) 
        student_count = min(student_count, 10)
    
    # 创建管理员用户
    admin_users = []
    for i in range(1, admin_count + 1):
        username = f"admin{i}" if i > 1 else "admin"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f"{username}@example.com",
                'user_type': 'admin',  # 确保用户类型为admin
                'is_staff': True,
                'is_superuser': True if i == 1 else False,  # 第一个管理员是超级用户
                'first_name': f"管理员{i}",
                'last_name': ''
            }
        )
        
        if created:
            user.set_password('admin123')
            user.save()
            print(f"  创建管理员: {username}")
        else:
            print(f"  管理员 {username} 已存在")
        
        admin_users.append(user)
    
    # 创建家长用户
    parent_users = []
    for i in range(1, parent_count + 1):
        username = f"parent{i}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f"{username}@example.com",
                'user_type': 'parent',  # 确保用户类型为parent
                'is_staff': False,
                'is_superuser': False,
                'first_name': random.choice(["王", "李", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴"]) + random.choice(["先生", "女士"]),
                'last_name': ''
            }
        )
        
        if created:
            user.set_password('parent123')
            user.save()
            print(f"  创建家长: {username}")
        else:
            print(f"  家长 {username} 已存在")
        
        parent_users.append(user)
    
    # 创建学生用户
    student_users = []
    for i in range(1, student_count + 1):
        username = f"student{i}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f"{username}@example.com",
                'user_type': 'student',  # 确保用户类型为student
                'is_staff': False,
                'is_superuser': False,
                'first_name': f"学生{i}",
                'last_name': ''
            }
        )
        
        if created:
            user.set_password('student123')
            user.save()
            print(f"  创建学生用户: {username}")
        else:
            print(f"  学生用户 {username} 已存在")
        
        student_users.append(user)
    
    return admin_users, parent_users, student_users
