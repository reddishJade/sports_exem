from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, PhysicalStandard, TestPlan, TestResult, Comment, HealthReport, MakeupNotification, SportsNews, NewsComment

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'phone', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('email', 'phone', 'user_type')}),
        ('权限', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'user_type', 'password1', 'password2'),
        }),
    )

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_id', 'class_name', 'get_parent_name')
    search_fields = ('name', 'student_id', 'class_name')
    list_filter = ('class_name',)

    def get_parent_name(self, obj):
        return obj.parent.username if obj.parent else '-'
    get_parent_name.short_description = '家长'

@admin.register(PhysicalStandard)
class PhysicalStandardAdmin(admin.ModelAdmin):
    list_display = ('gender', 'bmi_min', 'bmi_max', 'vital_capacity_excellent', 
                   'run_50m_excellent', 'sit_and_reach_excellent', 'standing_jump_excellent', 
                   'run_800m_excellent')
    list_filter = ('gender',)

@admin.register(TestPlan)
class TestPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'test_date', 'location', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('test_date', 'location')
    date_hierarchy = 'test_date'

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'test_plan', 'total_score', 'test_date', 'is_makeup')
    search_fields = ('student__name', 'test_plan__title')
    list_filter = ('is_makeup', 'test_date')
    date_hierarchy = 'test_date'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('student', 'test_result', 'content', 'created_at', 'is_approved')
    search_fields = ('student__name', 'content')
    list_filter = ('is_approved', 'created_at')
    date_hierarchy = 'created_at'
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = '批准选中的评论'

@admin.register(HealthReport)
class HealthReportAdmin(admin.ModelAdmin):
    list_display = ('test_result', 'get_student_name', 'created_at')
    search_fields = ('test_result__student__name', 'overall_assessment')
    date_hierarchy = 'created_at'

    def get_student_name(self, obj):
        return obj.test_result.student.name
    get_student_name.short_description = '学生'

@admin.register(MakeupNotification)
class MakeupNotificationAdmin(admin.ModelAdmin):
    list_display = ('student', 'test_plan', 'is_read', 'sent_at')
    search_fields = ('student__name', 'test_plan__title')
    list_filter = ('is_read', 'sent_at')
    date_hierarchy = 'sent_at'
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = '标记为已读'

@admin.register(SportsNews)
class SportsNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'status', 'views', 'is_featured')
    search_fields = ('title', 'content', 'source_name')
    list_filter = ('status', 'is_featured', 'pub_date')
    date_hierarchy = 'pub_date'
    fieldsets = (
        (None, {'fields': ('title', 'content', 'status', 'is_featured')}),
        ('来源信息', {'fields': ('source_url', 'source_name')}),
        ('图片', {'fields': ('featured_image',)}),
        ('SEO', {'fields': ('keywords',)}),
    )

@admin.register(NewsComment)
class NewsCommentAdmin(admin.ModelAdmin):
    list_display = ('student', 'news', 'content', 'created_at', 'is_approved')
    search_fields = ('student__name', 'news__title', 'content')
    list_filter = ('is_approved', 'created_at')
    date_hierarchy = 'created_at'
    actions = ['approve_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = '批准选中的评论'

# 自定义管理站点标题
admin.site.site_header = '体测管理系统'
admin.site.site_title = '体测管理系统'
admin.site.index_title = '管理界面'
