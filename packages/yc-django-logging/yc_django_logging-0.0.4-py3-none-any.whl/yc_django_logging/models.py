"""
Created on 2024-07-10
@author:LiuFei
@description:日志記錄
BaseModel中有創建人信息，這裏不再單獨創建
"""
from django.db import models
from simple_history.models import HistoricalRecords
from django.conf import settings
from django.utils.translation import gettext as _
from yc_django_utils.models import BaseModel

table_prefix = settings.TABLE_PREFIX


class LoginLog(BaseModel):
    username = models.CharField(max_length=32, verbose_name=_("登录用户名"), null=True, blank=True)
    ip = models.CharField(max_length=32, verbose_name=_("登录ip"), null=True, blank=True)
    agent = models.TextField(verbose_name=_("agent信息"), null=True, blank=True)
    browser = models.CharField(max_length=255, verbose_name=_("浏览器名"), null=True, blank=True)
    os = models.CharField(max_length=255, verbose_name=_("操作系统"), null=True, blank=True)
    continent = models.CharField(max_length=255, verbose_name=_("州"), null=True, blank=True)
    country = models.CharField(max_length=255, verbose_name=_("国家"), null=True, blank=True)
    province = models.CharField(max_length=255, verbose_name=_("省份"), null=True, blank=True)
    city = models.CharField(max_length=255, verbose_name=_("城市"), null=True, blank=True)
    district = models.CharField(max_length=255, verbose_name=_("县区"), null=True, blank=True)
    isp = models.CharField(max_length=255, verbose_name=_("运营商"), null=True, blank=True)
    area_code = models.CharField(max_length=255, verbose_name=_("区域代码"), null=True, blank=True)
    country_english = models.CharField(max_length=255, verbose_name=_("英文全称"), null=True, blank=True)
    country_code = models.CharField(max_length=255, verbose_name=_("简称"), null=True, blank=True)
    longitude = models.CharField(max_length=255, verbose_name=_("经度"), null=True, blank=True)
    latitude = models.CharField(max_length=255, verbose_name=_("纬度"), null=True, blank=True)
    history = HistoricalRecords(verbose_name=_("历史修改记录"))

    class Meta:
        db_table = table_prefix + "login_log"
        verbose_name = _("登录日志")
        verbose_name_plural = verbose_name
        ordering = ("-id",)

    def __str__(self):
        return f"{self.username}"


class OperationLog(BaseModel):
    request_modular = models.CharField(max_length=255, verbose_name=_("请求模块"), null=True, blank=True)
    request_path = models.CharField(max_length=400, verbose_name=_("请求地址"), null=True, blank=True)
    request_body = models.TextField(verbose_name=_("请求参数"), null=True, blank=True)
    request_method = models.CharField(max_length=255, verbose_name=_("请求方式"), null=True, blank=True)
    request_msg = models.TextField(verbose_name=_("操作说明"), null=True, blank=True)
    request_ip = models.CharField(max_length=32, verbose_name=_("请求ip地址"), null=True, blank=True)
    request_browser = models.CharField(max_length=255, verbose_name=_("请求浏览器"), null=True, blank=True)
    response_code = models.CharField(max_length=32, verbose_name=_("响应状态码"), null=True, blank=True)
    request_os = models.CharField(max_length=255, verbose_name=_("操作系统"), null=True, blank=True)
    json_result = models.TextField(verbose_name=_("返回信息"), null=True, blank=True)
    status = models.BooleanField(default=False, verbose_name=_("响应状态"))
    history = HistoricalRecords(verbose_name=_("历史修改记录"))

    class Meta:
        db_table = table_prefix + "operation_log"
        verbose_name = _("操作日志")
        verbose_name_plural = verbose_name
        ordering = ("-id",)

    def __str__(self):
        return f"{self.request_path}"
