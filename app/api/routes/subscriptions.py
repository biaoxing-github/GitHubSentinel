"""
订阅相关的API路由
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from app.services.subscription_service import SubscriptionService
from app.collectors.github_collector import GitHubCollector
from app.schemas.subscription_schemas import (
    SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse, 
    SubscriptionListResponse, RepositoryActivityResponse
)
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/", response_model=SubscriptionResponse)
async def create_subscription(subscription_data: SubscriptionCreate, background_tasks: BackgroundTasks):
    """创建新订阅"""
    try:
        subscription = await SubscriptionService.create_subscription(
            user_id=subscription_data.user_id,
            repository=subscription_data.repository,
            frequency=subscription_data.frequency,
            monitor_commits=subscription_data.monitor_commits,
            monitor_issues=subscription_data.monitor_issues,
            monitor_pull_requests=subscription_data.monitor_pull_requests,
            monitor_releases=subscription_data.monitor_releases,
            monitor_discussions=subscription_data.monitor_discussions
        )
        
        # 后台任务：获取仓库基本信息
        background_tasks.add_task(update_repository_info, subscription.id, subscription_data.repository)
        
        return subscription
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建订阅失败: {str(e)}")


@router.get("/", response_model=SubscriptionListResponse)
async def get_subscriptions(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="限制返回的记录数"),
    status: Optional[str] = Query(None, description="订阅状态"),
    repository: Optional[str] = Query(None, description="仓库名称")
):
    """获取所有订阅列表"""
    try:
        subscriptions = await SubscriptionService.get_all_subscriptions(
            skip=skip, limit=limit, status=status, repository=repository
        )
        total = await SubscriptionService.get_subscription_count(status=status)
        
        return SubscriptionListResponse(
            subscriptions=subscriptions,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取订阅列表失败: {str(e)}")


@router.get("/user/{user_id}", response_model=SubscriptionListResponse)
async def get_user_subscriptions(
    user_id: int,
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="限制返回的记录数"),
    status: Optional[str] = Query(None, description="订阅状态")
):
    """获取用户的订阅列表"""
    try:
        subscriptions = await SubscriptionService.get_user_subscriptions(
            user_id=user_id, skip=skip, limit=limit, status=status
        )
        total = await SubscriptionService.get_subscription_count(user_id=user_id, status=status)
        
        return SubscriptionListResponse(
            subscriptions=subscriptions,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户订阅列表失败: {str(e)}")


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(subscription_id: int):
    """根据ID获取订阅"""
    try:
        subscription = await SubscriptionService.get_subscription(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="订阅不存在")
        return subscription
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取订阅失败: {str(e)}")


@router.put("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(subscription_id: int, subscription_data: SubscriptionUpdate):
    """更新订阅"""
    try:
        updated_subscription = await SubscriptionService.update_subscription(
            subscription_id=subscription_id,
            status=subscription_data.status,
            frequency=subscription_data.frequency,
            monitor_commits=subscription_data.monitor_commits,
            monitor_issues=subscription_data.monitor_issues,
            monitor_pull_requests=subscription_data.monitor_pull_requests,
            monitor_releases=subscription_data.monitor_releases,
            monitor_discussions=subscription_data.monitor_discussions,
            exclude_authors=subscription_data.exclude_authors,
            include_labels=subscription_data.include_labels,
            exclude_labels=subscription_data.exclude_labels,
            notification_emails=subscription_data.notification_emails,
            notification_slack_webhooks=subscription_data.notification_slack_webhooks,
            notification_custom_webhooks=subscription_data.notification_custom_webhooks,
            enable_email_notification=subscription_data.enable_email_notification,
            enable_slack_notification=subscription_data.enable_slack_notification,
            enable_webhook_notification=subscription_data.enable_webhook_notification
        )
        
        if not updated_subscription:
            raise HTTPException(status_code=404, detail="订阅不存在")
        
        return updated_subscription
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新订阅失败: {str(e)}")


@router.delete("/{subscription_id}")
async def delete_subscription(subscription_id: int):
    """删除订阅"""
    try:
        success = await SubscriptionService.delete_subscription(subscription_id)
        if not success:
            raise HTTPException(status_code=404, detail="订阅不存在")
        
        return {"message": "订阅删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除订阅失败: {str(e)}")


@router.get("/{subscription_id}/activities", response_model=List[RepositoryActivityResponse])
async def get_subscription_activities(
    subscription_id: int,
    activity_type: Optional[str] = Query(None, description="活动类型"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="限制返回的记录数")
):
    """获取订阅的活动记录"""
    try:
        activities = await SubscriptionService.get_subscription_activities(
            subscription_id=subscription_id,
            activity_type=activity_type,
            skip=skip,
            limit=limit
        )
        return activities
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取活动记录失败: {str(e)}")


@router.post("/{subscription_id}/sync")
async def sync_subscription(subscription_id: int, background_tasks: BackgroundTasks):
    """手动同步订阅数据"""
    try:
        subscription = await SubscriptionService.get_subscription(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="订阅不存在")
        
        # 后台任务：同步数据
        background_tasks.add_task(sync_subscription_data, subscription_id, subscription.repository)
        
        return {"message": "数据同步已开始"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步数据失败: {str(e)}")


@router.get("/stats/summary")
async def get_subscription_stats():
    """获取订阅统计信息"""
    try:
        logger.info("📊 开始获取订阅统计信息")
        
        total_subscriptions = await SubscriptionService.get_subscription_count()
        active_subscriptions = await SubscriptionService.get_subscription_count(status="active")
        paused_subscriptions = await SubscriptionService.get_subscription_count(status="paused")
        
        stats = {
            "total_subscriptions": total_subscriptions,
            "active_subscriptions": active_subscriptions,
            "paused_subscriptions": paused_subscriptions
        }
        
        logger.info(f"✅ 订阅统计获取成功: {stats}")
        return stats
    except Exception as e:
        logger.error(f"💥 获取订阅统计失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取订阅统计失败: {str(e)}")


# 后台任务函数
async def update_repository_info(subscription_id: int, repository: str):
    """更新仓库基本信息"""
    try:
        collector = GitHubCollector()
        repo_info = await collector.get_repository_info(repository)
        
        if repo_info:
            await SubscriptionService.update_repository_info(
                subscription_id=subscription_id,
                repository_description=repo_info.get("description"),
                repository_url=repo_info.get("html_url"),
                repository_language=repo_info.get("language"),
                repository_stars=repo_info.get("stargazers_count"),
                repository_forks=repo_info.get("forks_count")
            )
    except Exception as e:
        print(f"更新仓库信息失败: {e}")


async def sync_subscription_data(subscription_id: int, repository: str):
    """同步订阅数据"""
    try:
        collector = GitHubCollector()
        # 这里可以添加具体的数据同步逻辑
        # 例如获取最新的commits, issues, PRs等
        print(f"正在同步仓库 {repository} 的数据...")
    except Exception as e:
        print(f"同步数据失败: {e}") 