# -*- coding: UTF-8 -*-
# @Project ：zadmin 
# @version : 1.0
# @File    ：support.py
# @Author  ：ben
# @Date    ：2025/3/14 下午2:16 
# @desc    : 数据表模型相关
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


async def update_login_info(db, user, last_ip: str) -> None:
    """
    更新当前登录信息
    :param db:
    :param user: 用户对象
    :param last_ip: 最近一次登录 IP
    :return:
    """
    user.last_ip = last_ip
    user.last_login_at = datetime.now()
    db.flush()


async def get_user_by_id(db: AsyncSession, user_id: str, options=None) -> User:
    """
    通过user_id 获取用户信息
    """
    if options is None:
        stmt = select(User).where(User.id == user_id)
    else:
        stmt = select(User).options(*options).where(User.id == user_id)

    return (await db.execute(stmt)).scalar()


async def get_user_by_telephone(db: AsyncSession, telephone: str) -> User:
    """
    通过手机号码获取用户信息
    """
    stmt = select(User).where(User.telephone == telephone)
    return (await db.execute(stmt)).scalar()