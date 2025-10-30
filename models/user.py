from sqlalchemy import String, Integer, Boolean, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import BaseModel, TableName, Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = {'comment': '用户角色关联表'}

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True, comment="用户ID")
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), primary_key=True, comment="角色Id")


class User(BaseModel):
    __tablename__ = 'users'
    telephone: Mapped[str] = mapped_column(String(11), index=True, unique=True, comment="手机号码")
    password: Mapped[str] = mapped_column(String(128), comment="密码")
    username: Mapped[str] = mapped_column(String(50), index=True, nullable=False, comment="姓名")

    # 修复关联关系
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users"
    )

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        生成哈希密码
        :param password: 原始密码
        :return: 哈希密码
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        验证原始密码是否与哈希密码一致
        :param password: 原始密码
        :param hashed_password: 哈希密码
        :return:
        """
        return pwd_context.verify(password, hashed_password)

    @property
    def is_admin(self) -> bool:
        """
        获取该用户是否拥有最高权限
        以最高权限为准
        :return:
        """
        return any([i.is_admin for i in self.roles])


class Role(BaseModel):
    __tablename__ = "roles"
    __table_args__ = ({'comment': '角色表'})
    role_key: Mapped[str] = mapped_column(String(50), index=True, comment="角色key")
    name: Mapped[str] = mapped_column(String(50), index=True, comment="名称")
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否禁用")
    order: Mapped[int | None] = mapped_column(Integer, default=0, comment="排序")
    desc: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="描述")
    is_admin: Mapped[bool] = mapped_column(Boolean, comment="是否为超级角色", default=False)

    # 添加反向关系
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles"
    )