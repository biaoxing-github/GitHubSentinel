"""
订阅服务层
处理订阅相关的业务逻辑
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, desc, select

from app.models.subscription import Subscription, RepositoryActivity, SubscriptionStatus, ReportFrequency
from app.core.database import get_db_session


class SubscriptionService:
    """订阅服务类"""

    @staticmethod
    async def create_subscription(
            user_id: int,
            repository: str,
            frequency: str = ReportFrequency.DAILY,
            status: str = SubscriptionStatus.ACTIVE,
            monitor_commits: bool = True,
            monitor_issues: bool = True,
            monitor_pull_requests: bool = True,
            monitor_releases: bool = True,
            monitor_discussions: bool = False,
            repository_description: Optional[str] = None,
            repository_url: Optional[str] = None,
            repository_language: Optional[str] = None,
            repository_stars: Optional[int] = None,
            repository_forks: Optional[int] = None,
            notification_emails: Optional[List[str]] = None,
            notification_slack_webhooks: Optional[List[str]] = None,
            notification_custom_webhooks: Optional[List[str]] = None,
            enable_email_notification: bool = True,
            enable_slack_notification: bool = False,
            enable_webhook_notification: bool = False
    ) -> Subscription:
        """创建新订阅"""
        async with get_db_session() as session:
            subscription = Subscription(
                user_id=user_id,
                repository=repository,
                repository_full_name=repository,
                frequency=frequency,
                status=status,
                monitor_commits=monitor_commits,
                monitor_issues=monitor_issues,
                monitor_pull_requests=monitor_pull_requests,
                monitor_releases=monitor_releases,
                monitor_discussions=monitor_discussions,
                repository_description=repository_description,
                repository_url=repository_url,
                repository_language=repository_language,
                repository_stars=repository_stars,
                repository_forks=repository_forks,
                notification_emails=json.dumps(notification_emails) if notification_emails else None,
                notification_slack_webhooks=json.dumps(
                    notification_slack_webhooks) if notification_slack_webhooks else None,
                notification_custom_webhooks=json.dumps(
                    notification_custom_webhooks) if notification_custom_webhooks else None,
                enable_email_notification=enable_email_notification,
                enable_slack_notification=enable_slack_notification,
                enable_webhook_notification=enable_webhook_notification
            )
            session.add(subscription)
            await session.commit()
            await session.refresh(subscription)
            return subscription

    @staticmethod
    async def get_subscription(subscription_id: int) -> Optional[Subscription]:
        """根据ID获取订阅"""
        async with get_db_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(Subscription)
                .options(selectinload(Subscription.user))
                .filter(Subscription.id == subscription_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_user_subscriptions(
            user_id: int,
            skip: int = 0,
            limit: int = 100,
            status: Optional[str] = None
    ) -> List[Subscription]:
        """获取用户的订阅列表"""
        async with get_db_session() as session:
            from sqlalchemy import select
            query = select(Subscription).filter(Subscription.user_id == user_id)

            if status:
                query = query.filter(Subscription.status == status)

            result = await session.execute(
                query.order_by(desc(Subscription.created_at))
                .offset(skip).limit(limit)
            )
            return result.scalars().all()

    @staticmethod
    async def get_all_subscriptions(
            skip: int = 0,
            limit: int = 100,
            status: Optional[str] = None,
            repository: Optional[str] = None
    ) -> List[Subscription]:
        """获取所有订阅"""
        async with get_db_session() as session:
            from sqlalchemy import select
            query = select(Subscription)

            if status:
                query = query.filter(Subscription.status == status)

            if repository:
                query = query.filter(Subscription.repository.ilike(f"%{repository}%"))

            result = await session.execute(
                query.order_by(desc(Subscription.created_at))
                .offset(skip).limit(limit)
            )
            return result.scalars().all()

    @staticmethod
    async def update_subscription(
            subscription_id: int,
            status: Optional[str] = None,
            frequency: Optional[str] = None,
            monitor_commits: Optional[bool] = None,
            monitor_issues: Optional[bool] = None,
            monitor_pull_requests: Optional[bool] = None,
            monitor_releases: Optional[bool] = None,
            monitor_discussions: Optional[bool] = None,
            exclude_authors: Optional[List[str]] = None,
            include_labels: Optional[List[str]] = None,
            exclude_labels: Optional[List[str]] = None,
            notification_emails: Optional[List[str]] = None,
            notification_slack_webhooks: Optional[List[str]] = None,
            notification_custom_webhooks: Optional[List[str]] = None,
            enable_email_notification: Optional[bool] = None,
            enable_slack_notification: Optional[bool] = None,
            enable_webhook_notification: Optional[bool] = None
    ) -> Optional[Subscription]:
        """更新订阅"""
        async with get_db_session() as session:
            subscription = await session.get(Subscription, subscription_id)
            if not subscription:
                return None

            if status is not None:
                subscription.status = status
            if frequency is not None:
                subscription.frequency = frequency
            if monitor_commits is not None:
                subscription.monitor_commits = monitor_commits
            if monitor_issues is not None:
                subscription.monitor_issues = monitor_issues
            if monitor_pull_requests is not None:
                subscription.monitor_pull_requests = monitor_pull_requests
            if monitor_releases is not None:
                subscription.monitor_releases = monitor_releases
            if monitor_discussions is not None:
                subscription.monitor_discussions = monitor_discussions

            # 处理JSON字段
            if exclude_authors is not None:
                subscription.exclude_authors = json.dumps(exclude_authors)
            if include_labels is not None:
                subscription.include_labels = json.dumps(include_labels)
            if exclude_labels is not None:
                subscription.exclude_labels = json.dumps(exclude_labels)

            # 处理通知配置
            if notification_emails is not None:
                subscription.notification_emails = json.dumps(notification_emails)
            if notification_slack_webhooks is not None:
                subscription.notification_slack_webhooks = json.dumps(notification_slack_webhooks)
            if notification_custom_webhooks is not None:
                subscription.notification_custom_webhooks = json.dumps(notification_custom_webhooks)
            if enable_email_notification is not None:
                subscription.enable_email_notification = enable_email_notification
            if enable_slack_notification is not None:
                subscription.enable_slack_notification = enable_slack_notification
            if enable_webhook_notification is not None:
                subscription.enable_webhook_notification = enable_webhook_notification

            await session.commit()
            await session.refresh(subscription)
            return subscription

    @staticmethod
    async def delete_subscription(subscription_id: int) -> bool:
        """删除订阅"""
        async with get_db_session() as session:
            subscription = await session.get(Subscription, subscription_id)
            if not subscription:
                return False

            await session.delete(subscription)
            await session.commit()
            return True

    @staticmethod
    async def update_repository_info(
            subscription_id: int,
            repository_description: Optional[str] = None,
            repository_url: Optional[str] = None,
            repository_language: Optional[str] = None,
            repository_stars: Optional[int] = None,
            repository_forks: Optional[int] = None
    ) -> Optional[Subscription]:
        """更新仓库信息"""
        async with get_db_session() as session:
            subscription = await session.get(Subscription, subscription_id)
            if not subscription:
                return None

            if repository_description is not None:
                subscription.repository_description = repository_description
            if repository_url is not None:
                subscription.repository_url = repository_url
            if repository_language is not None:
                subscription.repository_language = repository_language
            if repository_stars is not None:
                subscription.repository_stars = repository_stars
            if repository_forks is not None:
                subscription.repository_forks = repository_forks

            subscription.last_sync_at = datetime.now()

            await session.commit()
            await session.refresh(subscription)
            return subscription

    @staticmethod
    async def get_subscription_count(
            user_id: Optional[int] = None,
            status: Optional[str] = None
    ) -> int:
        """获取订阅总数"""
        async with get_db_session() as session:
            from sqlalchemy import select, func
            query = select(func.count(Subscription.id))

            if user_id is not None:
                query = query.filter(Subscription.user_id == user_id)

            if status:
                query = query.filter(Subscription.status == status)

            result = await session.execute(query)
            return result.scalar()

    @staticmethod
    async def get_active_subscriptions() -> List[Subscription]:
        """获取所有活跃的订阅"""
        async with get_db_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(Subscription)
                .filter(Subscription.status == SubscriptionStatus.ACTIVE)
                .order_by(desc(Subscription.created_at))
            )
            return result.scalars().all()

    @staticmethod
    async def add_repository_activity(
            subscription_id: int,
            activity_type: str,
            activity_id: str,
            title: Optional[str] = None,
            description: Optional[str] = None,
            url: Optional[str] = None,
            author_login: Optional[str] = None,
            author_name: Optional[str] = None,
            github_created_at: Optional[datetime] = None,
            **kwargs
    ) -> RepositoryActivity:
        """添加仓库活动记录"""
        async with get_db_session() as session:
            activity = RepositoryActivity(
                subscription_id=subscription_id,
                activity_type=activity_type,
                activity_id=activity_id,
                title=title,
                description=description,
                url=url,
                author_login=author_login,
                author_name=author_name,
                github_created_at=github_created_at,
                **kwargs
            )
            session.add(activity)
            await session.commit()
            await session.refresh(activity)
            return activity

    @staticmethod
    async def get_subscription_activities(
            subscription_id: int,
            activity_type: Optional[str] = None,
            skip: int = 0,
            limit: int = 100
    ) -> List[RepositoryActivity]:
        """获取订阅的活动记录"""
        async with get_db_session() as session:
            from sqlalchemy import select
            query = select(RepositoryActivity).filter(
                RepositoryActivity.subscription_id == subscription_id
            )

            if activity_type:
                query = query.filter(RepositoryActivity.activity_type == activity_type)

            result = await session.execute(
                query.order_by(desc(RepositoryActivity.github_created_at))
                .offset(skip).limit(limit)
            )
            return result.scalars().all()

    @staticmethod
    async def get_recent_subscriptions(days: int = 7, limit: int = 10) -> List[Subscription]:
        """获取最近的订阅"""
        async with get_db_session() as session:
            cutoff_date = datetime.now() - timedelta(days=days)
            result = await session.execute(
                select(Subscription)
                .filter(Subscription.created_at >= cutoff_date)
                .order_by(desc(Subscription.created_at))
                .limit(limit)
            )
            return result.scalars().all()
