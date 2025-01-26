# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2024/12/07
# @File           : settings.py
# @IDE            : PyCharm
# @desc           : 主配置文件

import os
from fastapi.security import OAuth2PasswordBearer

"""
系统版本
"""
VERSION = "1.0.0"

"""安全警告: 不要在生产中打开调试运行!"""
DEBUG = True

"""
引入数据库配置
"""
if DEBUG:
    from config.development import *
else:
    from config.production import *

"""项目根目录"""
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

"""
是否开启登录认证
只适用于简单的接口
如果是与认证关联性比较强的接口，则无法使用
"""
OAUTH_ENABLE = True
"""
配置 OAuth2 密码流认证方式
官方文档：https://fastapi.tiangolo.com/zh/tutorial/security/first-steps/#fastapi-oauth2passwordbearer
auto_error:(bool) 可选参数，默认为 True。当验证失败时，如果设置为 True，FastAPI 将自动返回一个 401 未授权的响应，如果设置为 False，你需要自己处理身份验证失败的情况。
这里的 auto_error 设置为 False 是因为存在 OpenAuth：开放认证，无认证也可以访问，
如果设置为 True，那么 FastAPI 会自动报错，即无认证时 OpenAuth 会失效，所以不能使用 True。
"""
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login", auto_error=False) if OAUTH_ENABLE else lambda: ""
"""安全的随机密钥，该密钥将用于对 JWT 令牌进行签名"""
SECRET_KEY = 'vgb0tnl9d58+6n-6h-ea&u^1#s0ccp!794=kbvqacjq75vzps$'
"""用于设定 JWT 令牌签名算法"""
ALGORITHM = "HS256"
"""access_token 过期时间，一天"""
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
"""refresh_token 过期时间，用于刷新token使用，两天"""
REFRESH_TOKEN_EXPIRE_MINUTES = 1440 * 2
"""access_token 缓存时间，用于刷新token使用，30分钟"""
ACCESS_TOKEN_CACHE_MINUTES = 30

"""
挂载临时文件目录，并添加路由访问，此路由不会在接口文档中显示
TEMP_DIR：临时文件目录绝对路径
官方文档：https://fastapi.tiangolo.com/tutorial/static-files/
"""
TEMP_DIR = os.path.join(BASE_DIR, "temp")

"""
挂载静态目录，并添加路由访问，此路由不会在接口文档中显示
STATIC_URL：路由访问
STATIC_ROOT：静态文件目录绝对路径
官方文档：https://fastapi.tiangolo.com/tutorial/static-files/
"""
STATIC_URL = "/media"
STATIC_DIR = "static"
STATIC_ROOT = os.path.join(BASE_DIR, STATIC_DIR)


"""
跨域解决
"""
# 只允许访问的域名列表，* 代表所有
ALLOW_ORIGINS = ["*"]
# 是否支持携带 cookie
ALLOW_CREDENTIALS = True
# 设置允许跨域的http方法，比如 get、post、put等。
ALLOW_METHODS = ["*"]
# 允许携带的headers，可以用来鉴别来源等作用。
ALLOW_HEADERS = ["*"]


"""
其他项目配置
"""
# 默认密码，"0" 默认为手机号后六位
DEFAULT_PASSWORD = "123456"
# 默认登陆时最大输入密码或验证码错误次数
DEFAULT_AUTH_ERROR_MAX_NUMBER = 5
# 是否开启保存每次请求日志到本地
REQUEST_LOG_RECORD = True

"""
中间件配置
"""
MIDDLEWARES = [
    "core.middleware.http_request_cors_middleware",
    "core.middleware.register_request_log_middleware" if REQUEST_LOG_RECORD else None,
    "core.middleware.register_jwt_refresh_middleware"
]
