"""
Created on 2024/7/17 下午3:36
@author:刘飞
@description: 登录日志
"""
from yc_django_logging.models import LoginLog
from yc_django_utils.viewset import CustomModelViewSet
from yc_django_utils.request_util import get_request_user
from yc_django_logging.serializers import LoginLogSerializer


class LoginLogViewSet(CustomModelViewSet):
    """
    登录日志接口
    list:查询
    retrieve:单例
    """
    http_method_names = ["get"]
    serializer_class = LoginLogSerializer

    def get_queryset(self):
        return LoginLog.objects.filter(creator=get_request_user(self.request))
