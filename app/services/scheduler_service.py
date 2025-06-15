"""
定时任务服务
负责定期收集GitHub数据并更新数据库
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.core.logger import get_logger
from app.core.database import get_db_session
from app.models.subscription import Subscription, RepositoryActivity
from app.services.subscription_service import SubscriptionService
from app.collectors.github_collector import GitHubCollector
from app.utils.timezone_utils import beijing_now
from sqlalchemy import select

logger = get_logger(__name__)


class SchedulerService:
    """定时任务服务"""
    
    def __init__(self):
        self.github_collector = GitHubCollector()
        self.is_running = False
    
    async def start_scheduler(self):
        """启动定时任务调度器"""
        if self.is_running:
            logger.warning("⚠️ 定时任务调度器已在运行")
            return
        
        self.is_running = True
        logger.info("🚀 启动定时任务调度器")
        
        # 启动数据收集任务
        asyncio.create_task(self._data_collection_loop())
        
    async def stop_scheduler(self):
        """停止定时任务调度器"""
        self.is_running = False
        logger.info("🛑 停止定时任务调度器")
    
    async def _data_collection_loop(self):
        """数据收集循环 - 每分钟执行一次"""
        while self.is_running:
            try:
                await self.collect_repository_data()
                # 等待60秒
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"💥 数据收集循环出错: {e}", exc_info=True)
                # 出错后等待30秒再重试
                await asyncio.sleep(30)
    
    async def collect_repository_data(self):
        """收集仓库数据"""
        try:
            logger.info("📊 开始定时收集仓库数据")
            
            # 获取所有活跃订阅
            async with get_db_session() as session:
                result = await session.execute(
                    select(Subscription).where(Subscription.status == "active")
                )
                subscriptions = result.scalars().all()
            
            if not subscriptions:
                logger.info("📭 没有活跃的订阅，跳过数据收集")
                return
            
            logger.info(f"📋 找到 {len(subscriptions)} 个活跃订阅")
            
            success_count = 0
            error_count = 0
            
            for subscription in subscriptions:
                try:
                    await self._collect_subscription_data(subscription)
                    success_count += 1
                except Exception as e:
                    logger.error(f"💥 收集订阅 {subscription.id} 数据失败: {e}", exc_info=True)
                    error_count += 1
            
            logger.info(f"✅ 数据收集完成 - 成功: {success_count}, 失败: {error_count}")
            
        except Exception as e:
            logger.error(f"💥 收集仓库数据失败: {e}", exc_info=True)
    
    async def _collect_subscription_data(self, subscription: Subscription):
        """收集单个订阅的数据"""
        try:
            logger.info(f"📊 收集订阅数据: {subscription.repository}")
            
            # 解析仓库信息
            repo_parts = subscription.repository.split('/')
            if len(repo_parts) != 2:
                logger.error(f"❌ 仓库格式错误: {subscription.repository}")
                return
            
            owner, repo = repo_parts
            
            # 收集最近1天的活动数据（GitHub收集器会自动存储到数据库）
            activities_data = await self.github_collector.collect_repository_activities(
                subscription, 
                days=1,  # 收集最近1天的数据，但会过滤重复
                include_states=['open', 'closed', 'merged']
            )
            
            # 记录收集结果
            if activities_data.get('activities'):
                logger.info(f"✅ 收集并存储了 {len(activities_data['activities'])} 条活动记录")
            else:
                logger.info(f"📭 没有新的活动数据")
            
        except Exception as e:
            logger.error(f"💥 收集订阅 {subscription.id} 数据失败: {e}", exc_info=True)
            raise
    
    async def _store_activities(self, activities: List[Dict[str, Any]]):
        """存储活动数据到数据库"""
        try:
            async with get_db_session() as session:
                stored_count = 0
                
                for activity_data in activities:
                    # 检查是否已存在相同的活动
                    existing = await session.execute(
                        select(RepositoryActivity).where(
                            RepositoryActivity.subscription_id == activity_data['subscription_id'],
                            RepositoryActivity.activity_id == activity_data['activity_id'],
                            RepositoryActivity.activity_type == activity_data['activity_type']
                        )
                    )
                    
                    if existing.scalar():
                        continue  # 跳过已存在的活动
                    
                    # 创建新的活动记录
                    activity = RepositoryActivity(
                        subscription_id=activity_data['subscription_id'],
                        repository_full_name=activity_data['repository_full_name'],
                        activity_type=activity_data['activity_type'],
                        activity_id=activity_data['activity_id'],
                        title=activity_data.get('title'),
                        description=activity_data.get('description'),
                        url=activity_data.get('url'),
                        author_login=activity_data.get('author_login'),
                        author_name=activity_data.get('author_name'),
                        state=activity_data.get('state'),
                        github_created_at=activity_data.get('github_created_at'),
                        created_at=beijing_now()
                    )
                    
                    session.add(activity)
                    stored_count += 1
                
                await session.commit()
                
                if stored_count > 0:
                    logger.info(f"💾 存储了 {stored_count} 条新活动记录")
                
        except Exception as e:
            logger.error(f"💥 存储活动数据失败: {e}", exc_info=True)
            raise
    
    async def _update_subscription_sync_time(self, subscription_id: int):
        """更新订阅的最后同步时间"""
        try:
            async with get_db_session() as session:
                result = await session.execute(
                    select(Subscription).where(Subscription.id == subscription_id)
                )
                subscription = result.scalar()
                
                if subscription:
                    subscription.last_sync_at = beijing_now()
                    await session.commit()
                    
        except Exception as e:
            logger.error(f"💥 更新订阅同步时间失败: {e}", exc_info=True)
    
    async def get_dashboard_statistics(self) -> Dict[str, Any]:
        """获取 Dashboard 统计数据"""
        try:
            async with get_db_session() as session:
                # 获取最近24小时的活动统计
                cutoff_time = beijing_now() - timedelta(hours=24)
                
                # 按活动类型统计
                activity_stats = {}
                for activity_type in ['commit', 'issue', 'pull_request', 'release']:
                    result = await session.execute(
                        select(RepositoryActivity).where(
                            RepositoryActivity.activity_type == activity_type,
                            RepositoryActivity.created_at >= cutoff_time
                        )
                    )
                    count = len(result.scalars().all())
                    activity_stats[activity_type] = count
                
                # 获取最活跃的仓库
                from sqlalchemy import func
                result = await session.execute(
                    select(
                        RepositoryActivity.repository_full_name,
                        func.count(RepositoryActivity.id).label('activity_count')
                    ).where(
                        RepositoryActivity.created_at >= cutoff_time
                    ).group_by(
                        RepositoryActivity.repository_full_name
                    ).order_by(
                        func.count(RepositoryActivity.id).desc()
                    ).limit(10)
                )
                
                top_repositories = []
                for row in result:
                    top_repositories.append({
                        'name': row.repository_full_name,
                        'activity_count': row.activity_count
                    })
                
                return {
                    'activity_stats': activity_stats,
                    'top_repositories': top_repositories,
                    'last_updated': beijing_now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"💥 获取 Dashboard 统计数据失败: {e}")
            return {
                'activity_stats': {},
                'top_repositories': [],
                'last_updated': beijing_now().isoformat()
            }


# 全局调度器实例
scheduler_service = SchedulerService() 