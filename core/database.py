from datetime import datetime

from sqlalchemy import create_engine, Integer, DateTime, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, Mapped, mapped_column

from config.config import get_settings

settings = get_settings()
# 定义基类
Base = declarative_base()


# 定义一个公共模型
class BaseModel(Base):
    """
    公共 ORM 模型，基表
    """
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='主键ID')
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        comment='创建时间')
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        comment='更新时间'
    )
    deleted_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        comment='删除时间')


# 异步引擎
async_engine = create_async_engine(
    url=settings.database.async_url,
    echo=settings.database.echo_sql,
    pool_size=settings.database.pool_size
)

# 同步引擎
engine = create_engine(
    url=settings.database.url,
    echo=settings.database.echo_sql,
    pool_size=settings.database.pool_size
)

# 同步会话工厂
session_local = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine)

# 异步会话工厂
session_factory = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    expire_on_commit=True,
    class_=AsyncSession
)


# 异步会话
async def get_async_db():
    async with session_factory() as session:
        yield session


# 同步会话
def get_db():
    with session_local() as session:
        yield session


def create_all_tables():
    Base.metadata.create_all(bind=engine)


async def async_create_all_tables():
    async with async_engine.begin() as conn:
        # 使用 run_sync 在异步上下文中执行同步操作
        await conn.run_sync(Base.metadata.create_all)


def TableName(table_name: str = None):
    def decorator(cls):
        if table_name is not None:
            # 如果指定了表名，直接设置为类属性
            cls.__tablename__ = table_name
        else:
            # 如果没有指定表名，使用自动生成的表名
            model_name = cls.__name__
            ls = []
            for index, char in enumerate(model_name):
                if char.isupper() and index != 0:
                    ls.append("_")
                ls.append(char.lower())
            cls.__tablename__ = "".join(ls)

        return cls

    return decorator