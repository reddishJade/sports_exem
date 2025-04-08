"""
新闻数据生成模块 - 创建新闻、通知和公告
"""
import random
from django.utils import timezone
from datetime import timedelta, datetime
from fitness.models import SportsNews

def create_news(admin_users, minimal=False):
    """
    创建新闻和公告数据
    
    参数:
        admin_users: 管理员用户列表（用作新闻作者）
        minimal: 是否仅创建最少量的数据
    
    返回:
        创建的新闻列表
    """
    # 检查是否已存在
    existing_news = SportsNews.objects.all()
    if existing_news.exists():
        print(f"  已存在 {existing_news.count()} 条新闻，使用现有数据")
        return list(existing_news)
    
    news_items = []
    
    # 决定创建多少条新闻
    if minimal:
        news_count = 5  # 最少创建5条新闻
    else:
        news_count = 20  # 创建20条新闻
    
    # 新闻标题模板
    news_titles = [
        "全国大学生体育锦标赛在北京举行，我校获得{0}项冠军",
        "国家体育总局发布最新体质测试标准，关注青少年体质健康",
        "体育部召开会议，强调提高学生体质健康水平的重要性",
        "我校{0}项目在全国大学生运动会上获得佳绩",
        "校园体育文化节开幕，丰富多彩的活动迎接新学期",
        "冬季体育锻炼指南：如何在寒冷天气保持运动习惯",
        "体测数据分析：我校学生体质呈{0}趋势",
        "校运会圆满结束，{0}班级获得团体总分第一",
        "专家讲座：科学健身与营养搭配的重要性",
        "体育健儿风采展：记录校园体育明星的故事",
        "学校增设新的体育课程，丰富学生体育活动选择",
        "夏季运动会预告：多项新增比赛项目等你来挑战",
        "健康生活方式调查：超过{0}%的学生每周运动不足3小时",
        "体育教学改革动态：强调趣味性和实用性相结合",
        "校园健步走活动启动，鼓励师生每日万步走",
        "体测成绩优秀者表彰大会，弘扬健康向上的校园风尚",
        "国际体育交流活动：我校代表队访问{0}大学",
        "体育与学术的平衡：如何在紧张学习中保持运动习惯",
        "校园体育设施更新改造工程正式启动",
        "体育特长生招生政策解读，多维度考核综合素质",
        "健康知识竞赛开始报名，丰厚奖品等你来赢",
        "新学期体育课程安排出炉，新增多个热门项目",
        "体质健康监测系统上线，实时跟踪学生健康状况",
        "校园马拉松活动预告：挑战自我，超越极限",
        "体育部发布《学生体质健康白皮书》，数据详实令人关注"
    ]
    
    # 新闻详情模板
    news_content_template = """
    {title}
    
    发布时间：{date}
    
    {intro}
    
    {detail}
    
    {quote}
    
    {summary}
    
    {call_to_action}
    """
    
    # 新闻来源
    news_sources = [
        "校体育部官网", "教育部体卫艺司", "国家体育总局", "校新闻网", 
        "中国大学生体育协会", "体育科学研究所", "校学生会", "全国学联"
    ]
    
    # 新闻图片URL（示例）
    image_urls = [
        "https://example.com/sports/image1.jpg",
        "https://example.com/sports/image2.jpg",
        "https://example.com/sports/image3.jpg",
        "https://example.com/sports/image4.jpg",
        "https://example.com/sports/image5.jpg"
    ]
    
    # 新闻关键词
    keywords_list = [
        "体育,健康,测试", 
        "体质,标准,学生", 
        "运动会,比赛,奖项", 
        "健身,锻炼,科学", 
        "体育课程,改革,创新",
        "校园,活动,文化",
        "测试,数据,分析",
        "冬季,运动,指南",
        "夏季,比赛,预告",
        "健康,生活方式,调查"
    ]
    
    # 创建新闻
    for i in range(news_count):
        # 标题处理 - 替换占位符
        title_template = random.choice(news_titles)
        if "{0}" in title_template:
            if "项目" in title_template:
                placeholder = random.choice(["足球", "篮球", "排球", "田径", "游泳", "乒乓球"])
            elif "班级" in title_template:
                placeholder = random.choice(["计算机科学", "电子工程", "机械工程", "经济管理", "外国语", "医学"])
            elif "趋势" in title_template:
                placeholder = random.choice(["上升", "稳定", "不均衡", "显著提高", "两极分化"])
            elif "大学" in title_template:
                placeholder = random.choice(["哈佛", "牛津", "东京", "首尔", "悉尼", "多伦多"])
            elif "%" in title_template:
                placeholder = str(random.randint(40, 75))
            else:
                placeholder = str(random.randint(1, 5))
            
            title = title_template.format(placeholder)
        else:
            title = title_template
        
        # 创建时间 - 过去3个月内随机时间
        days_ago = random.randint(0, 90)
        pub_date = timezone.now() - timedelta(days=days_ago)
        
        # 随机选择来源
        source_name = random.choice(news_sources)
        source_url = f"https://example.com/{source_name.lower().replace(' ', '_')}"
        
        # 随机选择图片
        featured_image = random.choice(image_urls)
        
        # 随机选择关键词
        keywords = random.choice(keywords_list)
        
        # 新闻状态
        status = 'published'
        
        # 是否置顶（只有少数新闻是置顶的）
        is_featured = (i < 3)  # 前3条新闻置顶
        
        # 浏览次数
        views = random.randint(100, 10000)
        
        # 创建内容段落
        intro = f"近日，{random.choice(['我校', '教育部', '体育总局', '校体育部'])}发布了关于{title.split('，')[0]}的最新消息。这一消息引起了广泛关注。"
        
        detail = "\n\n".join([
            f"根据{source_name}的消息，此次{title.split('，')[0]}活动得到了{random.choice(['校领导', '学生', '老师', '社会各界'])}的广泛支持。",
            f"活动期间，{random.choice(['参与人数超过1000人', '展示了丰富多彩的体育项目', '发布了最新的体育教学成果', '展现了当代大学生的蓬勃朝气'])}。",
            f"本次活动的主题是\"{random.choice(['健康中国，活力校园', '强身健体，立德树人', '科学健身，快乐生活', '体育强国，青春力量'])}\",旨在{random.choice(['提高学生体质健康水平', '培养学生终身体育锻炼意识', '促进校园体育文化建设', '发现和培养体育特长学生'])}。"
        ])
        
        quote = f"""{random.choice(['校体育部负责人', '参与学生', '专业教师', '体育教研室主任'])}表示："这次{title.split('，')[0]}对于{random.choice(['提高学生体质', '丰富校园文化生活', '促进学生全面发展', '落实立德树人根本任务'])}具有重要意义。\""""
        
        summary = f"总之，此次{title.split('，')[0]}活动{random.choice(['取得了圆满成功', '受到了广泛好评', '达到了预期目标', '开创了新的局面'])}，为{random.choice(['今后类似活动的开展', '校园体育文化建设', '学生体质健康提升', '体育教学改革'])}积累了宝贵经验。"
        
        call_to_action = f"欢迎广大{random.choice(['学生', '师生', '体育爱好者', '校友'])}继续关注相关活动，{random.choice(['踊跃参与', '提出宝贵意见', '共同建设健康校园', '为校体育事业发展贡献力量'])}。"
        
        # 组合完整内容
        content = news_content_template.format(
            title=title,
            date=pub_date.strftime("%Y年%m月%d日 %H:%M"),
            intro=intro,
            detail=detail,
            quote=quote,
            summary=summary,
            call_to_action=call_to_action
        )
        
        # 选择作者（管理员）
        author = random.choice(admin_users)
        
        # 创建新闻对象
        news = SportsNews.objects.create(
            title=title,
            content=content,
            source_url=source_url,
            source_name=source_name,
            featured_image=featured_image,
            status=status,
            views=views,
            keywords=keywords,
            is_featured=is_featured
        )
        
        news_items.append(news)
        print(f"  创建新闻: {news.title}")
    
    return news_items
