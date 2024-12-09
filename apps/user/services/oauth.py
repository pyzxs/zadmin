# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2024/12/9
# @File           : oauth
# @desc           : 主配置文件
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from apps.user.models import User
from config import settings
from config.settings import oauth2_scheme
from core.database import get_db
from utils import status


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
