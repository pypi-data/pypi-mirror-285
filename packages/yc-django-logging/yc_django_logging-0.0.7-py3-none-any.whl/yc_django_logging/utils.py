"""
Created on 2024/7/17 10:56
@author:刘飞
@description:
"""
from user_agents import parse
from .models import LoginLog
from yc_django_utils.request_util import get_request_ip, get_ip_analysis, get_browser, get_os


# 登录日志记录
def save_login_log(request):
    """
    保存登录日志
    :return:
    """
    ip = get_request_ip(request=request)
    analysis_data = get_ip_analysis(ip)
    analysis_data['username'] = request.user.username
    analysis_data['ip'] = ip
    analysis_data['agent'] = str(parse(request.META['HTTP_USER_AGENT']))
    analysis_data['browser'] = get_browser(request)
    analysis_data['os'] = get_os(request)
    analysis_data['creator_id'] = request.user.id
    LoginLog.objects.create(**analysis_data)
