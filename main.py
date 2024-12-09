# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2024/12/07 15:47
# @File           : main.py
# @IDE            : PyCharm
# @desc           : 主程序入口

"""
FastApi 更新文档：https://github.com/tiangolo/fastapi/releases
FastApi Github：https://github.com/tiangolo/fastapi
Typer 官方文档：https://typer.tiangolo.com/
"""

import uvicorn

from apps import userAPI
from config import settings
from core.database import engine, Base
from core.exception import register_exception
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from utils.tools import import_modules

"""
启动项目
"""
app = FastAPI(
    title="zadmin",
    description="管理后台模板",
    version=settings.VERSION,
)

Base.metadata.create_all(bind=engine)
import_modules(settings.MIDDLEWARES, "中间件", app=app)

# 全局异常捕捉处理
register_exception(app)

# 跨域解决
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS
)

app.mount(settings.STATIC_URL, app=StaticFiles(directory=settings.STATIC_ROOT))
app.include_router(userAPI, prefix='/user', tags=['用户'])

if __name__ == '__main__':
    if settings.DEBUG:
        uvicorn.run('main:app', host='0.0.0.0', port=8081, reload=True)
    else:
        uvicorn.run('main:app', host='0.0.0.0', port=8081)
