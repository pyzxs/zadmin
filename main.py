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
import typer
import uvicorn

from apps import router
from config import settings
from core.database import engine, Base
from core.exception import register_exception
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from core.module import import_modules
from scripts import scheduler

shell_app = typer.Typer()


def create_app():
    """启动项目"""
    app = FastAPI(
        title="zadmin",
        description="管理后台模板",
        version=settings.VERSION,
    )

    Base.metadata.create_all(bind=engine)
    import_modules(settings.MIDDLEWARES, "中间件", app=app)

    # 全局异常捕捉处理
    register_exception(app)

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",  # 指定 OpenAPI 文档路径
            title="partner",  # 自定义页面标题
            swagger_js_url="/media/swagger-ui/swagger-ui-bundle.js",  # 本地 JS 文件
            swagger_css_url="/media/swagger-ui/swagger-ui.css",  # 本地 CSS 文件
            swagger_favicon_url="/media/swagger-ui/favicon.png"  # 本地 favicon 图标
        )

    if settings.STATIC_ENABLE:
        app.mount(settings.STATIC_URL, app=StaticFiles(directory=settings.STATIC_ROOT))

    for url in router.urlpatterns:
        app.include_router(url["ApiRouter"], prefix=url["prefix"], tags=url["tags"])

    return app



@shell_app.command()
def run(
        host: str = typer.Option(default='0.0.0.0', help='监听主机IP，默认开放给本网络所有主机'),
        port: int = typer.Option(default=9630, help='监听端口')
):
    if settings.DEBUG:
        uvicorn.run(app='main:create_app', host=host, port=port, reload=True, factory=True)
    else:
        uvicorn.run(app='main:create_app', host=host, port=port, factory=True)


@shell_app.command()
def queue():
    """
    启动服务脚本

    celery --app schedule worker -l info -c 4  -E -P eventlet
    """
    scheduler.queue()


@shell_app.command()
def crontab():
    """
    启动服务脚本

    celery --app schedule beat -l info
    """
    scheduler.crontab()


if __name__ == '__main__':
    shell_app()
