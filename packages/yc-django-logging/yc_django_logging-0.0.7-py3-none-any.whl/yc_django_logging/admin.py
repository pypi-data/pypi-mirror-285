from django.contrib import admin
from .models import LoginLog, OperationLog
from django.contrib.admin.models import LogEntry


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    """
    登录日志
    """
    list_display = ['id', 'username', 'ip', 'agent', 'browser', 'os', 'continent', 'country', 'province', 'city',
                    'district', 'isp', 'area_code', 'country_english', 'country_code', 'longitude', 'latitude', 'create_time']
    list_display_links = ['id', 'username']
    date_hierarchy = 'create_time'

    def has_add_permission(self, request):  # 禁用新增
        return False

    def has_change_permission(self, request, obj=None):  # 禁用修改
        return False

    def has_delete_permission(self, request, obj=None):  # 禁用删除
        return False


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    """
    操作日志
    """
    list_display = ['id', 'creator', 'request_modular', 'request_path', 'request_method', 'request_ip', 'request_browser',
                    'response_code', 'request_os', 'status']
    list_display_links = ['id', 'request_modular']
    date_hierarchy = 'create_time'

    def has_add_permission(self, request):  # 禁用新增
        return False

    def has_change_permission(self, request, obj=None):  # 禁用修改
        return False

    def has_delete_permission(self, request, obj=None):  # 禁用删除
        return False


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    """
    该类用于显示 admin 内置的 django_admin_log 表。
    其中，content_type 是指用户修改的 Model 名
    """
    list_display = ['action_time', 'user', 'content_type', '__str__']
    list_display_links = ['action_time']
    list_filter = ['action_time', 'content_type', 'user']
    list_per_page = 100
    readonly_fields = ['action_time', 'user', 'content_type',
                       'object_id', 'object_repr', 'action_flag', 'change_message']

    def has_add_permission(self, request):  # 禁用新增
        return False

    def has_change_permission(self, request, obj=None):  # 禁用修改
        return False

    def has_delete_permission(self, request, obj=None):  # 禁用删除
        return False
