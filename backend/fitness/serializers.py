from rest_framework import serializers
from .models import User, Student, PhysicalStandard, TestPlan, TestResult, Comment, HealthReport, SportsNews, NewsComment, MakeupNotification

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'user_type', 'phone')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class PhysicalStandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalStandard
        fields = '__all__'

class TestPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestPlan
        fields = '__all__'

class TestResultSerializer(serializers.ModelSerializer):
    # 添加嵌套的test_plan字段，确保测试计划数据被正确序列化
    test_plan = TestPlanSerializer(read_only=True)
    # 使用SerializerMethodField显式获取is_passed字段
    is_passed = serializers.SerializerMethodField()
    
    class Meta:
        model = TestResult
        # 显式列出所有字段，确保is_passed被包含
        fields = ('id', 'student', 'test_plan', 'bmi', 'vital_capacity', 'run_50m', 
                  'sit_and_reach', 'standing_jump', 'run_800m', 'total_score', 'test_date', 
                  'is_makeup', 'is_passed')
        
    def get_is_passed(self, obj):
        # 获取对应性别的体测标准
        standard = PhysicalStandard.objects.get(gender=obj.student.gender)
        
        # 检查每个项目是否达到及格标准
        vital_capacity_passed = obj.vital_capacity >= standard.vital_capacity_pass
        run_50m_passed = obj.run_50m <= standard.run_50m_pass
        sit_and_reach_passed = obj.sit_and_reach >= standard.sit_and_reach_pass
        standing_jump_passed = obj.standing_jump >= standard.standing_jump_pass
        run_800m_passed = obj.run_800m <= standard.run_800m_pass
        
        all_items_passed = all([
            vital_capacity_passed,
            run_50m_passed,
            sit_and_reach_passed,
            standing_jump_passed,
            run_800m_passed
        ])
        
        # 打印详细信息
        print(f"TestResult ID: {obj.id}, Student: {obj.student.name}, Total Score: {obj.total_score}")
        print(f"  肺活量: {obj.vital_capacity} >= {standard.vital_capacity_pass} = {vital_capacity_passed}")
        print(f"  50米跑: {obj.run_50m} <= {standard.run_50m_pass} = {run_50m_passed}")
        print(f"  坐位体前屈: {obj.sit_and_reach} >= {standard.sit_and_reach_pass} = {sit_and_reach_passed}")
        print(f"  立定跳远: {obj.standing_jump} >= {standard.standing_jump_pass} = {standing_jump_passed}")
        print(f"  800米跑: {obj.run_800m} <= {standard.run_800m_pass} = {run_800m_passed}")
        print(f"  全部项目通过: {all_items_passed}")
        
        # 总分及格线为60分
        score_passed = obj.total_score >= 60
        passed = score_passed and all_items_passed
        print(f"  最终是否通过: {passed} (总分>=60:{score_passed} AND 所有项目通过:{all_items_passed})")
        
        return passed

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class HealthReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthReport
        fields = '__all__'

class SportsNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportsNews
        fields = '__all__'
        
class SportsNewsListSerializer(serializers.ModelSerializer):
    """简化版的新闻序列化器，用于列表显示"""
    class Meta:
        model = SportsNews
        fields = ('id', 'title', 'pub_date', 'featured_image', 'source_name', 'is_featured', 'views')

class NewsCommentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    
    class Meta:
        model = NewsComment
        fields = ('id', 'news', 'student', 'student_name', 'content', 'created_at', 'is_approved')
        read_only_fields = ('is_approved',)

class MakeupNotificationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    test_plan_title = serializers.CharField(source='test_plan.title', read_only=True)
    
    class Meta:
        model = MakeupNotification
        fields = ('id', 'student', 'student_name', 'test_plan', 'test_plan_title', 
                  'original_result', 'is_read', 'sent_at')
