#!/usr/bin/env python3
"""
添加测试订阅数据的脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.subscription_service import SubscriptionService
from app.core.logger import get_logger

logger = get_logger(__name__)

async def add_test_subscriptions():
    """添加测试订阅数据"""
    test_subscriptions = [
        {
            "repository": "microsoft/vscode",
            "user_id": 1,
            "frequency": "daily",
            "status": "active"
        },
        {
            "repository": "facebook/react",
            "user_id": 1,
            "frequency": "weekly",
            "status": "active"
        },
        {
            "repository": "vuejs/vue",
            "user_id": 1,
            "frequency": "daily",
            "status": "active"
        },
        {
            "repository": "tensorflow/tensorflow",
            "user_id": 1,
            "frequency": "weekly",
            "status": "active"
        },
        {
            "repository": "pytorch/pytorch",
            "user_id": 1,
            "frequency": "daily",
            "status": "active"
        }
    ]
    
    logger.info("🚀 开始添加测试订阅数据...")
    
    for sub_data in test_subscriptions:
        try:
            # 检查是否已存在
            existing_subs = await SubscriptionService.get_all_subscriptions(
                repository=sub_data["repository"]
            )
            
            if existing_subs:
                logger.info(f"⏭️ 订阅已存在: {sub_data['repository']}")
                continue
            
            # 创建订阅
            subscription = await SubscriptionService.create_subscription(
                user_id=sub_data["user_id"],
                repository=sub_data["repository"],
                frequency=sub_data["frequency"],
                status=sub_data["status"],
                monitor_commits=True,
                monitor_issues=True,
                monitor_pull_requests=True,
                monitor_releases=True,
                monitor_discussions=False
            )
            
            logger.info(f"✅ 成功添加订阅: {subscription.repository} (ID: {subscription.id})")
            
        except Exception as e:
            logger.error(f"❌ 添加订阅失败 {sub_data['repository']}: {e}")
    
    # 显示统计信息
    total_count = await SubscriptionService.get_subscription_count()
    active_count = await SubscriptionService.get_subscription_count(status="active")
    
    logger.info(f"📊 订阅统计: 总数 {total_count}, 活跃 {active_count}")

if __name__ == "__main__":
    asyncio.run(add_test_subscriptions()) 