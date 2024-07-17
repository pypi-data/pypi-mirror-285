"""
Created on 2024/7/16 17:06
@author:刘飞
@description: 一些配置信息
"""
from django.utils.translation import gettext_lazy as _

logging_menu_list = [
    {
        'name': _('日志模块'),
        'models': [
            {
                'name': _('操作日志'),
                'url': 'yc_django_logging/operationlog/'
            },  # 操作日志
            {
                'name': _('登录日志'),
                'url': 'yc_django_logging/loginlog/'
            },  # 登录日志
            {
                'name': _('后台日志'),
                'url': 'admin/logentry/'
            },  # 后台日志
        ]
    }
]
