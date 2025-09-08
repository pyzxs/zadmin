# -*- coding: UTF-8 -*-
# @Project ：zadmin 
# @version : 1.0
# @File    ：event.py
# @Author  ：ben
# @Date    ：2025/8/27 上午9:50 
# @desc    : 注释内容
from contextlib import asynccontextmanager

import aioredis
from aioredis import AuthenticationError, RedisError
from fastapi import FastAPI

from config import config

settings = config.get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    await register_cache(app, True)
    yield
    # 关闭时执行
    await register_cache(app, False)


async def register_cache(app: FastAPI, status=True):
    """
    缓存注册
    """
    if status:
        rd = aioredis.from_url(settings.CACHE_DB_URL, decode_responses=True, health_check_interval=1)
        app.state.redis = rd
        try:
            response = await rd.ping()
            if response:
                print("Redis 连接成功")
            else:
                print("Redis 连接失败")
        except AuthenticationError as e:
            raise AuthenticationError(f"Redis 连接认证失败，用户名或密码错误: {e}")
        except TimeoutError as e:
            raise TimeoutError(f"Redis 连接超时，地址或者端口错误: {e}")
        except RedisError as e:
            raise RedisError(f"Redis 连接失败: {e}")
    else:
        print("Redis 连接关闭")
        await app.state.redis.close()
