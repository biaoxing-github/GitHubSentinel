"""
简化认证模块
专门处理开发环境的demo_token认证
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import jwt
import os

from app.models.subscription import User
from app.core.logger import get_logger
from app.core.config import get_settings

logger = get_logger(__name__)

# HTTP Bearer 认证方案
bearer_scheme = HTTPBearer()

# 全局引擎
_engine = None
_SessionLocal = None

def get_sync_engine():
    """获取同步数据库引擎"""
    global _engine, _SessionLocal
    
    if _engine is None:
        settings = get_settings()
        # 为认证模块使用简化的sqlite数据库
        sync_url = "sqlite:///./github_sentinel.db"
            
        _engine = create_engine(sync_url, echo=False)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        
        # 创建表（如果不存在）
        from app.core.database import Base
        Base.metadata.create_all(_engine)
    
    return _SessionLocal()

def get_or_create_demo_user() -> User:
    """获取或创建demo用户"""
    db = get_sync_engine()
    try:
        # 查找现有demo用户
        user = db.query(User).filter(User.email == "demo@example.com").first()
        
        if not user:
            # 创建demo用户
            user = User(
                username="demo_user",
                email="demo@example.com", 
                full_name="Demo User",
                hashed_password="demo_password",
                is_active=True,
                is_superuser=False
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info("Created demo user for development")
        
        return user
    except Exception as e:
        logger.error(f"Error getting/creating demo user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> User:
    """获取当前认证用户 - 简化版本"""
    try:
        token = credentials.credentials
        
        # 在开发环境中，接受demo_token
        if token == "demo_token":
            return get_or_create_demo_user()
        
        # 其他token也返回demo用户（开发模式）
        logger.warning(f"Unknown token '{token}', using demo user")
        return get_or_create_demo_user()
        
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        # 开发环境容错
        return get_or_create_demo_user()

async def get_user_from_token(token: str, db: Session = None) -> Optional[User]:
    """从token获取用户 - 简化版本"""
    try:
        if token == "demo_token":
            return get_or_create_demo_user()
        
        # 其他情况也返回demo用户
        logger.warning(f"Unknown token '{token}', using demo user")
        return get_or_create_demo_user()
        
    except Exception as e:
        logger.error(f"Error getting user from token: {e}")
        return get_or_create_demo_user() 