# -*- coding: utf-8 -*-
# @Project        : Apartment-partner-server
# @version        : 1.0
# @Create Time    : 2025/2/12
# @File           : helps.py
# @desc           : 基础全局函数
import inspect
import json
import random
import re
import string
from datetime import datetime, timedelta
from typing import List, Union, Any, Callable

import aiohttp
import jwt
from aiohttp import TCPConnector

from config import settings
from core.logger import logger


def valid_password(password: str) -> Union[str, bool]:
    """
    检测密码强度
    """
    if len(password) < 8 or len(password) > 16:
        return '长度需为8-16个字符,请重新输入。'
    else:
        for i in password:
            if 0x4e00 <= ord(i) <= 0x9fa5 or ord(i) == 0x20:  # Ox4e00等十六进制数分别为中文字符和空格的Unicode编码
                return '不能使用空格、中文，请重新输入。'
        else:
            key = 0
            key += 1 if bool(re.search(r'\d', password)) else 0
            key += 1 if bool(re.search(r'[A-Za-z]', password)) else 0
            key += 1 if bool(re.search(r"\W", password)) else 0
            if key >= 2:
                return True
            else:
                return '至少含数字/字母/字符2种组合，请重新输入。'


def generate_string(length: int = 8) -> str:
    """
    生成随机字符串
    :param length: 字符串长度
    """
    return ''.join(random.sample(string.ascii_letters + string.digits, length))


def date2str(dt, f="%Y-%m-%d %H:%M:%S") -> str:
    if isinstance(dt, str):
        return dt
    return dt.strftime(f)


def model_validate_out(obj, schemas) -> dict[str, Any]:
    """
    映射sqlalchemy对象到dydantic模型
    :param obj : sqlalchemy对象:
    :param schemas : pydantic模型:
    :return:
    """
    return schemas.model_validate(obj).model_dump()


def list_dict_find(options: List[dict], key: str, value: any) -> Union[dict, None]:
    """
    字典列表查找
    """
    return next((item for item in options if item.get(key) == value), None)


def dict_to_list_by_key(options: List[dict], key: str) -> list:
    """
    已字典中某个键重新生成列表
    :param options:
    :param key:
    :return:
    """
    return list(map(lambda item: item[key], options))


def get_file_size_unit(byte_size: float) -> str:
    """
    将字节大小转换为更易读的格式，单位可能是B、KB、MB、GB。

    :param byte_size: 文件大小（字节数）
    :return: 返回一个字符串，表示转换后的大小和单位
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if byte_size < 1024.0:
            return f"{byte_size:.2f} {unit}"
        byte_size /= 1024.0
    return f"{byte_size:.2f} TB"  # 如果文件大小达到TB级别，则返回TB单位。


async def cache_forever(rd, func: Callable, args: tuple, expire=settings.CACHE_EXPIRE) -> Any:
    """
    存储或获取缓存数据
    :param expire:
    :param rd: redis句柄
    :param func: 回调函数
    :param args: 回调函数参数
    :return:
    """
    mod = inspect.getmodule(func)
    module_name = mod.__name__ if mod else ''
    cache_key = f"cache:{module_name}.{func.__name__}"
    cache_data = await rd.get(cache_key)
    if not cache_data:
        data = await func(*args)
        await rd.set(cache_key, json.dumps(data), ex=expire)
        return data
    else:
        return json.loads(cache_data)


def generate_random_code(prefix_length=6, digits_length=7, separator='-'):
    """
    生成类似 JLXXFH-4355656 的随机码
    :param prefix_length: 前缀部分的长度，默认为6
    :param digits_length: 数字部分的长度，默认为7
    :param separator: 分隔符，默认为'-'
    :return: 随机生成的代码
    """
    # 生成前缀部分：大写字母
    prefix = ''.join(random.choices(string.ascii_uppercase, k=prefix_length))

    # 生成数字部分：数字字符
    digits = ''.join(random.choices(string.digits, k=digits_length))

    # 组合成最终的随机码
    random_code = f"{prefix}{separator}{digits}"

    return random_code


def timestamp_to_formatted_date(timestamp: float) -> str:
    """
    将时间戳转换为指定格式的日期时间字符串
    :param timestamp: 时间戳（秒）
    :return: 格式化后的日期时间字符串
    """
    # 将时间戳转换为 datetime 对象
    dt_object = datetime.fromtimestamp(timestamp)

    # 将 datetime 对象格式化为指定格式的字符串
    formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')

    return formatted_date


def create_token(payload: dict, expires: timedelta = None):
    """
    创建一个生成新的访问令牌的工具函数。

    pyjwt：https://github.com/jpadilla/pyjwt/blob/master/docs/usage.rst
    jwt 博客：https://geek-docs.com/python/python-tutorial/j_python-jwt.html

    #TODO 传入的时间为UTC时间datetime.datetime类型，但是在解码时获取到的是本机时间的时间戳
    """
    if expires:
        expire = datetime.now() + expires
    else:
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire})
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_location_by_ip(ip: str):
    url = f"https://api.ip138.com/ip/?ip={ip}&datatype=jsonp&token={settings.IP_PARSE_TOKEN}"
    ip_location_out_dict = {
        "ip": None,
        "address": None,
        "country": None,
        "province": None,
        "city": None,
        "county": None,
        "operator": None,
        "postal_code": None,
        "area_code": None
    }

    if not settings.IP_PARSE_ENABLE:
        logger.warning(
            "未开启IP地址数据解析，无法获取到IP所属地，请在application/config/production.py:IP_PARSE_ENABLE中开启！")
        return ip_location_out_dict  # 返回空模型的字典

    async with aiohttp.ClientSession(connector=TCPConnector(ssl=False)) as session:
        async with session.get(url) as resp:  # 修正self.url为url
            body = await resp.json()
            if body.get("ret") != 'ok':
                logger.error(f"获取IP所属地失败：{body}")
                return ip_location_out_dict

            data = body.get("data")
            ip_location_out_dict["ip"] = ip
            ip_location_out_dict["address"] = f"{''.join(data[i] for i in range(0, 4))} {data[4]}"
            ip_location_out_dict["country"] = data[0]
            ip_location_out_dict["province"] = data[1]
            ip_location_out_dict["city"] = data[2]
            ip_location_out_dict["county"] = data[3]
            ip_location_out_dict["operator"] = data[4]
            ip_location_out_dict["postal_code"] = data[5]
            ip_location_out_dict["area_code"] = data[6]
        return ip_location_out_dict
