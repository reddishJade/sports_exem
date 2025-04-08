import os
import django
import random
from datetime import datetime, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
django.setup()

from django.utils import timezone
from fitness.models import User, Student, SportsNews as News, Comment, NewsComment
from fitness.models import TestPlan as FitnessItem, PhysicalStandard as FitnessStandard
from fitness.models import HealthReport as FitnessTip
from fitness.models import Student as StudentInfo
from fitness.models import TestPlan as Exam, TestResult as ExamItem

def create_fitness_items():
    """创建体测项目数据"""
    if FitnessItem.objects.count() > 0:
        print("体测项目已存在，跳过创建")
        return FitnessItem.objects.all()
    
    fitness_items = [
        {
            'name': '身高体重',
            'description': '测量身高（厘米）和体重（公斤），计算BMI指数',
            'unit': 'BMI值',
            'is_higher_better': False,  # BMI标准范围是最好的
        },
        {
            'name': '肺活量',
            'description': '测量最大呼气量，反映肺部功能',
            'unit': '毫升(ml)',
            'is_higher_better': True,
        },
        {
            'name': '立定跳远',
            'description': '测量下肢爆发力',
            'unit': '厘米(cm)',
            'is_higher_better': True,
        },
        {
            'name': '坐位体前屈',
            'description': '测量躯干和下肢关节的柔韧性',
            'unit': '厘米(cm)',
            'is_higher_better': True,
        },
        {
            'name': '50米跑',
            'description': '测量速度素质',
            'unit': '秒(s)',
            'is_higher_better': False,  # 时间越短越好
        },
        {
            'name': '引体向上',
            'description': '测量上肢和肩带力量',
            'unit': '次数',
            'is_higher_better': True,
        },
        {
            'name': '仰卧起坐',
            'description': '测量腹肌耐力',
            'unit': '次数/分钟',
            'is_higher_better': True,
        },
        {
            'name': '1000米跑',
            'description': '测量男生心肺耐力',
            'unit': '分:秒',
            'is_higher_better': False,  # 时间越短越好
        },
        {
            'name': '800米跑',
            'description': '测量女生心肺耐力',
            'unit': '分:秒',
            'is_higher_better': False,  # 时间越短越好
        },
    ]
    
    created_items = []
    for item_data in fitness_items:
        item = FitnessItem.objects.create(**item_data)
        created_items.append(item)
        print(f"创建体测项目: {item.name}")
        
        # 为每个项目创建标准
        create_fitness_standards(item)
        
        # 为每个项目创建建议
        create_fitness_tips(item)
    
    return created_items

def create_fitness_standards(item):
    """为体测项目创建标准"""
    # 男生标准
    if item.name == '身高体重':
        # BMI标准一般为18.5-23.9正常
        FitnessStandard.objects.create(item=item, gender='male', level='excellent', min_value=18.5, max_value=23.9, score=100)
        FitnessStandard.objects.create(item=item, gender='male', level='good', min_value=17.0, max_value=25.0, score=85)
        FitnessStandard.objects.create(item=item, gender='male', level='pass', min_value=16.0, max_value=28.0, score=60)
        FitnessStandard.objects.create(item=item, gender='male', level='fail', min_value=0, max_value=16.0, score=40)
        
        # 女生标准
        FitnessStandard.objects.create(item=item, gender='female', level='excellent', min_value=18.5, max_value=23.9, score=100)
        FitnessStandard.objects.create(item=item, gender='female', level='good', min_value=17.0, max_value=25.0, score=85)
        FitnessStandard.objects.create(item=item, gender='female', level='pass', min_value=16.0, max_value=28.0, score=60)
        FitnessStandard.objects.create(item=item, gender='female', level='fail', min_value=0, max_value=16.0, score=40)
    elif item.name == '肺活量':
        # 男生肺活量标准
        FitnessStandard.objects.create(item=item, gender='male', level='excellent', min_value=4000, max_value=None, score=100)
        FitnessStandard.objects.create(item=item, gender='male', level='good', min_value=3500, max_value=4000, score=85)
        FitnessStandard.objects.create(item=item, gender='male', level='pass', min_value=3000, max_value=3500, score=60)
        FitnessStandard.objects.create(item=item, gender='male', level='fail', min_value=0, max_value=3000, score=40)
        
        # 女生肺活量标准
        FitnessStandard.objects.create(item=item, gender='female', level='excellent', min_value=3000, max_value=None, score=100)
        FitnessStandard.objects.create(item=item, gender='female', level='good', min_value=2500, max_value=3000, score=85)
        FitnessStandard.objects.create(item=item, gender='female', level='pass', min_value=2000, max_value=2500, score=60)
        FitnessStandard.objects.create(item=item, gender='female', level='fail', min_value=0, max_value=2000, score=40)
    elif item.name == '立定跳远':
        # 男生标准
        FitnessStandard.objects.create(item=item, gender='male', level='excellent', min_value=250, max_value=None, score=100)
        FitnessStandard.objects.create(item=item, gender='male', level='good', min_value=230, max_value=250, score=85)
        FitnessStandard.objects.create(item=item, gender='male', level='pass', min_value=210, max_value=230, score=60)
        FitnessStandard.objects.create(item=item, gender='male', level='fail', min_value=0, max_value=210, score=40)
        
        # 女生标准
        FitnessStandard.objects.create(item=item, gender='female', level='excellent', min_value=200, max_value=None, score=100)
        FitnessStandard.objects.create(item=item, gender='female', level='good', min_value=180, max_value=200, score=85)
        FitnessStandard.objects.create(item=item, gender='female', level='pass', min_value=160, max_value=180, score=60)
        FitnessStandard.objects.create(item=item, gender='female', level='fail', min_value=0, max_value=160, score=40)
    
    print(f"  为{item.name}创建了评分标准")

