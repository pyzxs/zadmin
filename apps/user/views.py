# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2024/12/7
# @File           : views
# @desc           : 视图文件
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from apps.user.schemas import request_schemas, response_schemas
from apps.user.services import auth, user, oauth, menu
from core import dependencies
from core.database import get_db
from utils import response

userAPI = APIRouter()


@userAPI.post("/api/login", response_model=response_schemas.Token, name="文档登录认证")
async def api_login_for_access_token(
        data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    token = auth.check_user_login(db, data)
    return {"access_token": token, "token_type": "bearer"}


@userAPI.post("/register", description="注册用户", name="注册用户")
async def register_user(
        req: request_schemas.RegisterUser,
        db: Session = Depends(get_db),
        u=Depends(oauth.get_current_user)
):
    await user.create(db, req)
    return response.success(data="创建用户完成")


@userAPI.get("/", response_model=response_schemas.UserListResponse, description="用户列表", name="用户列表")
async def get_user_lists(
        pagination=Depends(dependencies.Paging),
        u=Depends(oauth.get_current_user),
        db: Session = Depends(get_db)
):
    total, records = user.get_list(db, pagination)

    return {
        "total": total,
        "data": records
    }


@userAPI.get("/menus", description="菜单列表", name="菜单列表")
async def get_menu_lists(
        pagination=Depends(dependencies.Paging),
        u=Depends(oauth.get_current_user),
        db: Session = Depends(get_db)
):
    total, records = menu.get_menu_list(db, pagination)

    return {
        "total": total,
        "data": records
    }
