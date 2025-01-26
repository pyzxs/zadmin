# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2025/1/26
# @File           : curl.py
# @desc           : 主配置文件
from datetime import datetime

from core import database


def get_list(query, model, pagination):
    total = query.count()
    page = pagination.dict()
    query = order_by(query, model, page)
    records = query.offset(page["offset"]).limit(page["limit"]).all()
    returns = []
    for item in records:
        tmp = item.__dict__
        tmp['created_at'] = item.created_at.strftime('%Y-%m-%d %H:%M:%S')
        returns.append(tmp)

    return total, returns


def create(model, data):
    """创建数据"""
    db = database.get_db()
    m = model(**data)
    db.add(m)
    db.commit()


def update(model, primary_id, data):
    """更新数据"""
    db = database.get_db()
    db.query(model).filter_by(id=primary_id).update(data)
    db.commit()


def soft_delete(model, primary_id):
    """软删除"""
    db = database.get_db()
    db.query(model).filter_by(id=primary_id).update({"deleted_at": datetime.now()})
    db.commit()


def real_delete(model, primary_id):
    """真实删除"""
    db = database.get_db()
    db.query(model).filter_by(id=primary_id).delete()
    db.commit()


def get(model, primary_id):
    """获取详情"""
    db = database.get_db()
    return db.query(model).filter_by(id=primary_id).first()


def restore(row):
    """回复软软删除"""
    db = database.get_db()
    row.deleted_at = None
    db.commit()


def order_by(query, model, page):
    if page['v_order_field']:
        field = getattr(model, page['v_order_field'])
        if page['v_order'] == 'desc':
            query = query.order_by(field.desc())
        else:
            query = query.order_by(field.asc())
    return query
