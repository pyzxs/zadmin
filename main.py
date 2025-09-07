# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2025/2/12
# @File           : main.py
# @desc           : 入口主文件
import os.path

import uvicorn
from fastapi import FastAPI, Path, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette.staticfiles import StaticFiles

import config
from config.config import BASE_DIR
from core import register_exception, database
from core.database import get_async_db, get_db
from models.user import User

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
    database.create_all_tables()

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",  # 指定 OpenAPI 文档路径
            title="partner",  # 自定义页面标题
            swagger_js_url="/media/swagger-ui/swagger-ui-bundle.js",  # 本地 JS 文件
            swagger_css_url="/media/swagger-ui/swagger-ui.css",  # 本地 CSS 文件
            swagger_favicon_url="/media/swagger-ui/favicon.png"  # 本地 favicon 图标
        )

    @app.get("/curd/async")
    async def async_curd(
            db: AsyncSession = Depends(get_async_db),
    ):
        """创建用户"""
        hashed_password = User.get_password_hash("123456")
        user = User(telephone="13800000090", password=hashed_password, username="admin")
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print("add user {} {} {}".format(user.username, user.telephone, user.id))

        """根据ID获取用户"""
        result = await db.execute(select(User).where(User.id == 3))
        user = result.scalar()
        print(" scalar_one_or_none user {} {} {}".format(user.username, user.telephone, user.id))

        """获取所有用户（分页）"""
        result = await db.execute(select(User).offset(0).limit(10))
        print(result.scalars().all())

        """更新用户信息"""
        stmt = update(User).where(User.id == 1).values({"telephone":"13522023423"})
        result = await db.execute(stmt)
        print(result)

        result = await db.execute(select(User).where(User.telephone == "13522023423"))
        user = result.scalar_one_or_none()
        print(user)

    @app.get("/curd/sync")
    async def sync_curd(
            db: Session = Depends(get_db),
    ):
        """同步创建用户"""
        hashed_password = User.get_password_hash("123456")
        user = User(telephone="13800000090", password=hashed_password, username="admin")
        db.add(user)
        db.commit()
        db.refresh(user)
        print("add user {} {} {}".format(user.username, user.telephone, user.id))
        """单行查询"""
        user = db.query(User).filter(User.id == 3).first()
        print("user by id  {} {} {}".format(user.username, user.telephone, user.id))
        """更新操作"""
        user = db.query(User).filter(User.id == 3).first()
        user.telephone = "13522023423"
        db.query(User).filter(User.id == 3).update({"telephone":"13522023423"})
        db.commit()
        db.refresh(user)

        user = db.query(User).filter(User.id == 1).first()
        db.delete(user)
        db.commit()

    return app


if __name__ == '__main__':
    if settings.app.debug:
        uvicorn.run(app='main:create_app', host=settings.app.host, port=settings.app.port, reload=True, factory=True)
    else:
        uvicorn.run(app='main:create_app', host=settings.app.host, port=settings.app.port, factory=True)
