"""
用户服务层
处理用户相关的业务逻辑
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.subscription import User
from app.core.database import get_db_session


class UserService:
    """用户服务类"""
    
    @staticmethod
    async def create_user(
        username: str,
        email: str,
        full_name: Optional[str] = None,
        hashed_password: Optional[str] = None,
        is_active: Optional[bool] = True,
        is_superuser: Optional[bool] = False,
        notification_email: Optional[bool] = True,
        notification_slack: Optional[bool] = False,
        slack_webhook_url: Optional[str] = None
    ) -> User:
        """创建新用户"""
        async with get_db_session() as session:
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                hashed_password=hashed_password or "temp_password",  # 实际应用中需要proper password hashing
                is_active=is_active,
                is_superuser=is_superuser,
                notification_email=notification_email,
                notification_slack=notification_slack,
                slack_webhook_url=slack_webhook_url
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
    
    @staticmethod
    async def get_user(user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        async with get_db_session() as session:
            user = await session.get(User, user_id)
            return user
    
    @staticmethod
    async def get_user_by_username(username: str) -> Optional[User]:
        """根据用户名获取用户"""
        async with get_db_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(User).filter(User.username == username)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        async with get_db_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(User).filter(User.email == email)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def get_users(
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """获取用户列表"""
        async with get_db_session() as session:
            from sqlalchemy import select
            query = select(User)
            
            if is_active is not None:
                query = query.filter(User.is_active == is_active)
            
            result = await session.execute(
                query.offset(skip).limit(limit)
            )
            return result.scalars().all()
    
    @staticmethod
    async def update_user(
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        is_active: Optional[bool] = None,
        notification_email: Optional[bool] = None,
        notification_slack: Optional[bool] = None,
        slack_webhook_url: Optional[str] = None
    ) -> Optional[User]:
        """更新用户信息"""
        async with get_db_session() as session:
            user = await session.get(User, user_id)
            if not user:
                return None
            
            if username is not None:
                user.username = username
            if email is not None:
                user.email = email
            if full_name is not None:
                user.full_name = full_name
            if is_active is not None:
                user.is_active = is_active
            if notification_email is not None:
                user.notification_email = notification_email
            if notification_slack is not None:
                user.notification_slack = notification_slack
            if slack_webhook_url is not None:
                user.slack_webhook_url = slack_webhook_url
            
            await session.commit()
            await session.refresh(user)
            return user
    
    @staticmethod
    async def delete_user(user_id: int) -> bool:
        """删除用户"""
        async with get_db_session() as session:
            user = await session.get(User, user_id)
            if not user:
                return False
            
            await session.delete(user)
            await session.commit()
            return True
    
    @staticmethod
    async def get_user_count(is_active: Optional[bool] = None) -> int:
        """获取用户总数"""
        async with get_db_session() as session:
            from sqlalchemy import select, func
            query = select(func.count(User.id))
            
            if is_active is not None:
                query = query.filter(User.is_active == is_active)
            
            result = await session.execute(query)
            return result.scalar() 