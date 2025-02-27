from rest_framework import serializers
from .models import User, Student, PhysicalStandard, TestPlan, TestResult, Comment, HealthReport

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
