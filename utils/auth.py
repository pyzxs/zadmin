# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2021/10/24 16:44
# @File           : auth.py
# @IDE            : PyCharm
# @desc           : 用户凭证验证装饰器
from typing import Annotated

from fastapi import Request, Depends
import jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from starlette import status

from config import settings
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db, get_db
from core.exception import CustomException
from datetime import timedelta, datetime

from models.user import User, Role
from utils.support import get_user_by_id


class Auth(BaseModel):
    user: User = None
    async_db: AsyncSession
    db: AsyncSession

    class Config:
        # 接收任意类型
        arbitrary_types_allowed = True


class AuthValidation:
    """
    用于用户每次调用接口时，验证用户提交的token是否正确，并从token中获取用户信息
    """

    # status_code = 401 时，表示强制要求重新登录，因账号已冻结，账号已过期，手机号码错误，刷新token无效等问题导致
    # 只有 code = 401 时，表示 token 过期，要求刷新 token
    # 只有 code = 错误值时，只是报错，不重新登陆
    error_code = status.HTTP_401_UNAUTHORIZED
    warning_code = status.HTTP_400_BAD_REQUEST

    # status_code = 403 时，表示强制要求重新登录，因无系统权限，而进入到系统访问等问题导致

    @classmethod
    def validate_token(cls, request: Request, token: str | None) -> str:
        """
        验证用户 token
        """
        if not token:
            raise CustomException(
                msg="请您先登录！",
                code=status.HTTP_403_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN
            )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            exp: int = payload.get("exp")
            is_refresh: bool = payload.get("is_refresh")
            if not user_id or is_refresh:
                raise CustomException(
                    msg="未认证，请您重新登录",
                    code=status.HTTP_403_FORBIDDEN,
                    status_code=status.HTTP_403_FORBIDDEN
                )
            # 计算当前时间 + 缓冲时间是否大于等于 JWT 过期时间
            buffer_time = (datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_CACHE_MINUTES)).timestamp()
            # print("过期时间", exp, datetime.fromtimestamp(exp))
            # print("当前时间", buffer_time, datetime.fromtimestamp(buffer_time))
            # print("剩余时间", exp - buffer_time)
            if buffer_time >= exp:
                request.scope["if-refresh"] = 1
            else:
                request.scope["if-refresh"] = 0
        except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError):
            raise CustomException(
                msg="无效认证，请您重新登录",
                code=status.HTTP_403_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN
            )
        except jwt.exceptions.ExpiredSignatureError:
            raise CustomException(msg="认证已失效，请您重新登录", code=cls.error_code, status_code=cls.error_code)

        return user_id

    @classmethod
    def validate_user(cls, request: Request, user: User, db: AsyncSession) -> Auth:
        """
        验证用户信息
        :param request:
        :param user:
        :param db:
        :return:
        """
        if user is None:
            raise CustomException(msg="未认证，请您重新登陆", code=cls.error_code, status_code=cls.error_code)
        elif not user.is_active:
            raise CustomException(msg="用户已被冻结！", code=cls.error_code, status_code=cls.error_code)
        request.scope["telephone"] = user.telephone
        request.scope["user_id"] = user.id
        request.scope["user_name"] = user.name
        try:
            request.scope["body"] = request.body()
        except RuntimeError:
            request.scope["body"] = "获取失败"

        return Auth(user=user, db=db)

    @classmethod
    async def get_user_permissions(cls, user: User) -> set:
        """
        获取员工用户所有权限列表
        :parama user: 用户实例
        :return:
        """
        if user.is_admin:
            return {'*.*.*'}
        permissions = set()
        for role_obj in user.roles:
            for menu in role_obj.menus:
                if menu.perms and not menu.disabled:
                    permissions.add(menu.perms)
        return permissions


class UserAuth(AuthValidation):
    """
    开放认证，无认证也可以访问
    认证了以后可以获取到用户信息，无认证则获取不到
    """

    async def __call__(
            self,
            request: Request,
            token: Annotated[str, Depends(settings.oauth2_scheme)],
            async_db: AsyncSession = Depends(get_async_db),
            db: Session = Depends(get_db),
    ):
        """
        每次调用依赖此类的接口会执行该方法
        """
        if not settings.OAUTH_ENABLE:
            return Auth(async_db=async_db, db=db)
        try:
            user_id = self.validate_token(request, token)
            user = await get_user_by_id(async_db,user_id)
            return await self.validate_user(request, user, async_db)
        except CustomException:
            return Auth(async_db=async_db, db=db)


class AdminAuth(AuthValidation):
    """
    只支持员工用户认证
    获取员工用户完整信息
    如果有权限，那么会验证该用户是否包括权限列表中的其中一个权限
    """

    def __init__(self, permissions: list[str] | None = None):
        if permissions:
            self.permissions = set(permissions)
        else:
            self.permissions = None

    async def __call__(
            self,
            request: Request,
            token: str = Depends(settings.oauth2_scheme),
            async_db: AsyncSession = Depends(get_async_db),
            db: Session = Depends(get_db),
    ) -> Auth:
        """
        每次调用依赖此类的接口会执行该方法
        """
        if not settings.OAUTH_ENABLE:
            return Auth(db=db,async_db=async_db)
        user_id = self.validate_token(request, token)
        options = [
            joinedload(User.roles).subqueryload(Role.menus),
        ]
        user = await get_user_by_id(async_db, user_id, options)
        result = await self.validate_user(request, user, async_db)
        permissions = self.get_user_permissions(user)
        if permissions != {'*.*.*'} and self.permissions:
            if not (self.permissions & permissions):
                raise CustomException(msg="无权限操作", code=status.HTTP_403_FORBIDDEN)
        return result






