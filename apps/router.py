# -*- coding: UTF-8 -*-
# @Project ：zadmin 
# @version : 1.0
# @File    ：router.py
# @Author  ：ben
# @Date    ：2025/3/14 下午2:04 
# @desc    : 路由地址

from apps.admin import adminSystemAPI
from apps.common import loginAPI

urlpatterns = [
    # 管理后台路由配置
    {"ApiRouter": adminSystemAPI, "prefix": "/api/admin/system", "tags": ["管理后台-权限管理"]},
    {"ApiRouter": loginAPI, "prefix": "/api", "tags": ["通用-授权登录"]},
]



