# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2024/12/9
# @File           : response_schemas
# @desc           : 主配置文件
from typing import List, Union

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(..., description='登录Token')
    token_type: str = Field(..., description="jwt类型")


class UserResponse(BaseModel):
    id: int = Field(..., description="用户ID")
    mobile: str = Field(..., description="手机号码")
    name: str = Field(description="用户名")
    nickname: str = Field(description="用户昵称")
    disabled: bool = Field("是否禁止")
    created_at: Union[str, None] = Field("创建时间")

    model_config = {
        "from_attributes": True
    }


class UserListResponse(BaseModel):
    data: List[UserResponse]
    total: int = Field(description="数量")
