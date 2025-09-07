from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import BaseModel, TableName
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class User(BaseModel):
    __tablename__ = 'users'
    telephone: Mapped[str] = mapped_column(String(11), index=True, unique=True, comment="手机号码")
    password: Mapped[str] = mapped_column(String(128), comment="密码")
    username: Mapped[str] = mapped_column(String(50), index=True, nullable=False, comment="姓名")

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