def create_fitness_tips(item):
    """为体测项目创建建议"""
    if item.name == '身高体重':
        FitnessTip.objects.create(
            item=item, 
            level='excellent', 
            tip_content='您的BMI指数处于理想范围内，身材健康。',
            improvement_methods='保持健康饮食和适量运动，维持当前体型。'
        )
        FitnessTip.objects.create(
            item=item, 
            level='good', 
            tip_content='您的BMI指数基本正常，但有小幅偏离理想范围。',
            improvement_methods='调整饮食结构，增加蔬果摄入，保持每周3-4次有氧运动。'
        )
        FitnessTip.objects.create(
            item=item, 
            level='pass', 
            tip_content='您的BMI指数偏离正常范围，可能存在体重不足或超重的情况。',
            improvement_methods='建议咨询营养师制定饮食计划，体重过低者增加优质蛋白质摄入，体重过高者控制热量摄入并增加运动量。'
        )
        FitnessTip.objects.create(
            item=item, 
            level='fail', 
            tip_content='您的BMI指数严重异常，可能存在健康风险。',
            improvement_methods='建议尽快就医检查，在专业医生指导下调整饮食和运动习惯。严重超重者应进行针对性的减重计划，严重体重不足者需增加营养摄入。'
        )
    elif item.name == '肺活量':
        FitnessTip.objects.create(
            item=item, 
            level='excellent', 
            tip_content='您的肺活量表现优秀，呼吸系统功能强健。',
            improvement_methods='继续保持有氧运动习惯，如跑步、游泳等，让肺部得到充分锻炼。'
        )
        FitnessTip.objects.create(
            item=item, 
            level='good', 
            tip_content='您的肺活量良好，呼吸系统功能正常。',
            improvement_methods='建议增加高强度间歇训练和呼吸训练，如深呼吸练习，可进一步提高肺活量。'
        )
        FitnessTip.objects.create(
            item=item, 
            level='pass', 
            tip_content='您的肺活量达到及格标准，但仍有较大提升空间。',
            improvement_methods='建议每周进行3-4次有氧运动，每次30分钟以上，并注意进行深呼吸练习。避免吸烟和待在空气污染环境中。'
        )
        FitnessTip.objects.create(
            item=item, 
            level='fail', 
            tip_content='您的肺活量较低，呼吸系统功能可能存在问题。',
            improvement_methods='建议检查是否有呼吸系统疾病；开始进行循序渐进的有氧训练，如散步、慢跑等，并逐渐增加强度；学习腹式呼吸法，每天进行5-10分钟的深呼吸练习。'
        )
    
    print(f"  为{item.name}创建了改进建议")

