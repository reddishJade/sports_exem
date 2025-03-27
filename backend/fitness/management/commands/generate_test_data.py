import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from fitness.models import (
    User, Student, PhysicalStandard, TestPlan, TestResult, 
    Comment, HealthReport, MakeupNotification, SportsNews, NewsComment
)

class Command(BaseCommand):
    help = '生成全面的测试数据'

    def handle(self, *args, **kwargs):
        self.stdout.write('开始生成测试数据...')
        
        # 使用事务包装所有数据库操作，如果出错可以回滚
        with transaction.atomic():
            self.create_users()
            self.create_students()
            self.create_physical_standards()
            self.create_test_plans()
            self.create_test_results()
            self.create_comments()
            self.create_health_reports()
            self.create_makeup_notifications()
            self.create_sports_news()
            # 跳过创建新闻评论，避免数据库结构不一致问题
            # self.create_news_comments()
            
        self.stdout.write(self.style.SUCCESS('测试数据生成完成!'))
    
    def create_users(self):
        self.stdout.write('创建用户...')
        
        # 创建管理员用户
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                user_type='admin',
                phone='13800000000'
            )
        
        # 创建学生用户
        for i in range(1, 21):
            if not User.objects.filter(username=f'student{i}').exists():
                User.objects.create_user(
                    username=f'student{i}',
                    email=f'student{i}@example.com',
                    password='student123',
                    user_type='student',
                    phone=f'138{i:08d}'
                )
        
        # 创建家长用户
        for i in range(1, 11):
            if not User.objects.filter(username=f'parent{i}').exists():
                User.objects.create_user(
                    username=f'parent{i}',
                    email=f'parent{i}@example.com',
                    password='parent123',
                    user_type='parent',
                    phone=f'139{i:08d}'
                )
    
    def create_students(self):
        self.stdout.write('创建学生信息...')
        
        # 获取所有学生用户和家长用户
        student_users = User.objects.filter(user_type='student')
        parent_users = User.objects.filter(user_type='parent')
        
        # 为每个学生用户创建学生信息
        for i, user in enumerate(student_users):
            # 如果学生记录已经存在，则跳过
            if Student.objects.filter(user=user).exists():
                continue
            
            # 为学生分配一个家长
            parent = parent_users[i % len(parent_users)]
            
            gender = 'M' if i % 2 == 0 else 'F'
            grade = ['大一', '大二', '大三', '大四'][i % 4]
            class_name = f'{grade}-{(i % 6) + 1}班'
            
            Student.objects.create(
                user=user,
                student_id=f'2023{i+1:04d}',
                name=f'学生{i+1}',
                gender=gender,
                class_name=class_name,
                parent=parent
            )
    
    def create_physical_standards(self):
        self.stdout.write('创建体测标准...')
        
        # 如果已经有体测标准，则跳过
        if PhysicalStandard.objects.exists():
            return
        
        # 男生标准
        PhysicalStandard.objects.create(
            gender='M',
            bmi_min=18.5,
            bmi_max=24.9,
            vital_capacity_excellent=4000,
            run_50m_excellent=7.0,
            sit_and_reach_excellent=20,
            standing_jump_excellent=230,
            run_800m_excellent=180,
            vital_capacity_pass=3000,
            run_50m_pass=8.0,
            sit_and_reach_pass=10,
            standing_jump_pass=200,
            run_800m_pass=200
        )
        
        # 女生标准
        PhysicalStandard.objects.create(
            gender='F',
            bmi_min=18.0,
            bmi_max=24.0,
            vital_capacity_excellent=3000,
            run_50m_excellent=8.0,
            sit_and_reach_excellent=25,
            standing_jump_excellent=180,
            run_800m_excellent=210,
            vital_capacity_pass=2500,
            run_50m_pass=9.0,
            sit_and_reach_pass=15,
            standing_jump_pass=150,
            run_800m_pass=240
        )
    
    def create_test_plans(self):
        self.stdout.write('创建测试计划...')
        
        # 如果已经有测试计划，则跳过
        if TestPlan.objects.exists():
            return
        
        # 常规测试
        for i in range(1, 4):
            month = i * 3
            test_date = timezone.make_aware(datetime(2025, month, 15, 9, 0))
            
            TestPlan.objects.create(
                title=f'2025年第{i}学期体质测试',
                test_date=test_date,
                location='体育中心',
                description=f'本次测试包括：身高体重、肺活量、50米跑、坐位体前屈、立定跳远和800米跑。请穿运动服装参加。',
                plan_type='regular'
            )
        
        # 补考测试
        for i in range(1, 3):
            month = i * 6
            test_date = timezone.make_aware(datetime(2025, month, 25, 14, 0))
            
            TestPlan.objects.create(
                title=f'2025年第{i}学期体质测试补考',
                test_date=test_date,
                location='田径场',
                description=f'本次补考仅针对前次测试未通过的学生，请务必准时参加。',
                plan_type='makeup'
            )
    
    def create_test_results(self):
        self.stdout.write('创建测试结果...')
        
        students = Student.objects.all()
        test_plans = TestPlan.objects.filter(plan_type='regular')
        standards = {
            'M': PhysicalStandard.objects.get(gender='M'),
            'F': PhysicalStandard.objects.get(gender='F')
        }
        
        # 为每个学生创建常规测试结果
        for student in students:
            for plan in test_plans:
                # 避免重复创建
                if TestResult.objects.filter(student=student, test_plan=plan).exists():
                    continue
                
                standard = standards[student.gender]
                
                # 随机决定是否及格
                pass_test = random.random() > 0.2  # 80%几率及格
                
                # 根据标准和及格与否生成测试结果
                vital_capacity = random.randint(
                    standard.vital_capacity_pass if pass_test else standard.vital_capacity_pass - 500,
                    standard.vital_capacity_excellent + 500
                )
                
                run_50m = round(random.uniform(
                    standard.run_50m_excellent - 0.5,
                    standard.run_50m_pass if pass_test else standard.run_50m_pass + 1.0
                ), 1)
                
                sit_and_reach = random.randint(
                    standard.sit_and_reach_pass if pass_test else standard.sit_and_reach_pass - 5,
                    standard.sit_and_reach_excellent + 5
                )
                
                standing_jump = random.randint(
                    standard.standing_jump_pass if pass_test else standard.standing_jump_pass - 20,
                    standard.standing_jump_excellent + 20
                )
                
                run_800m = random.randint(
                    standard.run_800m_excellent - 10,
                    standard.run_800m_pass if pass_test else standard.run_800m_pass + 30
                )
                
                # 计算BMI指数（因为TestResult只有BMI而没有height和weight字段）
                height = random.randint(160, 190)
                weight = random.randint(50, 80)
                bmi = round(weight / ((height / 100) ** 2), 1)
                
                # 计算总分
                score = 0
                if standard.bmi_min <= bmi <= standard.bmi_max:
                    score += 20
                
                if vital_capacity >= standard.vital_capacity_pass:
                    score += 16
                
                if run_50m <= standard.run_50m_pass:
                    score += 16
                
                if sit_and_reach >= standard.sit_and_reach_pass:
                    score += 16
                
                if standing_jump >= standard.standing_jump_pass:
                    score += 16
                
                if run_800m <= standard.run_800m_pass:
                    score += 16
                
                # 创建测试结果
                TestResult.objects.create(
                    student=student,
                    test_plan=plan,
                    bmi=bmi,
                    vital_capacity=vital_capacity,
                    run_50m=run_50m,
                    sit_and_reach=sit_and_reach,
                    standing_jump=standing_jump,
                    run_800m=run_800m,
                    total_score=score,
                    is_makeup=False
                )
    
    def generate_random_comment(self, score):
        if score >= 90:
            comments = [
                "表现优异，继续保持!",
                "各项指标均处于优秀水平，值得肯定!",
                "身体素质非常好，请继续保持良好的锻炼习惯!"
            ]
        elif score >= 80:
            comments = [
                "整体表现良好，可适当增加耐力训练!",
                "基础体能良好，建议增加柔韧性训练!",
                "各项指标平衡发展，继续努力!"
            ]
        elif score >= 60:
            comments = [
                "达到基本要求，需增加日常锻炼!",
                "部分项目有待提高，建议专项训练!",
                "身体素质尚可，但仍需坚持锻炼!"
            ]
        else:
            comments = [
                "未达到基本要求，需要参加补考!",
                "体能状况较差，建议加强体育锻炼!",
                "多项指标未达标，请注意身体健康!"
            ]
        
        return random.choice(comments)
    
    def create_comments(self):
        self.stdout.write('创建学生评论...')
        
        # 获取所有测试结果
        test_results = TestResult.objects.all()
        
        for result in test_results:
            # 30%几率添加评论
            if random.random() > 0.7:
                continue
            
            # 避免重复创建
            if Comment.objects.filter(test_result=result).exists():
                continue
            
            comments = [
                f"我对这次测试结果{['不太满意', '比较满意', '很满意'][random.randint(0, 2)]}。",
                f"这次测试我在{['50米跑', '肺活量', '坐位体前屈', '立定跳远', '800米跑'][random.randint(0, 4)]}项目上表现不错。",
                f"希望下次能在{['耐力', '速度', '力量', '柔韧性'][random.randint(0, 3)]}方面有所提高。",
                "我会继续努力，提高自己的体能水平。",
                "感谢老师的指导，我会坚持锻炼的！"
            ]
            
            content = random.choice(comments)
            is_approved = random.random() > 0.3  # 70%几率已审核
            
            Comment.objects.create(
                test_result=result,
                student=result.student,
                content=content,
                is_approved=is_approved
            )
    
    def create_health_reports(self):
        self.stdout.write('创建健康报告...')
        
        # 获取分数低于80的测试结果
        test_results = TestResult.objects.filter(total_score__lt=80)
        
        for result in test_results:
            # 避免重复创建
            if HealthReport.objects.filter(test_result=result).exists():
                continue
            
            # 50%几率创建健康报告
            if random.random() > 0.5:
                continue
            
            weak_items = []
            standard = PhysicalStandard.objects.get(gender=result.student.gender)
            
            if result.vital_capacity < standard.vital_capacity_pass:
                weak_items.append("肺活量")
            
            if result.run_50m > standard.run_50m_pass:
                weak_items.append("50米跑")
            
            if result.sit_and_reach < standard.sit_and_reach_pass:
                weak_items.append("坐位体前屈")
            
            if result.standing_jump < standard.standing_jump_pass:
                weak_items.append("立定跳远")
            
            if result.run_800m > standard.run_800m_pass:
                weak_items.append("800米跑")
            
            if not standard.bmi_min <= result.bmi <= standard.bmi_max:
                weak_items.append("BMI指数")
            
            if weak_items:
                weak_items_str = "、".join(weak_items)
                overall_assessment = f"根据本次体测结果，您在{weak_items_str}等项目上未达到标准要求。"
                
                suggestions = [
                    f"建议加强{['有氧', '力量', '柔韧性', '平衡性'][random.randint(0, 3)]}训练，每周至少3次，每次30分钟以上。",
                    f"注意合理饮食，增加蛋白质摄入，减少高糖高脂食品。",
                    f"保持规律作息，确保充足睡眠，减少熬夜。",
                    f"可以尝试{['慢跑', '游泳', '自行车', '健身', '瑜伽'][random.randint(0, 4)]}等运动方式，提高身体素质。"
                ]
                
                health_suggestions = " ".join(random.sample(suggestions, k=min(3, len(suggestions))))
                
                HealthReport.objects.create(
                    test_result=result,
                    overall_assessment=overall_assessment,
                    health_suggestions=health_suggestions
                )
    
    def create_makeup_notifications(self):
        self.stdout.write('创建补考通知...')
        
        # 获取分数低于60的测试结果和补考计划
        failed_results = TestResult.objects.filter(total_score__lt=60, is_makeup=False)
        makeup_plans = TestPlan.objects.filter(plan_type='makeup')
        
        if not makeup_plans.exists():
            self.stdout.write('没有补考计划，跳过创建补考通知')
            return
        
        for result in failed_results:
            # 避免重复创建
            if MakeupNotification.objects.filter(original_result=result).exists():
                continue
            
            # 分配最近的补考计划
            test_date = result.test_plan.test_date
            suitable_plans = makeup_plans.filter(test_date__gt=test_date).order_by('test_date')
            
            if suitable_plans.exists():
                makeup_plan = suitable_plans.first()
                
                MakeupNotification.objects.create(
                    student=result.student,
                    test_plan=makeup_plan,
                    original_result=result,
                    is_read=random.random() > 0.5  # 50%几率已读
                )
    
    def create_sports_news(self):
        self.stdout.write('创建体育新闻...')
        
        # 如果已经有新闻，则跳过
        if SportsNews.objects.exists():
            return
        
        news_titles = [
            "校运动会圆满结束，体育学院获团体冠军",
            "我校在全国大学生体育竞赛中获佳绩",
            "新学期体育课程改革，增设多项选修项目",
            "冬季锻炼指南：如何在寒冷天气保持运动习惯",
            "体质健康标准解析：大学生如何科学提高体能",
            "校内健身房设施更新，新增多项专业器材",
            "体育部举办教师培训，提升体育教学质量",
            "全民健身日活动报道：校园掀起运动热潮",
            "体育特长生招生政策调整，多项目纳入选拔范围",
            "体育与健康讲座系列：科学饮食与运动表现"
        ]
        
        news_content_template = """
        {title}
        
        发布日期：{date}
        
        近日，{event_description}。活动吸引了{participants}积极参与，现场氛围热烈。
        
        据{source}介绍，此次{event_type}旨在{purpose}，对于{benefit}具有重要意义。参与者纷纷表示，通过这次活动，不仅{personal_gain}，还{additional_benefit}。
        
        专家{expert}指出，定期参与体育活动可以{expert_advice}。对于大学生而言，保持良好的体质状况对学习和未来发展都有积极影响。
        
        学校体育部负责人表示，将继续举办类似活动，鼓励更多学生积极参与体育锻炼，提高身体素质。
        """
        
        event_descriptions = [
            "我校举办了一年一度的校运动会",
            "体育学院组织了大型体育文化节",
            "校内举行了健康生活方式宣传周活动",
            "学校进行了新一轮的体质健康测试",
            "我校代表队参加了省级大学生运动会"
        ]
        
        participants = [
            "全校师生",
            "各院系学生代表",
            "体育特长生和运动爱好者",
            "校内外体育专家和学生",
            "多名专业运动员和教练"
        ]
        
        sources = [
            "校体育部门负责人",
            "活动组织方",
            "体育学院院长",
            "学生会体育部",
            "校医院健康中心"
        ]
        
        event_types = [
            "活动",
            "比赛",
            "培训",
            "测试",
            "讲座"
        ]
        
        purposes = [
            "提高学生体质健康水平",
            "促进校园体育文化建设",
            "发掘体育人才",
            "普及科学健身知识",
            "培养学生终身体育意识"
        ]
        
        benefits = [
            "学生综合素质培养",
            "校园文化建设",
            "健康中国战略实施",
            "高校体育教育改革",
            "学生心理健康促进"
        ]
        
        personal_gains = [
            "增强了体质",
            "学到了专业知识",
            "结交了志同道合的朋友",
            "培养了团队合作精神",
            "提高了自信心"
        ]
        
        additional_benefits = [
            "加深了对体育精神的理解",
            "改变了以往不健康的生活习惯",
            "发现了自己的运动潜能",
            "体会到了运动的乐趣",
            "获得了放松身心的有效方式"
        ]
        
        experts = [
            "体育学教授王明",
            "运动医学专家李强",
            "知名体育教育家张华",
            "健康管理师刘芳",
            "体育心理学研究员赵阳"
        ]
        
        expert_advices = [
            "增强心肺功能，提高免疫力",
            "缓解学习压力，改善睡眠质量",
            "预防慢性疾病，保持理想体重",
            "培养毅力和自律能力",
            "促进大脑发育，提高学习效率"
        ]
        
        for i, title in enumerate(news_titles):
            # 创建发布日期，最近一个月内的随机日期
            days_ago = random.randint(1, 30)
            pub_date = timezone.now() - timedelta(days=days_ago)
            
            # 填充新闻内容模板
            content = news_content_template.format(
                title=title,
                date=pub_date.strftime('%Y年%m月%d日'),
                event_description=random.choice(event_descriptions),
                participants=random.choice(participants),
                source=random.choice(sources),
                event_type=random.choice(event_types),
                purpose=random.choice(purposes),
                benefit=random.choice(benefits),
                personal_gain=random.choice(personal_gains),
                additional_benefit=random.choice(additional_benefits),
                expert=random.choice(experts),
                expert_advice=random.choice(expert_advices)
            )
            
            # 创建新闻
            SportsNews.objects.create(
                title=title,
                content=content,
                source_name='校体育部',
                featured_image=f'https://picsum.photos/800/400?random={i+1}',  # 使用随机图片
                status='published',
                views=random.randint(50, 500),
                keywords='体育,健康,大学生,体质',
                is_featured=i < 3  # 前三条设为置顶
            )
    
    def create_news_comments(self):
        self.stdout.write('创建新闻评论...')
        
        # 获取所有学生和新闻
        students = Student.objects.all()
        news_items = SportsNews.objects.all()
        
        comments = [
            "这个活动很有意义，希望能继续举办!",
            "作为学生代表参加了这次活动，收获很大!",
            "文章内容很实用，学到了很多健身知识。",
            "期待下次能有更多类似的体育赛事!",
            "这些建议很专业，我会尝试按照这个方法锻炼。",
            "学校体育设施越来越好了，点赞!",
            "希望能增加更多的运动项目选择。",
            "这些专家的建议很有启发性。",
            "我们班已经组织同学一起参加了，效果很好!",
            "文章写得很详细，对我帮助很大。"
        ]
        
        # 为每条新闻创建2-5条评论
        for news in news_items:
            comment_count = random.randint(2, 5)
            random_students = random.sample(list(students), min(comment_count, len(students)))
            
            for i, student in enumerate(random_students):
                # 避免重复创建
                if NewsComment.objects.filter(news=news, student=student).exists():
                    continue
                
                content = random.choice(comments)
                is_approved = random.random() > 0.2  # 80%几率已审核
                
                # 创建评论
                NewsComment.objects.create(
                    news=news,
                    student=student,
                    content=content,
                    is_approved=is_approved,
                    created_at=timezone.now(),  # 明确设置created_at
                    updated_at=timezone.now()   # 添加updated_at字段
                )
