from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import User, Student, PhysicalStandard, TestPlan, TestResult, Comment, HealthReport, SportsNews, NewsComment
from .serializers import (
    UserSerializer, StudentSerializer, PhysicalStandardSerializer,
    TestPlanSerializer, TestResultSerializer, CommentSerializer, HealthReportSerializer,
    SportsNewsSerializer, SportsNewsListSerializer, NewsCommentSerializer
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
            return Response({
                'token': 'token_will_be_implemented',
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
        serializer.save(student=self.request.user.student_profile)
    
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
        elif self.request.user.user_type == 'student':
            student = Student.objects.filter(user=self.request.user).first()
            if student:
                return NewsComment.objects.filter(student=student)
        return NewsComment.objects.none()
    
    def perform_create(self, serializer):
        """确保只有学生可以创建评论，并且评论与当前登录的学生关联"""
        if self.request.user.user_type != 'student':
            raise permissions.PermissionDenied("只有学生可以发表评论")
        
        student = Student.objects.filter(user=self.request.user).first()
        if not student:
            raise permissions.PermissionDenied("未找到关联的学生信息")
        
        serializer.save(student=student)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审核评论"""
        if request.user.user_type != 'admin':
            return Response({'detail': '只有管理员可以审核评论'}, status=status.HTTP_403_FORBIDDEN)
        
        comment = self.get_object()
        comment.is_approved = True
        comment.save()
        return Response({'status': '评论已审核通过'})
