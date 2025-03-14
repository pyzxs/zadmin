# -*- coding: UTF-8 -*-
# @Project ：zadmin 
# @version : 1.0
# @File    ：request_schemas.py
# @Author  ：ben
# @Date    ：2025/3/14 下午3:24 
# @desc    : 注释内容
from pydantic import BaseModel, field_validator, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from apps.common.schemas import user_schemas
from config import settings
from core.validator import valid_telephone
from utils import auth, support


class LoginForm(BaseModel):
    telephone: str
    password: str
    method: str = '0'  # 认证方式，0：密码登录，1：短信登录，2：微信一键登录
    platform: str = '0'  # 登录平台，0：PC端管理系统，1：移动端管理系统

    # 重用验证器：https://docs.pydantic.dev/dev-v2/usage/validators/#reuse-validators
    normalize_telephone = field_validator('telephone')(valid_telephone)


class LoginResult(BaseModel):
    status: bool | None = False
    user: user_schemas.UserPasswordOut | None = None
    msg: str | None = None

    class Config:
        arbitrary_types_allowed = True


class LoginValidation:
    """
    验证用户登录时提交的数据是否有效
    """

    def __init__(self, func):
        self.func = func

    async def __call__(self, data: LoginForm, db: AsyncSession, request: Request) -> LoginResult:
        self.result = LoginResult()
        if data.platform not in ["0", "1"] or data.method not in ["0", "1"]:
            self.result.msg = "无效参数"
            return self.result
        user = await support.get_user_by_telephone(db,data.telephone)
        if not user:
            self.result.msg = "该手机号不存在！"
            return self.result

        result = await self.func(self, data=data, user=user, request=request)


        if not user.is_active:
            self.result.msg = "此手机号已被冻结！"
        elif data.platform in ["0", "1"] and not user.is_staff:
            self.result.msg = "此手机号无权限！"
        else:
            self.result.msg = "OK"
            self.result.status = True
            self.result.user = user_schemas.UserPasswordOut.model_validate(user)
            await support.update_login_info(db, user, request.client.host)
        return self.result
