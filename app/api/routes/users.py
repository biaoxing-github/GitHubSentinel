"""
用户相关的API路由
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.services.user_service import UserService
from app.schemas.user_schemas import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    """创建新用户"""
    try:
        logger.info(f"📝 开始创建用户: {user_data.username}")
        
        # 检查用户名和邮箱是否已存在
        existing_user = await UserService.get_user_by_username(user_data.username)
        if existing_user:
            logger.warning(f"❌ 用户名已存在: {user_data.username}")
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        existing_email = await UserService.get_user_by_email(user_data.email)
        if existing_email:
            logger.warning(f"❌ 邮箱已存在: {user_data.email}")
            raise HTTPException(status_code=400, detail="邮箱已存在")
        
        # 创建用户（实际应用中需要加密密码）
        user = await UserService.create_user(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=f"hashed_{user_data.password}"  # 临时实现
        )
        logger.info(f"✅ 用户创建成功: {user.username} (ID: {user.id})")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 创建用户失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")


@router.get("/", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="限制返回的记录数"),
    is_active: Optional[bool] = Query(None, description="是否活跃")
):
    """获取用户列表"""
    try:
        users = await UserService.get_users(skip=skip, limit=limit, is_active=is_active)
        total = await UserService.get_user_count(is_active=is_active)
        
        return UserListResponse(
            users=users,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """根据ID获取用户"""
    try:
        user = await UserService.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户失败: {str(e)}")


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate):
    """更新用户信息"""
    try:
        # 检查用户是否存在
        existing_user = await UserService.get_user(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 检查用户名和邮箱唯一性
        if user_data.username:
            username_user = await UserService.get_user_by_username(user_data.username)
            if username_user and username_user.id != user_id:
                raise HTTPException(status_code=400, detail="用户名已存在")
        
        if user_data.email:
            email_user = await UserService.get_user_by_email(user_data.email)
            if email_user and email_user.id != user_id:
                raise HTTPException(status_code=400, detail="邮箱已存在")
        
        # 更新用户
        updated_user = await UserService.update_user(
            user_id=user_id,
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            is_active=user_data.is_active,
            notification_email=user_data.notification_email,
            notification_slack=user_data.notification_slack,
            slack_webhook_url=user_data.slack_webhook_url
        )
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新用户失败: {str(e)}")


@router.delete("/{user_id}")
async def delete_user(user_id: int):
    """删除用户"""
    try:
        success = await UserService.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return {"message": "用户删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除用户失败: {str(e)}")


@router.get("/stats/count")
async def get_user_stats():
    """获取用户统计信息"""
    try:
        logger.info("📊 开始获取用户统计信息")
        
        total_users = await UserService.get_user_count()
        active_users = await UserService.get_user_count(is_active=True)
        inactive_users = await UserService.get_user_count(is_active=False)
        
        stats = {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users
        }
        
        logger.info(f"✅ 用户统计获取成功: {stats}")
        return stats
    except Exception as e:
        logger.error(f"💥 获取用户统计失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取用户统计失败: {str(e)}") 