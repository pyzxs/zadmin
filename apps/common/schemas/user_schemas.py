# -*- coding: UTF-8 -*-
# @Project ：zadmin 
# @version : 1.0
# @File    ：user.py
# @Author  ：ben
# @Date    ：2025/3/14 下午3:28 
# @desc    : 注释内容
from typing import Union

from pydantic import BaseModel, ConfigDict, Field

from core.datatype import Telephone, DatetimeStr


class User(BaseModel):
    name: str
    telephone: Telephone
    nickname: str | None = None
    avatar: str | None = None
    is_active: bool | None = True
    is_staff: bool | None = True
    gender: str | None = "0"
    is_wx_server_openid: bool | None = False


class UserSimpleOut(User):
    model_config = ConfigDict(from_attributes=True)

    id: int
    update_datetime: DatetimeStr
    create_datetime: DatetimeStr

    is_reset_password: bool | None = None
    last_login: DatetimeStr | None = None
    last_ip: str | None = None


class UserPasswordOut(UserSimpleOut):
    model_config = ConfigDict(from_attributes=True)

    password: str


class Meta(BaseModel):
    title: str
    icon: Union[str, None] = None
    keepAlive: Union[bool, None] = False
    hideInMenu: Union[bool, None] = False
    affixTab: Union[bool, None] = False
    order: Union[int, None] = None


class RouterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="菜单Id")
    name: Union[str, None] = None
    component: Union[str, None] = None
    path: str
    redirect: Union[str, None] = None
    meta: Union[Meta, None] = None
    index: Union[int, None] = None
    children: list[dict] = []