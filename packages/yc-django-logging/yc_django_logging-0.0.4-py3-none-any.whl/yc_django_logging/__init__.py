"""
Created on 2024-07-15
@author:LiuFei
@description:yc_django 日志记录模块【每次发布须修改版本号】

常用命令
# 导出依赖库
pip list --format=freeze > requirements.txt

# 安装依赖环境
pip install -r requirements.txt

# 打包成wheel格式
python setup.py bdist_wheel

# 发布、上传
twine upload --repository-url https://upload.pypi.org/legacy/  dist/*

# 用户安装
pip install yc_django_logging


# 使用方法
settings.py中添加中间件信息 和日志记录相关配置
"yc_django_logging.middleware.ApiLoggingMiddleware",  # 日志记录中间件[add]

日志模块配置
API_LOG_ENABLE = True  # 开启日志记录
# API_LOG_METHODS = 'ALL'
API_LOG_METHODS = ["POST", "UPDATE", "DELETE", "PUT"]  # 记录的类别

# 没有模块的可以在这里自定义映射。
API_MODEL_MAP = {
    "/token/": "登录模块",
    "/api/login/": "登录模块",
    "/api/plugins_market/plugins/": "插件市场",
}

登录日志调用utils.save_login_log记录

"""
