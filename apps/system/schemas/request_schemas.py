# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2024/12/9
# @File           : request_schemas
# @desc           : 主配置文件
from typing import Union

from pydantic import BaseModel, Field


class RegisterUser(BaseModel):
    mobile: str = Field(..., description="手机号码")
    password: str = Field(..., min_length=3, max_length=50)
    name: str = Field(default='', min_length=2, max_length=50)
    nickname: str = Field(default='', min_length=2, max_length=50)
    disabled: bool = Field(default=False, description="是否禁止")


class LoginUser(BaseModel):
    username: str = Field(..., description="登录用户")
    password: str = Field(..., min_length=3, max_length=50)


class CreateMenu(BaseModel):
    title: str = Field(..., description="名称")
    icon: str = Field(default='', description="菜单图标")
    redirect: Union[str, None] = Field(description="重定向地址")
    component: Union[str, None] = Field(description="前端组件地址")
    path: Union[str, None] = Field(description="前端路由地址")
    disabled: bool = Field(default=False, description="是否禁用")
    hidden: bool = Field(default=False, description="是否隐藏")
    order: int = Field(default=0, description="排序")
    menu_type: str = Field(description="菜单类型")
    parent_id: Union[int, None] = Field(default=0, description="父级ID")
    perms: Union[str,None] = Field(description="权限标识")
