# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2025/1/25
# @File           : views.py
# @desc           : 未登录通用
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from apps.index.schemas import response_schemas
from core.database import get_db
from utils import response, auth

indexAPI = APIRouter()


@indexAPI.get('/', description="首页", name='首页')
def index():
    return response.fail(detail="未能登录首页")


@indexAPI.post("/api/login", response_model=response_schemas.Token, name="文档登录认证", include_in_schema=False)
async def api_login_for_access_token(
        data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    token = auth.check_user_login(db, data)
    return {"access_token": token, "token_type": "bearer"}
