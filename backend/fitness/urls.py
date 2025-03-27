from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'students', views.StudentViewSet)
router.register(r'physical-standards', views.PhysicalStandardViewSet)
router.register(r'test-plans', views.TestPlanViewSet)
router.register(r'test-results', views.TestResultViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'health-reports', views.HealthReportViewSet)
router.register(r'news', views.SportsNewsViewSet)
router.register(r'news-comments', views.NewsCommentViewSet)
router.register(r'notifications', views.NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
