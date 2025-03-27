from rest_framework import serializers
from .models import User, Student, PhysicalStandard, TestPlan, TestResult, Comment, HealthReport, SportsNews, NewsComment

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
    class Meta:
        model = TestResult
        fields = '__all__'

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
