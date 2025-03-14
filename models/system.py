# -*- coding: UTF-8 -*-
# @Project ：zadmin 
# @version : 1.0
# @File    ：system.py
# @Author  ：ben
# @Date    ：2025/3/14 下午3:47 
# @desc    : 基础支撑模型
import json

from sqlalchemy import String, Text, Boolean
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from starlette.requests import Request
from starlette.requests import Request as StarletteRequest
from apps.common.schemas.login_schemas import LoginForm
from config import settings
from core.base import BaseModel
from user_agents import parse

from utils import helpers


class LoginRecord(BaseModel):
    __tablename__ = "login_records"
    __table_args__ = ({'comment': '登录记录表'})

    telephone: Mapped[str] = mapped_column(String(255), index=True, nullable=False, comment="手机号")
    status: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否登录成功")
    platform: Mapped[str] = mapped_column(String(8), comment="登陆平台")
    login_method: Mapped[str] = mapped_column(String(8), comment="认证方式")
    ip: Mapped[str | None] = mapped_column(String(50), comment="登陆地址")
    address: Mapped[str | None] = mapped_column(String(255), comment="登陆地点")
    country: Mapped[str | None] = mapped_column(String(255), comment="国家")
    province: Mapped[str | None] = mapped_column(String(255), comment="县")
    city: Mapped[str | None] = mapped_column(String(255), comment="城市")
    county: Mapped[str | None] = mapped_column(String(255), comment="区/县")
    operator: Mapped[str | None] = mapped_column(String(255), comment="运营商")
    postal_code: Mapped[str | None] = mapped_column(String(255), comment="邮政编码")
    area_code: Mapped[str | None] = mapped_column(String(255), comment="地区区号")
    browser: Mapped[str | None] = mapped_column(String(50), comment="浏览器")
    system: Mapped[str | None] = mapped_column(String(50), comment="操作系统")
    response: Mapped[str | None] = mapped_column(Text, comment="响应信息")
    request: Mapped[str | None] = mapped_column(Text, comment="请求信息")

    @classmethod
    async def create_login_record(
            cls,
            db: AsyncSession,
            data: LoginForm,
            status: bool,
            req: Request,
            resp: dict
    ):
        """
        创建登录记录
        :return:
        """
        if not settings.LOGIN_LOG_RECORD:
            return None
        header = {}
        for k, v in req.headers.items():
            header[k] = v
        if isinstance(req, StarletteRequest):
            form = (await req.form()).multi_items()
            params = json.dumps({"form": form, "headers": header})
        else:
            body = json.loads((await req.body()).decode())
            params = json.dumps({"body": body, "headers": header})
        user_agent = parse(req.headers.get("user-agent"))
        system = f"{user_agent.os.family} {user_agent.os.version_string}"
        browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
        ip = helpers.get_location_by_ip(req.client.host)
        location = await ip.parse()
        obj = LoginRecord(
            **location.dict(),
            telephone=data.telephone if data.telephone else data.code,
            status=status,
            browser=browser,
            system=system,
            response=json.dumps(resp),
            request=params,
            platform=data.platform,
            login_method=data.method
        )
        db.add(obj)
        await db.flush()
