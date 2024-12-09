# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2024/12/7
# @File           : auth
# @desc           : 主配置文件
from datetime import timedelta, datetime

from fastapi import status, Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from apps.user.models import User
from config import settings
from core.exception import CustomException
from utils import encrypt


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
    return create_token(data,expire )



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
