# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2024/12/7
# @File           : validator.py
# @desc           : 请求体验证
"""
官方文档：https://pydantic-docs.helpmanual.io/usage/validators/#reuse-validators
"""
import datetime
import re
from typing import Union


def date_str_vali(value: Union[str, datetime.date]):
    """
    日期字符串验证
    """
    if isinstance(value, str):
        pattern = "%Y-%m-%d"
        try:
            datetime.datetime.strptime(value, pattern)
            return value
        except ValueError:
            pass
    elif isinstance(value, datetime.date):
        return value.strftime("%Y-%m-%d")
    raise ValueError("无效的日期时间或字符串数据")


def vali_telephone(value: str) -> str:
    """
    手机号验证器
    :param value: 手机号
    :return: 手机号
    """
    if not value or len(value) != 11 or not value.isdigit():
        raise ValueError("请输入正确手机号")

    regex = r'^1(3\d|4[4-9]|5[0-35-9]|6[67]|7[013-8]|8[0-9]|9[0-9])\d{8}$'

    if not re.match(regex, value):
        raise ValueError("请输入正确手机号")

    return value


def vali_email(value: str) -> str:
    """
    邮箱地址验证器
    :param value: 邮箱
    :return: 邮箱
    """
    if not value:
        raise ValueError("请输入邮箱地址")

    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(regex, value):
        raise ValueError("请输入正确邮箱地址")

    return value


def datetime_str_vali(value: Union[str, datetime.datetime]):
    """
    日期时间字符串验证
    """
    if isinstance(value, str):
        pattern = "%Y-%m-%d %H:%M:%S"
        try:
            datetime.datetime.strptime(value, pattern)
            return value
        except ValueError:
            pass
    elif isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(value, dict):
        # 用于处理 mongodb 日期时间数据类型
        date_str = value.get("$date")
        date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        # 将字符串转换为datetime.datetime类型
        datetime_obj = datetime.datetime.strptime(date_str, date_format)
        # 将datetime.datetime对象转换为指定的字符串格式
        return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
    raise ValueError("无效的日期时间或字符串数据")
