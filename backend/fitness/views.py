from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Student, PhysicalStandard, TestPlan, TestResult, Comment, HealthReport, SportsNews, NewsComment, MakeupNotification
from .serializers import (
    UserSerializer, StudentSerializer, PhysicalStandardSerializer,
    TestPlanSerializer, TestResultSerializer, CommentSerializer, HealthReportSerializer,
    SportsNewsSerializer, SportsNewsListSerializer, NewsCommentSerializer,
    MakeupNotificationSerializer
)

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            # 使用JWT认证，生成access和refresh token
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_type': user.user_type,
                'username': user.username
            })
        return Response({'error': '用户名或密码错误'}, status=status.HTTP_400_BAD_REQUEST)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
    def get_queryset(self):
        if self.request.user.user_type == 'admin':
            return Student.objects.all()
        elif self.request.user.user_type == 'student':
            return Student.objects.filter(user=self.request.user)
        return Student.objects.none()

class PhysicalStandardViewSet(viewsets.ModelViewSet):
    queryset = PhysicalStandard.objects.all()
    serializer_class = PhysicalStandardSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

class TestPlanViewSet(viewsets.ModelViewSet):
    queryset = TestPlan.objects.all()
    serializer_class = TestPlanSerializer
    
    def get_queryset(self):
        # 管理员可以查看所有测试计划
        if self.request.user.user_type == 'admin':
            return TestPlan.objects.all()
            
        # 处理请求参数
        parent_filter = self.request.query_params.get('parent', 'false').lower() == 'true'
        student_filter = self.request.query_params.get('student', 'false').lower() == 'true'
        
        # 家长用户
        if self.request.user.user_type == 'parent' or parent_filter:
            try:
                # 获取家长关联的学生
                students = Student.objects.filter(parent_id=self.request.user.id)
                student_ids = [student.id for student in students]
                
                # 只返回常规计划和该家长子女的补考计划
                makeup_notifications = MakeupNotification.objects.filter(student_id__in=student_ids)
                makeup_plan_ids = [notification.test_plan_id for notification in makeup_notifications]
                
                # 返回常规计划和该家长子女的补考计划
                return TestPlan.objects.filter(
                    Q(plan_type='regular') | Q(id__in=makeup_plan_ids)
                )
            except Exception as e:
                print(f"Error filtering test plans for parent: {e}")
                return TestPlan.objects.filter(plan_type='regular')  # 默认只返回常规计划
        
        # 学生用户
        elif self.request.user.user_type == 'student' or student_filter:
            try:
                # 获取学生的ID
                student_id = self.request.user.student_profile.id if hasattr(self.request.user, 'student_profile') else None
                
                if student_id:
                    # 获取该学生相关的补考通知
                    makeup_notifications = MakeupNotification.objects.filter(student_id=student_id)
                    makeup_plan_ids = [notification.test_plan_id for notification in makeup_notifications]
                    
                    # 返回常规计划和该学生的补考计划
                    return TestPlan.objects.filter(
                        Q(plan_type='regular') | Q(id__in=makeup_plan_ids)
                    )
            except Exception as e:
                print(f"Error filtering test plans for student: {e}")
                
            # 默认只返回常规计划
            return TestPlan.objects.filter(plan_type='regular')
            
        # 默认处理
        return TestPlan.objects.filter(plan_type='regular')
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

class TestResultViewSet(viewsets.ModelViewSet):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer
    
    def get_queryset(self):
        if self.request.user.user_type == 'admin':
            return TestResult.objects.all()
        elif self.request.user.user_type == 'student':
            return TestResult.objects.filter(student__user=self.request.user)
        return TestResult.objects.none()
    
    @action(detail=False, methods=['get'])
    def makeup_list(self, request):
        queryset = self.get_queryset().filter(total_score__lt=60, is_makeup=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def perform_create(self, serializer):
        if self.request.user.user_type != 'student':
            raise permissions.PermissionDenied("只有学生可以发表评论")
        try:
            student = Student.objects.get(user=self.request.user)
            serializer.save(student=student)
        except Student.DoesNotExist:
            raise serializers.ValidationError("用户没有关联的学生信息")
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        if request.user.user_type != 'admin':
            return Response({'error': '没有权限'}, status=status.HTTP_403_FORBIDDEN)
        comment = self.get_object()
        comment.is_approved = True
        comment.save()
        return Response({'status': '评论已审核通过'})

class HealthReportViewSet(viewsets.ModelViewSet):
    queryset = HealthReport.objects.all()
    serializer_class = HealthReportSerializer
    
    def get_queryset(self):
        if self.request.user.user_type == 'admin':
            return HealthReport.objects.all()
        elif self.request.user.user_type in ['student', 'parent']:
            # 学生只能查看自己的报告，家长可以查看自己孩子的报告
            if self.request.user.user_type == 'student':
                student = Student.objects.filter(user=self.request.user).first()
                if student:
                    return HealthReport.objects.filter(test_result__student=student)
                return HealthReport.objects.none()  # 学生用户没有关联学生档案时返回空查询集
            else:  # 家长
                return HealthReport.objects.filter(test_result__student__parent=self.request.user)
        return HealthReport.objects.none()

class SportsNewsViewSet(viewsets.ModelViewSet):
    queryset = SportsNews.objects.filter(status='published')
    serializer_class = SportsNewsSerializer
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SportsNewsListSerializer
        return SportsNewsSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        """增加浏览次数"""
        news = self.get_object()
        news.views += 1
        news.save()
        return Response({'status': 'views updated'})
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """获取新闻评论"""
        news = self.get_object()
        comments = NewsComment.objects.filter(news=news, is_approved=True)
        serializer = NewsCommentSerializer(comments, many=True)
        return Response(serializer.data)

class NewsCommentViewSet(viewsets.ModelViewSet):
    queryset = NewsComment.objects.all()
    serializer_class = NewsCommentSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'approve']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        if self.request.user.user_type == 'admin':
            return NewsComment.objects.all()
        return NewsComment.objects.filter(student__user=self.request.user, is_approved=True)
    
    # 确保只有学生可以创建评论，并且评论与当前登录的学生关联
    def perform_create(self, serializer):
        if self.request.user.user_type != 'student':
            raise permissions.PermissionDenied("只有学生可以发表评论")
        try:
            student = Student.objects.get(user=self.request.user)
            serializer.save(student=student)
        except Student.DoesNotExist:
            raise serializers.ValidationError("用户没有关联的学生信息")
    
    # 审核评论
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        comment = self.get_object()
        comment.is_approved = True
        comment.save()
        return Response({'status': 'success'})

# 添加新的 NotificationViewSet 用于处理通知
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = MakeupNotification.objects.all()
    serializer_class = MakeupNotificationSerializer
    
    def get_queryset(self):
        # 只显示当前用户的通知
        if self.request.user.user_type == 'admin':
            return MakeupNotification.objects.all()
        elif self.request.user.user_type == 'student':
            try:
                student = Student.objects.get(user=self.request.user)
                return MakeupNotification.objects.filter(student=student)
            except Student.DoesNotExist:
                return MakeupNotification.objects.none()
        return MakeupNotification.objects.none()
    
    # 标记通知为已读
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'success'})
