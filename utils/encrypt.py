# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2024/12/9
# @File           : encrypt
# @desc           : 主配置文件
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password: str) -> str:
    """
    生成哈希密码
    :param password: 原始密码
    :return: 哈希密码
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    验证原始密码是否与哈希密码一致
    :param password: 原始密码
    :param hashed_password: 哈希密码
    :return:
    """
    return pwd_context.verify(password, hashed_password)
