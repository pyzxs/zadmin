# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2025/2/12
# @File           : main.py
# @desc           : 入口主文件


import uvicorn
from fastapi import FastAPI
import config

settings = config.get_settings()


def create_app():
    """启动项目"""

    app = FastAPI(
        title=settings.app.name,
        version=settings.app.version,
    )

    return app


if __name__ == '__main__':
    if settings.app.debug:
        uvicorn.run(app='main:create_app', host=settings.app.host, port=settings.app.port, reload=True, factory=True)
    else:
        uvicorn.run(app='main:create_app', host=settings.app.host, port=settings.app.port, factory=True)
