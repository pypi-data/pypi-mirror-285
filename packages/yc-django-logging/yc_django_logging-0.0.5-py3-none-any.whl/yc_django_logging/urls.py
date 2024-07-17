"""
Created on 2024/7/15 15:14
@author:刘飞
@description:
"""
from rest_framework import routers
from yc_django_logging.api.login_log import LoginLogViewSet
from yc_django_logging.api.operation_log import OperationLogViewSet

system_url = routers.SimpleRouter()

system_url.register(r'login_log', LoginLogViewSet)
system_url.register(r'operation_log', OperationLogViewSet)

urlpatterns = []
urlpatterns += system_url.urls
