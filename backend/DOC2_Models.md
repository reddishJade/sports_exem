# 体测管理系统后端数据模型文档

## 数据模型设计

系统核心数据模型体现了业务需求和数据关系。以下是主要模型的设计思路和实现方式。

## 用户认证模型设计

系统采用了两模型认证结构：

1. **User模型**：继承Django的AbstractUser，增加用户类型区分
2. **Student模型**：与User通过一对一关系关联，存储学生特有信息

### User模型设计

User模型扩展了Django的AbstractUser，添加了用户类型字段，支持三种用户角色：学生、家长和管理员。

**关键字段**:
- `user_type`: 用户类型，取值为'student'、'parent'或'admin'
- `phone`: 用户手机号码

这种设计允许我们：
- 利用Django内置的认证系统处理登录、密码管理等
- 通过user_type字段实现基于角色的权限控制

### Student模型设计

Student模型存储学生特有信息，并通过外键关联到家长用户。

**关键字段**:
- `user`: 与User模型的一对一关联，使用related_name='student_profile'
- `student_id`: 学号，唯一标识
- `gender`: 性别，用于关联体测标准
- `parent`: 关联到家长用户的外键，一个家长可以关联多个学生

**关系设计思路**:
- 使用OneToOneField关联User和Student，确保一个学生用户只对应一个学生记录
- 通过related_name='student_profile'使得可以通过user.student_profile访问学生信息
- 使用外键关联家长用户，建立家长与多个学生的关系

## 体测相关模型设计

### PhysicalStandard模型

存储不同性别的体测标准，包括优秀和及格两档标准。

**关键字段**:
- `gender`: 性别，区分男女标准
- 各项体测指标的优秀标准和及格标准

### TestPlan模型

记录体测计划信息，包括常规测试和补考测试。

**关键字段**:
- `plan_type`: 计划类型，区分常规测试和补考测试
- `test_date`: 测试日期
- `location`: 测试地点

### TestResult模型

记录学生的体测结果，关联学生和测试计划。

**关键字段**:
- `student`: 关联到Student模型的外键
- `test_plan`: 关联到TestPlan模型的外键
- 各项体测指标的具体成绩
- `total_score`: 总分
- `is_makeup`: 是否为补考

**特殊方法**:
- `is_passed`: 属性方法，判断是否达到及格标准

**技术实现关键点**:
- 使用`@property`装饰器将is_passed实现为只读属性
- 动态查询对应性别的体测标准
- 检查各项指标是否达到标准，并结合总分判断是否及格

## 评论系统设计

### Comment模型

学生对测试结果的评论，需要管理员审核。

**关键字段**:
- `test_result`: 关联到TestResult模型的外键
- `student`: 关联到Student模型的外键
- `is_approved`: 是否已审核通过

**权限控制**:
- 根据系统要求，只有学生用户类型(`user_type='student'`)
- 必须有关联的Student记录(`student_profile`)
- 这些规则在前端验证和后端CommentViewSet中都有实现

### 健康报告模型

基于测试结果生成的健康建议报告。

**关键字段**:
- `test_result`: 与TestResult模型的一对一关联
- `overall_assessment`: 总体评估
- `health_suggestions`: 健康建议

### 新闻评论模型

学生对体育新闻的评论，需要管理员审核。

**关键字段**:
- `news`: 关联到SportsNews模型的外键
- `student`: 关联到Student模型的外键
- `is_approved`: 是否已审核通过

## 自动化业务逻辑

### 自动创建补考通知

系统使用Django信号机制在学生成绩不及格时自动创建补考通知。

**技术实现**:
- 使用`@receiver`装饰器监听TestResult的post_save信号
- 当新建测试结果、不及格且非补考时，创建补考通知
- 自动查找最近的补考计划关联到通知

### 数据库关系图

```
User (AbstractUser) <----> Student
     ^                        ^
     |                        |
     v                        v
Parent User                TestResult <----> TestPlan
                              ^
                              |
                              v
                         HealthReport
                         
SportsNews <----> NewsComment <---- Student
```

## 数据完整性和约束

系统通过以下方式确保数据完整性：

1. **外键约束**: 使用on_delete指定关联记录删除时的行为
2. **唯一性约束**: 如Student.student_id的唯一性
3. **字段验证器**: 如使用MinValueValidator、MaxValueValidator控制数值范围
4. **默认值**: 为可选字段设置合理的默认值

## 数据模型优化建议

1. **索引优化**: 为经常查询的字段添加索引
```python
class Meta:
    indexes = [
        models.Index(fields=['student', 'test_date']),
    ]
```

2. **批量查询优化**: 使用select_related和prefetch_related减少数据库查询
```python
# 优化前
results = TestResult.objects.all()
for result in results:
    print(result.student.name)  # 每次访问都会查询数据库

# 优化后
results = TestResult.objects.select_related('student').all()
for result in results:
    print(result.student.name)  # 不会额外查询数据库
```

3. **查询集复用**: 创建常用查询的管理器方法
```python
class TestResultManager(models.Manager):
    def get_passed_results(self):
        return self.filter(total_score__gte=60)
```
