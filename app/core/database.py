"""
数据库连接和会话管理模块
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase
from loguru import logger

from .config import get_settings


class Base(DeclarativeBase):
    """数据库模型基类"""
    pass


# 数据库引擎
engine = None
AsyncSessionLocal = None


async def init_database() -> None:
    """初始化数据库"""
    global engine, AsyncSessionLocal
    
    settings = get_settings()
    
    # 根据数据库类型设置连接参数
    engine_kwargs = {
        "echo": settings.database.echo,
        "pool_pre_ping": True,
    }
    
    # 只有非SQLite数据库才支持连接池参数
    if not settings.database.url.startswith("sqlite"):
        engine_kwargs.update({
            "pool_size": settings.database.pool_size,
            "max_overflow": settings.database.max_overflow,
        })
    
    # 创建异步数据库引擎
    engine = create_async_engine(
        settings.database.url,
        **engine_kwargs
    )
    
    # 创建会话工厂
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("数据库初始化完成")


async def close_database() -> None:
    """关闭数据库连接"""
    global engine
    if engine:
        await engine.dispose()
        logger.info("数据库连接已关闭")


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话上下文管理器"""
    if AsyncSessionLocal is None:
        raise RuntimeError("数据库未初始化，请先调用 init_database()")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（用于 FastAPI 依赖注入）"""
    async with get_db_session() as session:
        yield session 