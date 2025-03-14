# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2024/12/7
# @File           : views
# @desc           : 视图文件
from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from apps.system.schemas import request_schemas, response_schemas
from apps.system.services import user, menu
from core import dependencies
from core.database import get_db
from utils import response, auth

systemAPI = APIRouter()


@systemAPI.post("/user/login", name="用户登录")
async def login_user(
        data: request_schemas.LoginUser,
        db: Session = Depends(get_db)
):
    token = auth.check_user_login(db, data)
    return {"access_token": token, "token_type": "bearer"}


@systemAPI.post("/user/register", description="注册用户", name="注册用户")
async def register_user(
        req: request_schemas.RegisterUser,
        db: Session = Depends(get_db),
        u=Depends(auth.get_current_user)
):
    await user.create(db, req)
    return response.success(data="创建用户完成")


@systemAPI.get("/users", response_model=response_schemas.UserList, description="用户列表", name="用户列表")
async def get_user_lists(
        pagination=Depends(dependencies.Paging),
        u=Depends(auth.get_current_user),
        permission_check: bool = Depends(auth.check_permission),
        db: Session = Depends(get_db)
):
    total, records = user.get_list(db, pagination)

    return {
        "total": total,
        "data": records
    }


@systemAPI.get("/menus", description="菜单列表", name="菜单列表")
async def get_menu_lists(
        pagination=Depends(dependencies.Paging),
        u=Depends(auth.get_current_user),
        permission_check: bool = Depends(auth.check_permission),
        db: Session = Depends(get_db)
):
    total, records = menu.get_menu_list(db, u, pagination)

    return {
        "total": total,
        "data": records
    }


@systemAPI.post("/menus/create", description="创建菜单", name="创建菜单")
async def create_menu(
        req: request_schemas.CreateMenu,
        u=Depends(auth.get_current_user),
        permission_check: bool = Depends(auth.check_permission),
):
    menu.create_menu(req)
    return response.success(message="创建菜单完成")


@systemAPI.get("/menus/{menu_id}", description="获取菜单详情", name="菜单详情")
async def get_menu(
        menu_id: int = Path(default=..., description="菜单ID"),
        u=Depends(auth.get_current_user),
        permission_check: bool = Depends(auth.check_permission)
):
    return menu.get_menu(menu_id)

@systemAPI.post("/menus/{menu_id}", description="编辑菜单", name="编辑菜单")
async def update_menu(
        req: request_schemas.CreateMenu,
        menu_id: int = Path(default=..., description="菜单ID"),
        u=Depends(auth.get_current_user),
        permission_check: bool = Depends(auth.check_permission),
):
    menu.update_menu(menu_id, req)
    return response.success(message="创建菜单完成")

@systemAPI.delete("/menus/{menu_id}", description="删除菜单", name="删除菜单")
async def update_menu(
        menu_id: int = Path(default=..., description="菜单ID"),
        u=Depends(auth.get_current_user),
        permission_check: bool = Depends(auth.check_permission),
):
    menu.delete_menu(menu_id)
    return response.success(message="删除菜单完成")
