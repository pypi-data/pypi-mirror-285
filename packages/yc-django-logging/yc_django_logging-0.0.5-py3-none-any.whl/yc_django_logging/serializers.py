"""
Created on 2024/7/17 下午3:36
@author:刘飞
@description:
"""
from yc_django_logging.models import LoginLog, OperationLog
from yc_django_utils.serializers import CustomModelSerializer


class LoginLogSerializer(CustomModelSerializer):
    """
    登录日志权限-序列化器
    """

    class Meta:
        model = LoginLog
        fields = "__all__"
        read_only_fields = ["id"]


class OperationLogSerializer(CustomModelSerializer):
    """
    操作日志-序列化器
    """

    class Meta:
        model = OperationLog
        fields = "__all__"
        read_only_fields = ["id"]
