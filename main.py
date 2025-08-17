# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2025/2/12
# @File           : main.py
# @desc           : 入口主文件
import os.path

import uvicorn
from fastapi import FastAPI, Path, HTTPException
from starlette import status
from starlette.staticfiles import StaticFiles

import config
from config.config import BASE_DIR
from core import get_logger, register_exception
from core.exception import CustomException

settings = config.get_settings()


def create_app():
    """启动项目"""

    app = FastAPI(
        title=settings.app.name,
        version=settings.app.version,
    )

    root_path = os.path.join(BASE_DIR, 'static')
    app.mount("/media", app=StaticFiles(directory=root_path))
    register_exception(app)

    @app.get("/{form_id}")
    async def root(form_id: int = Path(..., gt=0)):
        return {"message": form_id}

    return app


if __name__ == '__main__':
    if settings.app.debug:
        uvicorn.run(app='main:create_app', host=settings.app.host, port=settings.app.port, reload=True, factory=True)
    else:
        uvicorn.run(app='main:create_app', host=settings.app.host, port=settings.app.port, factory=True)
