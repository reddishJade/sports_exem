# 体测管理系统后端技术文档

## 目录

1. [技术架构概述](#技术架构概述)
2. [数据模型设计](#数据模型设计)
3. [序列化器](#序列化器)
4. [API接口设计](#api接口设计)
5. [认证与权限控制](#认证与权限控制)
6. [数据关系与业务逻辑](#数据关系与业务逻辑)
7. [代码示例解析](#代码示例解析)

## 技术架构概述

本系统采用Django REST framework构建RESTful API，为前端提供数据服务。主要技术组件包括：

- **Django**: Python Web框架，提供ORM、中间件、认证等基础功能
- **Django REST framework**: 用于构建RESTful API的强大工具集
- **SQLite/MySQL**: 数据存储
- **JWT**: JSON Web Token用于用户认证

### 系统架构图

```
前端 <---> Django REST API <---> 数据库
            |
            v
        业务逻辑层
```

## 数据模型设计

系统核心数据模型及其关系如下：

### 用户认证模型

```python
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', '学生'),
        ('parent', '家长'),
        ('admin', '管理员'),
    )
    
    user_type = models.CharField('用户类型', max_length=10, choices=USER_TYPE_CHOICES)
    phone = models.CharField('手机号码', max_length=15, blank=True)
```

**说明**: 
- 继承自Django的AbstractUser，扩展了用户类型和电话字段
- 用户类型区分学生、家长和管理员，用于权限控制

### 学生模型

```python
class Student(models.Model):
    GENDER_CHOICES = (
        ('M', '男'),
        ('F', '女'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField('学号', max_length=20, unique=True)
    name = models.CharField('姓名', max_length=50)
    gender = models.CharField('性别', max_length=1, choices=GENDER_CHOICES, default='M')
    class_name = models.CharField('班级', max_length=50)
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='children')
```

**说明**:
- 与User模型通过OneToOneField关联，存储学生特有信息
- 使用related_name='student_profile'使得可以通过user.student_profile访问学生信息
- 与家长用户建立多对一关系，一个家长可以关联多个学生

### 体测标准模型

```python
class PhysicalStandard(models.Model):
    gender = models.CharField('性别', max_length=1, choices=GENDER_CHOICES)
    bmi_min = models.FloatField('BMI最小值')
    bmi_max = models.FloatField('BMI最大值')
    vital_capacity_excellent = models.IntegerField('肺活量优秀标准(ml)')
    run_50m_excellent = models.FloatField('50米跑优秀标准(秒)')
    # 其他字段略...
```

**说明**:
- 按性别存储不同的体测标准
- 包含优秀和及格两档标准

### 测试计划模型

```python
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
```

**说明**:
- 记录体测活动信息，包括常规测试和补考测试

### 测试结果模型

```python
class TestResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    test_plan = models.ForeignKey(TestPlan, on_delete=models.CASCADE)
    bmi = models.FloatField('BMI指数')
    vital_capacity = models.IntegerField('肺活量(ml)')
    run_50m = models.FloatField('50米跑(秒)')
    # 其他测试项目略...
    total_score = models.IntegerField('总分')
    is_makeup = models.BooleanField('是否补测', default=False)
    
    @property
    def is_passed(self):
        """判断是否及格"""
        # 获取对应性别的体测标准
        standard = PhysicalStandard.objects.get(gender=self.student.gender)
        
        # 检查每个项目是否达到及格标准
        passed_items = [
            self.vital_capacity >= standard.vital_capacity_pass,
            self.run_50m <= standard.run_50m_pass,  # 跑步项目时间越短越好
            # 其他项目略...
        ]
        
        # 总分及格线为60分
        return self.total_score >= 60 and all(passed_items)
```

**说明**:
- 关联学生和测试计划
- 存储各项测试结果和总分
- 提供is_passed方法判断是否及格

### 评论模型

```python
class Comment(models.Model):
    test_result = models.ForeignKey(TestResult, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    content = models.TextField('评论内容')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    is_approved = models.BooleanField('是否批准', default=False)
```

**说明**:
- 学生对测试结果的评论
- 需要管理员批准才能公开显示

### 健康报告模型

```python
class HealthReport(models.Model):
    test_result = models.OneToOneField(TestResult, on_delete=models.CASCADE)
    overall_assessment = models.TextField('总体评估')
    health_suggestions = models.TextField('健康建议')
```

**说明**:
- 基于测试结果生成的健康建议报告
- 与测试结果一对一关系

### 新闻相关模型

```python
class SportsNews(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('published', '已发布'),
        ('archived', '已归档'),
    )
    
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    # 其他字段略...
    
class NewsComment(models.Model):
    news = models.ForeignKey(SportsNews, on_delete=models.CASCADE, related_name='comments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='news_comments')
    content = models.TextField('评论内容')
    is_approved = models.BooleanField('是否已审核', default=False)
```

**说明**:
- 体育新闻发布系统
- 学生可以对新闻进行评论，评论需审核

## 序列化器

序列化器负责将数据模型转换为JSON格式，以及验证客户端提交的数据。

### 用户序列化器

```python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'user_type', 'phone')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
```

**说明**:
- 继承ModelSerializer简化序列化过程
- 密码字段设为write_only，确保不会在响应中返回
- 重写create方法，确保密码加密存储

### 学生序列化器

```python
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
```

**说明**:
- 使用`fields = '__all__'`包含模型的所有字段

### 新闻评论序列化器

```python
class NewsCommentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    
    class Meta:
        model = NewsComment
        fields = ('id', 'news', 'student', 'student_name', 'content', 'created_at', 'is_approved')
        read_only_fields = ('is_approved',)
```

**说明**:
- 添加student_name字段，方便前端显示评论者姓名
- 设置is_approved为只读，确保只有管理员可以审核

## API接口设计

系统使用ViewSet构建RESTful API，减少代码重复并提供一致的接口。

### 视图集示例

```python
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            return Response({
                'token': 'token_will_be_implemented',
                'user_type': user.user_type,
                'username': user.username
            })
        return Response({'error': '用户名或密码错误'}, status=status.HTTP_400_BAD_REQUEST)
```

**说明**:
- 使用ModelViewSet自动提供标准CRUD操作
- 自定义action提供登录功能

### 权限控制示例

```python
class TestResultViewSet(viewsets.ModelViewSet):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer
    
    def get_queryset(self):
        if self.request.user.user_type == 'admin':
            return TestResult.objects.all()
        elif self.request.user.user_type == 'student':
            return TestResult.objects.filter(student__user=self.request.user)
        return TestResult.objects.none()
```

**说明**:
- 重写get_queryset方法实现基于用户角色的数据过滤
- 管理员可查看所有数据，学生只能查看自己的数据

### 自定义Action示例

```python
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def perform_create(self, serializer):
        serializer.save(student=self.request.user.student_profile)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        if request.user.user_type != 'admin':
            return Response({'error': '没有权限'}, status=status.HTTP_403_FORBIDDEN)
        comment = self.get_object()
        comment.is_approved = True
        comment.save()
        return Response({'status': '评论已审核通过'})
```

**说明**:
- perform_create方法自动关联当前用户的学生信息
- 自定义approve端点提供评论审核功能

## 认证与权限控制

系统采用基于角色的访问控制（RBAC）模型，通过用户类型区分权限。

### 权限设计原则

1. 管理员：系统全部功能访问权限
2. 学生：查看自己的测试结果、健康报告，提交评论
3. 家长：查看自己关联学生的测试结果和健康报告

### 权限实现示例

```python
def get_permissions(self):
    if self.action in ['create', 'update', 'partial_update', 'destroy']:
        return [permissions.IsAdminUser()]
    return [permissions.IsAuthenticated()]
```

```python
def get_queryset(self):
    if self.request.user.user_type == 'admin':
        return HealthReport.objects.all()
    elif self.request.user.user_type in ['student', 'parent']:
        # 学生只能查看自己的报告，家长可以查看自己孩子的报告
        if self.request.user.user_type == 'student':
            student = Student.objects.filter(user=self.request.user).first()
            if student:
                return HealthReport.objects.filter(test_result__student=student)
        else:  # 家长
            return HealthReport.objects.filter(test_result__student__parent=self.request.user)
    return HealthReport.objects.none()
```

## 数据关系与业务逻辑

### 评论限制

根据记忆中的信息，系统对评论创建有严格限制：

```python
def perform_create(self, serializer):
    """确保只有学生可以创建评论，并且评论与当前登录的学生关联"""
    if self.request.user.user_type != 'student':
        raise permissions.PermissionDenied("只有学生可以发表评论")
    
    student = Student.objects.filter(user=self.request.user).first()
    if not student:
        raise permissions.PermissionDenied("未找到关联的学生信息")
    
    serializer.save(student=student)
```

### 自动创建补考通知

系统使用Django信号机制在学生成绩未及格时自动创建补考通知：

```python
@receiver(post_save, sender=TestResult)
def create_makeup_notification(sender, instance, created, **kwargs):
    """当保存测试结果时，如果不及格且不是补考，则自动创建补考通知"""
    if created and not instance.is_passed and not instance.is_makeup:
        # 查找最近的补考计划
        makeup_plan = TestPlan.objects.filter(
            plan_type='makeup',
            test_date__gt=instance.test_date
        ).order_by('test_date').first()
        
        if makeup_plan:
            MakeupNotification.objects.create(
                student=instance.student,
                test_plan=makeup_plan,
                original_result=instance
            )
```

## 代码示例解析

### 体测成绩计算逻辑

体测成绩的计算需要根据标准判断是否达到优秀或及格标准：

```python
def calculate_score(self, result, standard):
    """计算体测总分"""
    scores = []
    
    # BMI评分 (在正常范围内得满分)
    if standard.bmi_min <= result.bmi <= standard.bmi_max:
        scores.append(20)
    else:
        scores.append(10)  # BMI不在正常范围
        
    # 肺活量评分
    if result.vital_capacity >= standard.vital_capacity_excellent:
        scores.append(20)  # 优秀
    elif result.vital_capacity >= standard.vital_capacity_pass:
        scores.append(15)  # 及格
    else:
        scores.append(10)  # 不及格
    
    # ... 其他项目的评分逻辑 ...
    
    return sum(scores)
```

### URL配置

后端API路由配置：

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, StudentViewSet, PhysicalStandardViewSet,
    TestPlanViewSet, TestResultViewSet, CommentViewSet, 
    HealthReportViewSet, SportsNewsViewSet, NewsCommentViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'students', StudentViewSet)
router.register(r'physical-standards', PhysicalStandardViewSet)
router.register(r'test-plans', TestPlanViewSet)
router.register(r'test-results', TestResultViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'health-reports', HealthReportViewSet)
router.register(r'news', SportsNewsViewSet)
router.register(r'news-comments', NewsCommentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
```

## 性能优化建议

1. **查询优化**：对频繁查询的数据添加适当的索引
   ```python
   class TestResult(models.Model):
       # ... 字段定义 ...
       
       class Meta:
           indexes = [
               models.Index(fields=['student', 'test_plan']),
               models.Index(fields=['total_score']),
           ]
   ```

2. **批量加载关联数据**：使用select_related和prefetch_related减少数据库查询
   ```python
   def get_queryset(self):
       return TestResult.objects.select_related('student', 'test_plan').all()
   ```

3. **缓存频繁访问的数据**：例如体测标准
   ```python
   from django.core.cache import cache
   
   def get_standard(gender):
       cache_key = f'physical_standard_{gender}'
       standard = cache.get(cache_key)
       if not standard:
           standard = PhysicalStandard.objects.get(gender=gender)
           cache.set(cache_key, standard, 3600)  # 缓存1小时
       return standard
   ```

## 安全与部署

### 安全建议

1. 使用HTTPS加密传输
2. 实现适当的API限流防止DoS攻击
3. 定期更新依赖包以修复安全漏洞
4. 生产环境禁用DEBUG模式

### 部署流程

1. 设置生产环境变量（SECRET_KEY, DATABASE_URL等）
2. 收集静态文件：`python manage.py collectstatic`
3. 使用Gunicorn或uWSGI作为WSGI服务器
4. 配置Nginx作为反向代理
5. 设置数据库备份策略
