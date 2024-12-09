# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2024/12/9
# @File           : user
# @desc           : 主配置文件
from apps.user.models import User
from utils import encrypt, response
from utils.tools import order_by


async def create(db, req):
    req = req.dict()
    exists = db.query(User).filter_by(mobile=req['mobile']).count()
    if exists:
        raise response.fail(detail="手机号码已存在")

    req['password'] = encrypt.get_password_hash(req['password'])
    user = User(**req)
    db.add(user)
    db.commit()


def get_list(db, pagination):
    query = db.query(User)
    total = query.count()
    page = pagination.dict()
    query = order_by(query, User, page)
    records = query.offset(page["offset"]).limit(page["limit"]).all()
    returns = []
    for item in records:
        tmp = item.__dict__
        tmp['created_at'] = item.created_at.strftime('%Y-%m-%d %H:%M:%S')
        returns.append(tmp)

    return total, returns
