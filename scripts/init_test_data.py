#!/usr/bin/env python3
"""
初始化测试数据脚本
创建一些示例用户和订阅数据用于测试
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from app.core.database import init_database
from app.services.user_service import UserService
from app.services.subscription_service import SubscriptionService


async def create_test_users():
    """创建测试用户"""
    logger.info("🧑‍💻 开始创建测试用户...")
    
    test_users = [
        {
            "username": "admin",
            "email": "admin@example.com",
            "full_name": "系统管理员",
            "hashed_password": "hashed_admin123",
            "is_active": True,
            "notification_email": True,
            "notification_slack": False
        },
        {
            "username": "developer",
            "email": "dev@example.com", 
            "full_name": "开发者",
            "hashed_password": "hashed_dev123",
            "is_active": True,
            "notification_email": True,
            "notification_slack": True
        },
        {
            "username": "tester",
            "email": "test@example.com",
            "full_name": "测试员",
            "hashed_password": "hashed_test123",
            "is_active": False,
            "notification_email": False,
            "notification_slack": False
        }
    ]
    
    created_users = []
    for user_data in test_users:
        try:
            # 检查用户是否已存在
            existing_user = await UserService.get_user_by_username(user_data["username"])
            if existing_user:
                logger.info(f"用户 {user_data['username']} 已存在，跳过创建")
                created_users.append(existing_user)
                continue
                
            user = await UserService.create_user(**user_data)
            created_users.append(user)
            logger.info(f"✅ 创建用户: {user.username} (ID: {user.id})")
        except Exception as e:
            logger.error(f"❌ 创建用户失败 {user_data['username']}: {str(e)}")
    
    return created_users


async def create_test_subscriptions(users):
    """创建测试订阅"""
    logger.info("📋 开始创建测试订阅...")
    
    if not users:
        logger.warning("没有用户，无法创建订阅")
        return []
    
    test_subscriptions = [
        {
            "user_id": users[0].id,
            "repository": "langchain-ai/langchain",
            "frequency": "daily",
            "monitor_commits": True,
            "monitor_issues": True,
            "monitor_pull_requests": True,
            "monitor_releases": True,
            "monitor_discussions": False,
            "status": "active"
        },
        {
            "user_id": users[0].id,
            "repository": "microsoft/vscode",
            "frequency": "weekly",
            "monitor_commits": False,
            "monitor_issues": True,
            "monitor_pull_requests": True,
            "monitor_releases": True,
            "monitor_discussions": False,
            "status": "active"
        },
        {
            "user_id": users[1].id if len(users) > 1 else users[0].id,
            "repository": "vuejs/vue",
            "frequency": "daily",
            "monitor_commits": True,
            "monitor_issues": False,
            "monitor_pull_requests": True,
            "monitor_releases": True,
            "monitor_discussions": False,
            "status": "paused"
        }
    ]
    
    created_subscriptions = []
    for sub_data in test_subscriptions:
        try:
            # 检查订阅是否已存在
            existing_subs = await SubscriptionService.get_user_subscriptions(
                user_id=sub_data["user_id"], 
                skip=0, 
                limit=100
            )
            
            # 检查是否已有相同仓库的订阅
            repo_exists = any(sub.repository == sub_data["repository"] for sub in existing_subs)
            if repo_exists:
                logger.info(f"用户 {sub_data['user_id']} 已订阅 {sub_data['repository']}，跳过创建")
                continue
                
            subscription = await SubscriptionService.create_subscription(**sub_data)
            created_subscriptions.append(subscription)
            logger.info(f"✅ 创建订阅: {subscription.repository} (ID: {subscription.id})")
        except Exception as e:
            logger.error(f"❌ 创建订阅失败 {sub_data['repository']}: {str(e)}")
    
    return created_subscriptions


async def main():
    """主函数"""
    logger.info("🚀 开始初始化测试数据...")
    
    try:
        # 初始化数据库
        await init_database()
        logger.info("✅ 数据库初始化完成")
        
        # 创建测试用户
        users = await create_test_users()
        logger.info(f"✅ 创建了 {len(users)} 个用户")
        
        # 创建测试订阅
        subscriptions = await create_test_subscriptions(users)
        logger.info(f"✅ 创建了 {len(subscriptions)} 个订阅")
        
        # 显示统计信息
        total_users = await UserService.get_user_count()
        active_users = await UserService.get_user_count(is_active=True)
        total_subscriptions = await SubscriptionService.get_subscription_count()
        active_subscriptions = await SubscriptionService.get_subscription_count(status="active")
        
        logger.info("📊 当前数据统计:")
        logger.info(f"  总用户数: {total_users}")
        logger.info(f"  活跃用户数: {active_users}")
        logger.info(f"  总订阅数: {total_subscriptions}")
        logger.info(f"  活跃订阅数: {active_subscriptions}")
        
        logger.info("🎉 测试数据初始化完成！")
        
    except Exception as e:
        logger.error(f"💥 初始化测试数据失败: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # 配置日志
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
    )
    
    asyncio.run(main()) 