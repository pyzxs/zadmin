# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2024/12/9
# @File           : menu
# @desc           : 主配置文件

from apps.system.models import Menu
from core import curd


def get_menu_list(db, u, pagination):
    query = db.query(Menu)
    return curd.get_list(query, Menu, pagination)


def create_menu(req):
    data = req.dict()
    return curd.create(Menu, data)


def update_menu(menu_id, req):
    data = req.dict()
    return curd.update(Menu, menu_id, data)


def delete_menu(menu_id):
    """软删除菜单"""
    return curd.soft_delete(Menu, menu_id, )


def get_menu(menu_id):
    return curd.get(Menu, menu_id)
