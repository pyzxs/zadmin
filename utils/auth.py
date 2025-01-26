# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2025/1/25
# @File           : oauth.py
# @desc           : 登录授权
from datetime import timedelta, datetime

import casbin
import casbin_sqlalchemy_adapter
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette.requests import Request

from apps.system.models import User
from config import settings
from config.settings import oauth2_scheme
from core.database import get_db
from core.exception import CustomException
from utils import status, encrypt


def check_user_login(db, data):
    user = db.query(User).filter(User.mobile == data.username).first()
    error_code = status.HTTP_401_UNAUTHORIZED
    if not user:
        raise CustomException(status_code=error_code, code=error_code, msg="该手机号不存在")

    result = encrypt.verify_password(data.password, user.password)
    if not result:
        raise CustomException(status_code=error_code, code=error_code, msg="手机号或密码错误")
    if user.disabled:
        raise CustomException(status_code=error_code, code=error_code, msg="此手机号已被冻结")
    data = {"id": user.id, "mobile": user.mobile}
    expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_token(data, expire)


def create_token(payload: dict, expires: timedelta = None):
    """
    创建一个生成新的访问令牌的工具函数。

    pyjwt：https://github.com/jpadilla/pyjwt/blob/master/docs/usage.rst
    jwt 博客：https://geek-docs.com/python/python-tutorial/j_python-jwt.html

    #TODO 传入的时间为UTC时间datetime.datetime类型，但是在解码时获取到的是本机时间的时间戳
    """
    if expires:
        expire = datetime.utcnow() + expires
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire})
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        uid: str = payload.get("id")
        if uid is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).get(uid)

    if user is None:
        raise credentials_exception
    return user


async def check_permission(
    request: Request,
    user: User = Depends(get_current_user)
):
    """权限验证"""
    adapter = casbin_sqlalchemy_adapter.Adapter(settings.SQLALCHEMY_DATABASE_URL)
    enforcer = casbin.Enforcer(settings.BASE_DIR + "/config/rbac.conf", adapter)
    method = request.method
    path = request.url.path

    # 超级管理员
    if user.is_admin():
        return True

    # 假设用户的角色存储在User对象中的roles属性中
    for role in user.roles:
        if enforcer.enforce(role.role_key, path, method):
            return True
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
