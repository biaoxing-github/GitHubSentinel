import traceback
import asyncio
from app.core.database import init_database
from app.services.user_service import UserService
from app.services.subscription_service import SubscriptionService

async def test_services():
    try:
        print("正在初始化数据库...")
        await init_database()
        print("数据库初始化完成")
        
        print("测试用户服务...")
        count = await UserService.get_user_count()
        print(f'User count: {count}')
        
        print("测试订阅服务...")
        sub_count = await SubscriptionService.get_subscription_count()
        print(f'Subscription count: {sub_count}')
        
    except Exception as e:
        print(f'Error: {e}')
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_services())