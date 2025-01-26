# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2025/1/26
# @File           : response_schemas.py
# @desc           : 主配置文件
from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(..., description='登录Token')
    token_type: str = Field(..., description="jwt类型")
