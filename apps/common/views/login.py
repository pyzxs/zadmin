# -*- coding: UTF-8 -*-
# @Project ：zadmin
# @version : 1.0
# @File    ：login.py
# @Author  ：ben
# @Date    ：2025/3/14 下午3:05
# @desc    : 注释内容

"""
JWT 表示 「JSON Web Tokens」。https://jwt.io/

它是一个将 JSON 对象编码为密集且没有空格的长字符串的标准。

通过这种方式，你可以创建一个有效期为 1 周的令牌。然后当用户第二天使用令牌重新访问时，你知道该用户仍然处于登入状态。
一周后令牌将会过期，用户将不会通过认证，必须再次登录才能获得一个新令牌。

我们需要安装 python-jose 以在 Python 中生成和校验 JWT 令牌：pip install python-jose[cryptography]

PassLib 是一个用于处理哈希密码的很棒的 Python 包。它支持许多安全哈希算法以及配合算法使用的实用程序。
推荐的算法是 「Bcrypt」：pip install passlib[bcrypt]
"""

from fastapi import APIRouter, Depends, Request, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from apps.common.logics import login
from apps.common.schemas.login_schemas import LoginForm
from core.database import get_async_db
from core.response import SuccessResponse
from models.system import LoginRecord
from utils import auth
from utils.auth import Auth

loginAPI = APIRouter()


@loginAPI.post("/login", summary="文档登录认证",  include_in_schema=False, description="Swagger API 文档登录认证")
async def api_login_for_access_token(
        request: Request,
        data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_async_db)
):
    access_token = login.api_login_for_access_token(db, data.username, data.password)
    record = LoginForm(platform='2', method='0', telephone=data.username, password=data.password)
    resp = {"access_token": access_token, "token_type": "bearer"}
    await LoginRecord.create_login_record(db, record, True, request, resp)
    return resp


@loginAPI.post("/token/refresh", summary="刷新Token")
async def token_refresh(refresh: str = Body(..., title="刷新Token")):
    return SuccessResponse(login.update_refresh_token(refresh), "刷新Token完成")


@loginAPI.post("/user/login", summary="手机号密码登录", description="员工登录通道")
async def login_for_access_token(
        request: Request,
        data: LoginForm,
        db: AsyncSession = Depends(get_async_db)
):
    resp = await login.login_for_access_token(db, data, request)
    return SuccessResponse(resp, "员工登录完成")


@loginAPI.get("/user/menus", summary="获取当前用户菜单树")
async def get_menu_list(auth: Auth = Depends(auth.AdminAuth())):
    return SuccessResponse(await login.get_routers(auth.async_db, auth.user))
