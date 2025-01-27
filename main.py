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

from apps import systemAPI
from apps.index import indexAPI
from config import settings
from core.database import engine, Base
from core.exception import register_exception
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from core.router import get_all_routes
from scripts.initialize import initialize
from utils.tools import import_modules

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
    get_all_routes(app)

    # 路由
    app.mount(settings.STATIC_URL, app=StaticFiles(directory=settings.STATIC_ROOT))
    app.include_router(systemAPI, prefix='/system', tags=['系统'])
    app.include_router(indexAPI, tags=['通用'])

    return app


@shell_app.command()
def run(
        host: str = typer.Option(default='0.0.0.0', help='监听主机IP，默认开放给本网络所有主机'),
        port: int = typer.Option(default=8080, help='监听端口')
):
    if settings.DEBUG:
        print(f"start run develop {host} {port}")
        uvicorn.run(app='main:create_app', host=host, port=port, reload=True, factory=True)
    else:
        print(f"start run online {host} {port}")
        uvicorn.run(app='main:create_app', host=host, port=port, factory=True)


@shell_app.command()
def init():
    """初始化数据库"""
    migrate = initialize.Migration()
    migrate.run()


if __name__ == '__main__':
    shell_app()
