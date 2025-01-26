# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2024/12/9
# @File           : models.py
# @desc           : 主配置文件
from typing import Union

from sqlalchemy import Table, Integer, ForeignKey, Column, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base import BaseModel
from core.database import Base

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE")),
    comment="用户与角色关联表"
)

role_menus = Table(
    "role_menus",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE")),
    Column("menu_id", Integer, ForeignKey("menus.id", ondelete="CASCADE")),
    comment="角色与菜单关联表"
)

user_departments = Table(
    "user_departments",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("department_id", Integer, ForeignKey("departments.id", ondelete="CASCADE")),
    comment="用户与部门关联表"
)


class Department(BaseModel):
    __tablename__ = "departments"
    __table_args__ = ({'comment': '部门表'})

    name: Mapped[str] = mapped_column(String(50), index=True, nullable=False, comment="部门名称")
    dept_key: Mapped[str] = mapped_column(String(50), index=True, nullable=False, comment="部门标识")
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否禁用")
    order: Mapped[int or None] = mapped_column(Integer, comment="显示排序")
    desc: Mapped[str or None] = mapped_column(String(255), comment="描述")
    owner: Mapped[str or None] = mapped_column(String(255), comment="负责人")
    phone: Mapped[str or None] = mapped_column(String(255), comment="联系电话")
    email: Mapped[str or None] = mapped_column(String(255), comment="邮箱")

    parent_id: Mapped[Union[int, None]] = mapped_column(
        Integer,
        ForeignKey("departments.id", ondelete='CASCADE'),
        default=None,
        comment="上级部门"
    )


class Menu(BaseModel):
    __tablename__ = "menus"
    __table_args__ = ({'comment': '菜单表'})

    title: Mapped[str] = mapped_column(String(50), comment="名称")
    icon: Mapped[Union[str, None]] = mapped_column(String(50), comment="菜单图标")
    redirect: Mapped[Union[str, None]] = mapped_column(String(100), comment="重定向地址")
    component: Mapped[Union[str, None]] = mapped_column(String(255), comment="前端组件地址")
    path: Mapped[Union[str, None]] = mapped_column(String(50), comment="前端路由地址")
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否禁用")
    hidden: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否隐藏")
    order: Mapped[int] = mapped_column(Integer, comment="排序")
    menu_type: Mapped[str] = mapped_column(String(8), comment="菜单类型")
    parent_id: Mapped[Union[int, None]] = mapped_column(
        Integer,
        ForeignKey("menus.id"),
        nullable=True,
        comment="父菜单"
    )
    perms: Mapped[Union[str or None]] = mapped_column(String(50), comment="权限标识", unique=False, index=True)


class Role(BaseModel):
    __tablename__ = "roles"
    __table_args__ = ({'comment': '角色表'})

    name: Mapped[str] = mapped_column(String(50), index=True, comment="名称")
    role_key: Mapped[str] = mapped_column(String(50), index=True, comment="权限字符")
    data_range: Mapped[int] = mapped_column(Integer, default=4, comment="数据权限范围")
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否禁用")
    order: Mapped[int or None] = mapped_column(Integer, default=0,  comment="排序")
    desc: Mapped[str or None] = mapped_column(String(255), comment="描述")
    is_admin: Mapped[bool] = mapped_column(Boolean, comment="是否为超级角色", default=False)

    menus: Mapped[set[Menu]] = relationship(secondary=role_menus)


class User(BaseModel):
    __tablename__ = 'users'
    __table_args__ = ({'comment': '用户表'})
    mobile: Mapped[str] = mapped_column(String(11), index=True, unique=True, doc="手机号码")
    password: Mapped[str] = mapped_column(String(128), doc="密码")
    name: Mapped[str] = mapped_column(String(50), index=True, nullable=False, comment="姓名")
    nickname: Mapped[str or None] = mapped_column(String(50), nullable=True, comment="昵称")
    gender: Mapped[str or None] = mapped_column(String(8), nullable=True, comment="性别")
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否禁用")
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否为工作人员")

    roles: Mapped[set[Role]] = relationship(secondary=user_roles)
    depts: Mapped[set[Department]] = relationship(secondary=user_departments)

    def is_admin(self) -> bool:
        """
        获取该用户是否拥有最高权限
        以最高权限为准
        :return:
        """
        return any([i.is_admin for i in self.roles])
