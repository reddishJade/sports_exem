"""
评论数据生成模块 - 为新闻和通知创建用户评论
"""
import random
from django.utils import timezone
from datetime import timedelta
from fitness.models import NewsComment, Student

def create_comments(news_items, student_users, minimal=False):
    """
    创建评论数据
    
    参数:
        news_items: 新闻列表
        student_users: 学生用户列表（只有学生类型用户才能创建评论）
        minimal: 是否仅创建最少量的数据
    
    返回:
        创建的评论列表
    """
    # 检查是否已存在
    existing_comments = NewsComment.objects.all()
    if existing_comments.exists():
        print(f"  已存在 {existing_comments.count()} 条评论，使用现有数据")
        return list(existing_comments)
    
    # 确定每条新闻的评论数量
    if minimal:
        comments_per_news = 2
    else:
        comments_per_news = random.randint(3, 8)
    
    comments = []
    
    # 评论内容模板
    comment_templates = [
        "这条通知很重要，感谢分享！",
        "什么时候公布具体考试时间？",
        "希望能有更多的体育活动机会。",
        "请问具体位置在哪里？",
        "这个活动很有意义，期待参加。",
        "有没有提供健身指导的服务？",
        "测试时间能不能改一下？和我的课程冲突了。",
        "去年参加过，收获很大。",
        "请问需要提前准备什么吗？",
        "希望能提供更详细的信息。",
        "谢谢老师们的辛勤工作！",
        "体育锻炼真的很重要，要坚持。",
        "测试标准今年有变化吗？",
        "这方面的知识很实用，谢谢分享。",
        "我们班同学都很期待这次活动。"
    ]
    
    # 为每条新闻创建评论
    for news in news_items:
        # 为这条新闻创建的评论数
        num_comments = random.randint(1, comments_per_news)
        
        # 随机选择发评论的学生
        commenters = random.sample(student_users, min(num_comments, len(student_users)))
        
        for i, user in enumerate(commenters):
            # 根据两模型认证结构，确保用户类型是学生
            if user.user_type != 'student':
                continue
                
            try:
                # 获取学生档案
                student = Student.objects.get(user=user)
            except Student.DoesNotExist:
                print(f"  跳过用户 {user.username} 的评论 - 没有关联的学生档案")
                continue
                
            # 在新闻发布时间之后的随机时间发布评论
            if hasattr(news, 'publish_date') and news.publish_date:
                days_after = random.randint(0, min(30, (timezone.now().date() - news.publish_date.date()).days))
                comment_date = news.publish_date + timedelta(days=days_after)
            elif hasattr(news, 'pub_date') and news.pub_date:
                days_after = random.randint(0, min(30, (timezone.now().date() - news.pub_date.date()).days))
                comment_date = news.pub_date + timedelta(days=days_after)
            else:
                days_ago = random.randint(0, 30)
                comment_date = timezone.now() - timedelta(days=days_ago)
            
            # 随机选择评论内容
            if i < len(comment_templates):
                content = comment_templates[i]
            else:
                content = random.choice(comment_templates)
            
            # 创建评论 - 使用NewsComment而不是Comment
            comment = NewsComment.objects.create(
                news=news,
                student=student,  # 关联学生档案而不是用户
                content=content,
                created_at=comment_date
            )
            
            comments.append(comment)
            print(f"  为新闻'{news.title}'创建评论: {content[:20]}...")
    
    return comments
