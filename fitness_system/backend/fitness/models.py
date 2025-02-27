from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', '学生'),
        ('parent', '家长'),
        ('admin', '管理员'),
    )
    
    user_type = models.CharField('用户类型', max_length=10, choices=USER_TYPE_CHOICES)
    phone = models.CharField('手机号码', max_length=15, blank=True)
    
    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = '用户管理'

class Student(models.Model):
    GENDER_CHOICES = (
        ('M', '男'),
        ('F', '女'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', verbose_name='用户账号')
    student_id = models.CharField('学号', max_length=20, unique=True)
    name = models.CharField('姓名', max_length=50)
    gender = models.CharField('性别', max_length=1, choices=GENDER_CHOICES, default='M')
    class_name = models.CharField('班级', max_length=50)
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='children', verbose_name='家长账号')

    class Meta:
        db_table = 'student'
        verbose_name = '学生'
        verbose_name_plural = '学生管理'

    def __str__(self):
        return f'{self.name} ({self.student_id})'

class PhysicalStandard(models.Model):
    GENDER_CHOICES = (
        ('M', '男'),
        ('F', '女'),
    )
    
    gender = models.CharField('性别', max_length=1, choices=GENDER_CHOICES)
    bmi_min = models.FloatField('BMI最小值')
    bmi_max = models.FloatField('BMI最大值')
    vital_capacity_excellent = models.IntegerField('肺活量优秀标准(ml)')
    run_50m_excellent = models.FloatField('50米跑优秀标准(秒)')
    sit_and_reach_excellent = models.IntegerField('坐位体前屈优秀标准(cm)')
    standing_jump_excellent = models.IntegerField('立定跳远优秀标准(cm)')
    run_800m_excellent = models.IntegerField('800米跑优秀标准(秒)')
    vital_capacity_pass = models.IntegerField('肺活量及格标准(ml)', default=2000)
    run_50m_pass = models.FloatField('50米跑及格标准(秒)', default=9.0)
    sit_and_reach_pass = models.IntegerField('坐位体前屈及格标准(cm)', default=10)
    standing_jump_pass = models.IntegerField('立定跳远及格标准(cm)', default=180)
    run_800m_pass = models.IntegerField('800米跑及格标准(秒)', default=240)

    class Meta:
        db_table = 'physical_standard'
        verbose_name = '体测标准'
        verbose_name_plural = '体测标准管理'

    def __str__(self):
        return f'{self.get_gender_display()}生体测标准'

class TestPlan(models.Model):
    PLAN_TYPE_CHOICES = (
        ('regular', '常规测试'),
        ('makeup', '补考测试'),
    )

    title = models.CharField('标题', max_length=100)
    test_date = models.DateTimeField('测试日期')
    location = models.CharField('测试地点', max_length=200)
    description = models.TextField('测试说明')
    plan_type = models.CharField('计划类型', max_length=10, choices=PLAN_TYPE_CHOICES, default='regular')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'test_plan'
        verbose_name = '测试计划'
        verbose_name_plural = '测试计划管理'

    def __str__(self):
        return self.title

class TestResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='学生')
    test_plan = models.ForeignKey(TestPlan, on_delete=models.CASCADE, verbose_name='测试计划')
    bmi = models.FloatField('BMI指数')
    vital_capacity = models.IntegerField('肺活量(ml)')
    run_50m = models.FloatField('50米跑(秒)')
    sit_and_reach = models.IntegerField('坐位体前屈(cm)')
    standing_jump = models.IntegerField('立定跳远(cm)')
    run_800m = models.IntegerField('800米跑(秒)')
    total_score = models.IntegerField('总分')
    test_date = models.DateTimeField('测试时间', auto_now_add=True)
    is_makeup = models.BooleanField('是否补测', default=False)

    class Meta:
        db_table = 'test_result'
        verbose_name = '测试成绩'
        verbose_name_plural = '测试成绩管理'

    def __str__(self):
        return f'{self.student.name}的{self.test_plan.title}成绩'

    @property
    def is_passed(self):
        """判断是否及格"""
        # 获取对应性别的体测标准
        standard = PhysicalStandard.objects.get(gender=self.student.gender)
        
        # 检查每个项目是否达到及格标准
        passed_items = [
            self.vital_capacity >= standard.vital_capacity_pass,
            self.run_50m <= standard.run_50m_pass,  # 跑步项目时间越短越好
            self.sit_and_reach >= standard.sit_and_reach_pass,
            self.standing_jump >= standard.standing_jump_pass,
            self.run_800m <= standard.run_800m_pass,  # 跑步项目时间越短越好
        ]
        
        # 总分及格线为60分
        return self.total_score >= 60 and all(passed_items)

class Comment(models.Model):
    test_result = models.ForeignKey(TestResult, on_delete=models.CASCADE, verbose_name='测试成绩')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='学生')
    content = models.TextField('评论内容')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    is_approved = models.BooleanField('是否批准', default=False)

    class Meta:
        db_table = 'comment'
        verbose_name = '评论'
        verbose_name_plural = '评论管理'

    def __str__(self):
        return f'{self.student.name}的评论'

class HealthReport(models.Model):
    test_result = models.OneToOneField(TestResult, on_delete=models.CASCADE, verbose_name='测试成绩')
    overall_assessment = models.TextField('总体评估')
    health_suggestions = models.TextField('健康建议')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'health_report'
        verbose_name = '健康报告'
        verbose_name_plural = '健康报告管理'

    def __str__(self):
        return f'{self.test_result.student.name}的健康报告'

class MakeupNotification(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='学生')
    test_plan = models.ForeignKey(TestPlan, on_delete=models.CASCADE, verbose_name='补考计划')
    original_result = models.ForeignKey(TestResult, on_delete=models.CASCADE, verbose_name='原始成绩')
    is_read = models.BooleanField('是否已读', default=False)
    sent_at = models.DateTimeField('发送时间', auto_now_add=True)

    class Meta:
        db_table = 'makeup_notification'
        verbose_name = '补考通知'
        verbose_name_plural = '补考通知管理'

    def __str__(self):
        return f'{self.student.name}的{self.test_plan.title}补考通知'

@receiver(post_save, sender=TestResult)
def create_makeup_notification(sender, instance, created, **kwargs):
    """当保存测试结果时，如果不及格且不是补考，则自动创建补考通知"""
    if created and not instance.is_passed and not instance.is_makeup:
        # 创建补考计划
        makeup_plan = TestPlan.objects.create(
            title=f'{instance.test_plan.title}补考',
            test_date=instance.test_date + timedelta(days=14),  # 两周后补考
            location=instance.test_plan.location,
            description=f'补考测试 - 原测试：{instance.test_plan.title}',
            plan_type='makeup'
        )
        
        # 创建补考通知
        MakeupNotification.objects.create(
            student=instance.student,
            test_plan=makeup_plan,
            original_result=instance
        )
