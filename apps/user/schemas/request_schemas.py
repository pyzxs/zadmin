# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2024/12/9
# @File           : request_schemas
# @desc           : 主配置文件
from pydantic import BaseModel, Field


class RegisterUser(BaseModel):
    mobile: str = Field(..., description="手机号码")
    password: str = Field(..., min_length=3, max_length=50)
    name: str = Field(default='', min_length=3, max_length=50)
    nickname: str = Field(default='', min_length=3, max_length=50)
    disabled: bool = Field(default=False, description="是否禁止")