def create_news():
    """创建新闻公告数据"""
    if News.objects.count() > 0:
        print("新闻公告已存在，跳过创建")
        return News.objects.all()
    
    admin_user = User.objects.filter(is_superuser=True).first()
    
    news_items = [
        {
            'title': '2025年大学生体质测试即将开始',
            'content': '根据教育部体育卫生与艺术教育司要求，我校2025年春季体质测试工作将于4月1日正式开始。\n\n本次测试将覆盖全校所有在校学生，包括本科生和研究生，请各学院和班级做好准备工作。\n\n测试项目包括：身高体重、肺活量、立定跳远、坐位体前屈、仰卧起坐（女）/引体向上（男）、50米跑、800米跑（女）/1000米跑（男）等。\n\n请各位同学提前做好准备，保持良好的身体状态迎接测试。',
            'author': admin_user,
            'news_type': 'notice', 
            'is_published': True,
            'views': 1283,
            'cover_image': None,
            'is_pinned': True,
        },
        {
            'title': '体育锻炼方法与技巧分享会',
            'content': '为帮助同学们提高体育成绩，体育教研室将于本月15日下午2点在体育馆多功能厅举办"体育锻炼方法与技巧"分享会。\n\n内容包括：\n1. 各项体测项目的训练方法\n2. 提高成绩的有效技巧\n3. 常见问题解答\n\n欢迎所有同学参加，特别是往年体测成绩不理想的同学。',
            'author': admin_user,
            'news_type': 'article',
            'is_published': True,
            'views': 756,
            'cover_image': None,
            'is_pinned': False,
        },
        {
            'title': '关于体质测试成绩评定标准的说明',
            'content': '根据《国家学生体质健康标准》，我校体质测试成绩评定标准如下：\n\n优秀：总分≥90分\n良好：总分75-89分\n及格：总分60-74分\n不及格：总分<60分\n\n体测成绩将计入学生综合素质评价，并与评优评先、奖学金评定等挂钩。请同学们重视体育锻炼，保持良好的身体素质。',
            'author': admin_user,
            'news_type': 'notice',
            'is_published': True,
            'views': 892,
            'cover_image': None,
            'is_pinned': False,
        },
    ]
    
    created_news = []
    for news_data in news_items:
        news = News.objects.create(**news_data)
        created_news.append(news)
        print(f"创建新闻: {news.title}")
        
        # 为第一条新闻添加评论
        if news == created_news[0]:
            # 获取一些用户
            students = User.objects.filter(user_type='student')[:3]
            
            # 检查教师用户是否已存在
            teacher_username = "teacher1"
            try:
                teacher = User.objects.get(username=teacher_username)
                print(f"  教师用户 {teacher_username} 已存在，使用现有用户")
            except User.DoesNotExist:
                teacher = User.objects.create_user(
                    username=teacher_username,
                    email=f"{teacher_username}@example.com",
                    password="password123",
                    first_name="李教练",
                    user_type='admin',
                    is_active=True
                )
                print(f"  创建教师用户: {teacher.username}")
            
            comments = []
            
            # 只有在有学生账号的情况下才添加学生评论
            if students:
                comments.append({
                    'news': news,
                    'user': students[0],
                    'content': '希望能出台一些针对体质较弱学生的帮扶措施。',
                    'status': 'approved',
                })
                
                if len(students) > 1:
                    comments.append({
                        'news': news,
                        'user': students[1],
                        'content': '请问测试当天如果生病了怎么办？可以延期吗？',
                        'status': 'approved',
                    })
            
            # 添加教师评论
            comments.append({
                'news': news,
                'user': teacher,
                'content': '同学们可以提前来操场做一些基础训练，我们会提供专业指导。',
                'status': 'approved',
            })
            
            for comment_data in comments:
                Comment.objects.create(**comment_data)
                print(f"  添加评论: {comment_data['content'][:20]}...")
    
    return created_news

