"""
用户相关的数据模式定义
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    full_name: Optional[str] = Field(None, description="全名")


class UserCreate(UserBase):
    """创建用户模式"""
    password: str = Field(..., min_length=6, description="密码")


class UserUpdate(BaseModel):
    """更新用户模式"""
    username: Optional[str] = Field(None, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    full_name: Optional[str] = Field(None, description="全名")
    is_active: Optional[bool] = Field(None, description="是否活跃")
    notification_email: Optional[bool] = Field(None, description="邮件通知")
    notification_slack: Optional[bool] = Field(None, description="Slack通知")
    slack_webhook_url: Optional[str] = Field(None, description="Slack Webhook URL")


class UserResponse(UserBase):
    """用户响应模式"""
    id: int
    is_active: bool
    is_superuser: bool
    notification_email: bool
    notification_slack: bool
    slack_webhook_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应模式"""
    users: List[UserResponse]
    total: int
    skip: int
    limit: int 