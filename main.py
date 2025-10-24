# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2025/2/12
# @File           : main.py
# @desc           : 入口主文件
import os.path

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.staticfiles import StaticFiles

import config
from api.router import register_routers
from config.config import BASE_DIR
from core import register_exception, database, register_middleware

settings = config.get_settings()


def create_app():
    """启动项目"""

    app = FastAPI(
        title=settings.app.name,
        version=settings.app.version,
    )

    register_exception(app)
    register_middleware(app)
    register_routers(app)
    database.create_all_tables()
    root_path = os.path.join(BASE_DIR, 'static')
    app.mount("/media", app=StaticFiles(directory=root_path))

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",  # 指定 OpenAPI 文档路径
            title="partner",  # 自定义页面标题
            swagger_js_url="/media/swagger-ui/swagger-ui-bundle.js",  # 本地 JS 文件
            swagger_css_url="/media/swagger-ui/swagger-ui.css",  # 本地 CSS 文件
            swagger_favicon_url="/media/swagger-ui/favicon.png"  # 本地 favicon 图标
        )

    return app


if __name__ == '__main__':
    if settings.app.debug:
        uvicorn.run(app='main:create_app', host=settings.app.host, port=settings.app.port, reload=True, factory=True)
    else:
        uvicorn.run(app='main:create_app', host=settings.app.host, port=settings.app.port, factory=True)
