# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2024/12/9
# @File           : user
# @desc           : 主配置文件
from apps.user.models import User
from core import curd
from utils import encrypt, response


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
    return curd.get_list(query, User, pagination)