def create_students():
    """创建学生数据"""
    if StudentInfo.objects.count() > 0:
        print("学生信息已存在，跳过创建")
        return StudentInfo.objects.all()
    
    # 学院列表
    colleges = ['计算机学院', '机械工程学院', '电子信息学院', '经济管理学院', '外国语学院']
    # 专业列表
    majors_by_college = {
        '计算机学院': ['计算机科学与技术', '软件工程', '人工智能', '数据科学与大数据技术'],
        '机械工程学院': ['机械设计制造及其自动化', '车辆工程', '工业设计', '机器人工程'],
        '电子信息学院': ['电子信息工程', '通信工程', '微电子科学与工程', '光电信息科学与工程'],
        '经济管理学院': ['工商管理', '市场营销', '会计学', '财务管理', '国际经济与贸易'],
        '外国语学院': ['英语', '日语', '德语', '法语', '翻译'],
    }
    
    # 年级
    grades = ['大一', '大二', '大三', '大四']
    
    # 创建学生用户和信息
    students_data = []
    for i in range(1, 51):  # 创建50个学生
        # 随机选择学院和专业
        college = random.choice(colleges)
        major = random.choice(majors_by_college[college])
        
        # 生成学号
        student_id = f"2025{str(i).zfill(4)}"
        
        # 随机性别
        gender = random.choice(['male', 'female'])
        
        # 随机年级
        grade = random.choice(grades)
        
        # 创建用户 - 检查用户是否已存在
        username = f"student{i}"
        try:
            user = User.objects.get(username=username)
            print(f"  学生用户 {username} 已存在，跳过创建")
            
            # 检查关联的学生信息是否存在
            try:
                student_info = StudentInfo.objects.get(user=user)
                print(f"  学生 {student_info.name} 已有详细信息，跳过创建")
                students_data.append(student_info)
                continue
            except StudentInfo.DoesNotExist:
                # 用户存在但没有学生信息，继续创建学生信息
                pass
        except User.DoesNotExist:
            # 创建新用户
            email = f"{username}@example.com"
            user = User.objects.create_user(
                username=username,
                email=email,
                password="password123",  # 设置默认密码
                first_name=f"学生{i}",
                user_type='student',
                is_active=True
            )
        
        # 随机身高体重
        height = random.randint(155, 190)
        weight = random.randint(45, 85)
        
        # 随机生日（20-25岁）
        years_ago = random.randint(20, 25)
        days_vary = random.randint(-180, 180)
        birth_date = timezone.now() - timedelta(days=365*years_ago + days_vary)
        
        # 创建学生信息
        student_info = StudentInfo.objects.create(
            user=user,
            name=f"学生{i}",
            student_id=student_id,
            gender=gender,
            birth_date=birth_date,
            height=height,
            weight=weight,
            college=college,
            major=major,
            class_name=f"{major}2025级{random.randint(1,3)}班",
            grade=grade,
        )
        
        students_data.append(student_info)
        print(f"创建学生: {student_info.name} ({student_id})")
    
    return students_data

def create_exams():
    """创建考试安排数据"""
    if Exam.objects.count() > 0:
        print("考试安排已存在，跳过创建")
        return Exam.objects.all()
    
    fitness_items = list(FitnessItem.objects.all())
    if not fitness_items:
        print("没有体测项目数据，无法创建考试安排")
        return []
    
    # 创建普通考试
    regular_exam = Exam.objects.create(
        title="2025年春季体质测试",
        description="本次测试为2025年春季学期常规体质测试，所有在校学生必须参加。",
        start_date=timezone.now().date() + timedelta(days=15),
        end_date=timezone.now().date() + timedelta(days=25),
        status="upcoming",
        is_makeup=False
    )
    
    # 创建补考
    makeup_exam = Exam.objects.create(
        title="2025年春季体质测试补考",
        description="针对春季学期常规体测缺考或不及格的学生进行的补测。",
        start_date=timezone.now().date() + timedelta(days=60),
        end_date=timezone.now().date() + timedelta(days=62),
        status="upcoming",
        is_makeup=True
    )
    
    exams = [regular_exam, makeup_exam]
    
    # 为每个考试创建考试项目
    for exam in exams:
        for item in fitness_items:
            # 随机分配日期和时间
            days_offset = random.randint(0, (exam.end_date - exam.start_date).days)
            exam_date = exam.start_date + timedelta(days=days_offset)
            
            # 上午或下午
            if random.choice([True, False]):
                start_time = datetime.strptime("08:30", "%H:%M").time()
                end_time = datetime.strptime("11:30", "%H:%M").time()
            else:
                start_time = datetime.strptime("14:00", "%H:%M").time()
                end_time = datetime.strptime("17:00", "%H:%M").time()
            
            # 分配地点
            locations = ["田径场", "体育馆", "测试中心", "综合体育场"]
            location = random.choice(locations)
            
            # 分配考官
            examiners = ["张教练", "李教练", "王老师", "赵老师", "体育教研室"]
            examiner = random.choice(examiners)
            
            # 创建考试项目
            ExamItem.objects.create(
                exam=exam,
                fitness_item=item,
                exam_date=exam_date,
                start_time=start_time,
                end_time=end_time,
                location=location,
                examiner=examiner,
                notes=f"{item.name}测试注意事项：请穿着运动服装和运动鞋参加。"
            )
            
        print(f"创建考试: {exam.title}，包含{len(fitness_items)}个测试项目")
    
    return exams

if __name__ == "__main__":
    print("开始创建测试数据...")
    
    # 创建体测项目
    fitness_items = create_fitness_items()
    
    # 创建新闻公告
    news = create_news()
    
    # 创建学生数据
    students = create_students()
    
    # 创建考试安排
    exams = create_exams()
    
    print("测试数据创建完成！")
