"""
Created on 2024/7/17 下午3:36
@author:刘飞
@description: 操作日志
"""
from yc_django_utils.request_util import get_request_user
from yc_django_utils.viewset import CustomModelViewSet
from yc_django_logging.models import OperationLog
from yc_django_logging.serializers import OperationLogSerializer


class OperationLogViewSet(CustomModelViewSet):
    """
    操作日志接口
    list:查询
    retrieve:单例
    """
    http_method_names = ["get"]
    serializer_class = OperationLogSerializer

    def get_queryset(self):
        return OperationLog.objects.filter(creator=get_request_user(self.request))
