# -*- coding: UTF-8 -*-
# @Project ：zadmin 
# @version : 1.0
# @File    ：login.py
# @Author  ：ben
# @Date    ：2025/3/14 下午3:05 
# @desc    : 注释内容
from datetime import timedelta

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from apps.common.schemas import user_schemas
from config import settings
from core.exception import CustomException
from core.response import ErrorResponse
from models.system import LoginRecord
from models.user import User, Menu, Role
from utils import support, helpers


async def api_login_for_access_token(db: AsyncSession, username: str, password: str) -> str:
    """
    获取登录用户的 access_token
    """
    user = await support.get_user_by_telephone(db, username)
    error_code = status.HTTP_401_UNAUTHORIZED
    if not user:
        raise CustomException(status_code=error_code, code=error_code, msg="该手机号不存在")
    result = User.verify_password(password, user.password)
    if not result:
        raise CustomException(status_code=error_code, code=error_code, msg="手机号或密码错误")
    if not user.is_active:
        raise CustomException(status_code=error_code, code=error_code, msg="此手机号已被冻结")
    elif not user.is_staff:
        raise CustomException(status_code=error_code, code=error_code, msg="此手机号无权限")
    return helpers.create_token({"sub": user.id})


async def login_for_access_token(db, data, request):
    try:
        if data.method not in ["0", "1"]:
            raise CustomException("平台登录方式错误")
        user = await support.get_user_by_telephone(db, data.telephone)

        if not user:
            raise CustomException("手机或密码错误")

        result = User.verify_password(data.password, user.password)

        if not result:
            raise CustomException("输入密码验证失败")

        access_token = helpers.create_token(
            {"sub": user.id, "is_refresh": False}
        )
        expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        refresh_token = helpers.create_token(
            payload={"sub": user.id, "is_refresh": True},
            expires=expires
        )
        resp = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "is_reset_password": result.user.is_reset_password,
            "is_wx_server_openid": result.user.is_wx_server_openid
        }
        await LoginRecord.create_login_record(db, data, True, request, resp)

        return resp
    except Exception as e:
        await LoginRecord.create_login_record(db, data, False, request, {"message": str(e)})
        return ErrorResponse(msg=str(e))


async def update_refresh_token(refresh_token):
    """
    刷新refresh_token
    """
    error_code = status.HTTP_401_UNAUTHORIZED
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        is_refresh: bool = payload.get("is_refresh")

        if not user_id or not is_refresh:
            return ErrorResponse("未认证，请您重新登录", code=error_code, status=error_code)
    except jwt.exceptions.InvalidSignatureError:
        return ErrorResponse("无效认证，请您重新登录", code=error_code, status=error_code)
    except jwt.exceptions.ExpiredSignatureError:
        return ErrorResponse("登录已超时，请您重新登录", code=error_code, status=error_code)

    access_token = helpers.create_token({"sub": user_id, "is_refresh": False})
    expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = helpers.create_token(
        payload={"sub": user_id, "is_refresh": True},
        expires=expires
    )
    resp = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
    return resp


def generate_router_tree(menus: list[Menu], nodes: filter):
    """
    生成路由树
    :param menus: 总菜单列表
    :param nodes: 节点菜单列表
    :return:
    """

    data = []
    for root in nodes:
        router = user_schemas.RouterOut.model_validate(root)
        router.name = root.name
        router.index = root.order
        router.meta = user_schemas.Meta(
            title=root.title,
            icon=root.icon,
            hideInMenu=root.hidden,
            affixTab=root.affix,
            order=root.order,
            keepAlive=root.no_cache
        )
        sons = filter(lambda i: i.parent_id == root.id, menus)
        router.children = generate_router_tree(menus, sons)
        data.append(router.model_dump())
    return data


async def get_routers(db: AsyncSession, user: User):
    if any([i.is_admin for i in user.roles]):
        sql = select(Menu).where(Menu.disabled == 0, Menu.menu_type.in_([0, 1]), Menu.deleted_at.is_(None))
        queryset = await db.scalars(sql)
        datas = list(queryset.all())
    else:
        options = [joinedload(User.roles).subqueryload(Role.menus)]
        user = await support.get_user_by_id(db, user.id, options=options)
        datas = set()
        for role in user.roles:
            for menu in role.menus:
                # 非禁用并显示的所有惨淡
                if not menu.disabled:
                    datas.add(menu)
    roots = filter(lambda i: not i.parent_id, datas)
    menus = generate_router_tree(datas, roots)
    return Menu.menus_order(menus, 'index')
