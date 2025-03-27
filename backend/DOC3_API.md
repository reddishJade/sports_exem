# 体测管理系统后端API文档

## API设计与实现

本系统使用Django REST framework实现RESTful API，为前端提供数据服务。本文档详细说明API设计理念、实现方式和关键接口。

## 序列化器实现

序列化器负责将模型数据转换为JSON格式，以及验证客户端提交的数据。

### 序列化器设计理念

1. **模型映射**: 每个主要模型都有对应的序列化器
2. **字段控制**: 根据需求选择暴露或隐藏特定字段
3. **嵌套关系**: 处理模型间的关联关系
4. **验证逻辑**: 实现数据验证规则

### 关键序列化器实现

#### UserSerializer

用户序列化器处理用户创建和信息展示，特别注意密码安全性：

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

关键点：
- 使用`write_only=True`确保密码不会在响应中返回
- 重写`create`方法使用`create_user`方法，确保密码加密存储

#### NewsCommentSerializer

新闻评论序列化器展示了如何添加派生字段：

```python
class NewsCommentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    
    class Meta:
        model = NewsComment
        fields = ('id', 'news', 'student', 'student_name', 'content', 'created_at', 'is_approved')
        read_only_fields = ('is_approved',)
```

关键点：
- 添加`student_name`字段，方便前端显示评论者姓名
- 使用`source='student.name'`指定字段数据来源
- 设置`is_approved`为只读，确保只有管理员可以审核

## API视图实现

系统使用ViewSet构建RESTful API，减少代码重复并提供一致的接口。

### ViewSet设计理念

1. **资源导向**: 每个ViewSet对应一个资源类型
2. **CRUD操作**: 自动提供标准的创建、读取、更新、删除操作
3. **权限控制**: 基于用户角色控制资源访问
4. **自定义行为**: 通过`@action`装饰器扩展标准CRUD操作

### 用户认证API

用户认证API实现了基本的登录功能：

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

关键点：
- 使用`@action`装饰器定义自定义endpoint `/api/users/login/`
- 使用Django的`authenticate`函数验证用户凭据
- 返回包含用户类型的信息，前端据此控制界面显示

### 基于角色的数据过滤

系统根据用户角色过滤可访问的数据，如测试结果视图集：

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

关键点：
- 重写`get_queryset`方法实现基于用户角色的数据过滤
- 管理员可查看所有数据，学生只能查看自己的数据
- 默认返回空查询集，防止未授权访问

### 评论管理API

评论管理API体现了系统中的权限控制和业务限制：

```python
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def perform_create(self, serializer):
        if self.request.user.user_type != 'student':
            raise permissions.PermissionDenied("只有学生可以发表评论")
        
        try:
            student = self.request.user.student_profile
        except:
            raise permissions.PermissionDenied("未找到关联的学生信息")
            
        serializer.save(student=student)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        if request.user.user_type != 'admin':
            return Response({'error': '没有权限'}, status=status.HTTP_403_FORBIDDEN)
        comment = self.get_object()
        comment.is_approved = True
        comment.save()
        return Response({'status': '评论已审核通过'})
```

关键点：
- 重写`perform_create`方法确保：
  1. 只有学生用户类型可以创建评论
  2. 用户必须有关联的学生记录
  3. 评论自动关联到当前学生
- 自定义`approve`操作只允许管理员审核评论

## URL路由配置

系统使用DRF的Router自动为ViewSet生成URL配置：

```python
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

这种配置会生成以下URL模式：
- `/api/users/` - 用户列表和创建
- `/api/users/<id>/` - 用户详情、更新和删除
- `/api/users/login/` - 自定义的登录操作
- 其他资源也遵循类似的URL模式

## API权限控制

系统采用多层次的权限控制方案：

### 1. 基于视图的权限

在视图集中动态分配权限：

```python
def get_permissions(self):
    if self.action in ['create', 'update', 'partial_update', 'destroy']:
        return [permissions.IsAdminUser()]
    return [permissions.IsAuthenticated()]
```

### 2. 基于角色的数据过滤

家长只能查看自己孩子的健康报告：

```python
def get_queryset(self):
    if self.request.user.user_type == 'admin':
        return HealthReport.objects.all()
    elif self.request.user.user_type in ['student', 'parent']:
        if self.request.user.user_type == 'student':
            student = Student.objects.filter(user=self.request.user).first()
            if student:
                return HealthReport.objects.filter(test_result__student=student)
        else:  # 家长
            return HealthReport.objects.filter(test_result__student__parent=self.request.user)
    return HealthReport.objects.none()
```

### 3. 自定义操作权限

只有管理员可以审核评论：

```python
@action(detail=True, methods=['post'])
def approve(self, request, pk=None):
    if request.user.user_type != 'admin':
        return Response({'detail': '只有管理员可以审核评论'}, 
                        status=status.HTTP_403_FORBIDDEN)
```

## API性能优化

### 1. 查询优化

减少数据库查询次数：

```python
# 优化前
def get_queryset(self):
    results = TestResult.objects.filter(student__user=self.request.user)
    # 每个结果都会查询学生和测试计划
    return results

# 优化后
def get_queryset(self):
    return TestResult.objects.select_related('student', 'test_plan')
                      .filter(student__user=self.request.user)
```

### 2. 分页

处理大量数据时使用分页：

```python
class SportsNewsViewSet(viewsets.ModelViewSet):
    queryset = SportsNews.objects.filter(status='published')
    serializer_class = SportsNewsSerializer
    pagination_class = StandardResultsSetPagination
```

### 3. 过滤和搜索

为复杂查询添加过滤功能：

```python
class TestResultViewSet(viewsets.ModelViewSet):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__name', 'test_plan__title']
    ordering_fields = ['test_date', 'total_score']
```

## API错误处理

系统实现一致的错误处理机制：

1. **HTTP状态码**：使用标准HTTP状态码表示错误类型
   - 400：客户端请求错误
   - 401：未认证
   - 403：权限不足
   - 404：资源不存在
   - 500：服务器错误

2. **错误消息格式**：统一的错误响应格式
   ```json
   {
       "error": "错误描述",
       "field_errors": {
           "字段名": ["具体错误信息"]
       }
   }
   ```

3. **异常处理**：使用try-except捕获并处理异常
   ```python
   try:
       student = self.request.user.student_profile
   except:
       raise permissions.PermissionDenied("未找到关联的学生信息")
   ```

## API测试与文档

### API测试策略

1. **单元测试**：测试各个API端点的功能
2. **权限测试**：确保不同用户角色的访问控制正确
3. **集成测试**：测试端到端的业务流程

### API文档

系统可以集成DRF的文档生成工具，如drf-yasg，提供自动生成的API文档：

```python
# 集成Swagger文档
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="体测管理系统API",
        default_version='v1',
        description="体测管理系统API文档",
    ),
    public=True,
)

urlpatterns = [
    # 其他URL路径
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0)),
]
```
