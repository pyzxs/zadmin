from typing import Optional, List

import jwt
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta, datetime

from config import get_settings
from core.database import get_db
from core.exception import CustomException
from models.user import User

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login", auto_error=False)


def check_user_login(db, data):
    """
    fastapi授权登录
    :param db:
    :param data:
    :return:
    """

    user = db.query(User).filter(User.telephone == data.username).first()
    error_code = status.HTTP_401_UNAUTHORIZED
    if not user:
        raise CustomException(status_code=error_code, code=error_code, msg="该手机号不存在")

    result = User.verify_password(data.password, user.password)
    if not result:
        raise CustomException(status_code=error_code, code=error_code, msg="手机号或密码错误")

    data = {"id": user.id, "telephone": user.telephone}
    expire = timedelta(minutes=settings.jwt.expires_in)
    return create_token(data, expire)


def create_token(payload: dict, expires: timedelta = None):
    """
    创建一个生成新的访问令牌的工具函数。

    pyjwt：https://github.com/jpadilla/pyjwt/blob/master/docs/usage.rst
    jwt 博客：https://geek-docs.com/python/python-tutorial/j_python-jwt.html

    #TODO 传入的时间为UTC时间datetime.datetime类型，但是在解码时获取到的是本机时间的时间戳
    """
    if expires:
        expire = datetime.now() + expires
    else:
        expire = datetime.now() + timedelta(minutes=settings.jwt.expires_in)

    payload.update({"exp": expire})
    encoded_jwt = jwt.encode(payload, settings.jwt.secret_key, algorithm=settings.jwt.algorithm)
    return encoded_jwt


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="需要身份认证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm])
        uid: str = payload.get("id")
        if uid is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = db.query(User).get(uid)

    if user is None:
        raise credentials_exception
    return user

