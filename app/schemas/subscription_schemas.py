"""
订阅相关的数据模式定义
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class SubscriptionBase(BaseModel):
    """订阅基础模式"""
    repository: str = Field(..., description="仓库名称 (owner/repo)")
    frequency: str = Field("daily", description="报告频率")
    monitor_commits: bool = Field(True, description="监控提交")
    monitor_issues: bool = Field(True, description="监控Issue")
    monitor_pull_requests: bool = Field(True, description="监控PR")
    monitor_releases: bool = Field(True, description="监控发布")
    monitor_discussions: bool = Field(False, description="监控讨论")
    notification_emails: Optional[List[str]] = Field(None, description="通知邮箱列表")
    notification_slack_webhooks: Optional[List[str]] = Field(None, description="Slack Webhook URL列表")
    notification_custom_webhooks: Optional[List[str]] = Field(None, description="自定义Webhook URL列表")
    enable_email_notification: bool = Field(True, description="是否启用邮件通知")
    enable_slack_notification: bool = Field(False, description="是否启用Slack通知")
    enable_webhook_notification: bool = Field(False, description="是否启用Webhook通知")


class SubscriptionCreate(SubscriptionBase):
    """创建订阅模式"""
    user_id: int = Field(..., description="用户ID")


class SubscriptionUpdate(BaseModel):
    """更新订阅模式"""
    status: Optional[str] = Field(None, description="订阅状态")
    frequency: Optional[str] = Field(None, description="报告频率")
    monitor_commits: Optional[bool] = Field(None, description="监控提交")
    monitor_issues: Optional[bool] = Field(None, description="监控Issue")
    monitor_pull_requests: Optional[bool] = Field(None, description="监控PR")
    monitor_releases: Optional[bool] = Field(None, description="监控发布")
    monitor_discussions: Optional[bool] = Field(None, description="监控讨论")
    exclude_authors: Optional[List[str]] = Field(None, description="排除的作者")
    include_labels: Optional[List[str]] = Field(None, description="包含的标签")
    exclude_labels: Optional[List[str]] = Field(None, description="排除的标签")
    notification_emails: Optional[List[str]] = Field(None, description="通知邮箱列表")
    notification_slack_webhooks: Optional[List[str]] = Field(None, description="Slack Webhook URL列表")
    notification_custom_webhooks: Optional[List[str]] = Field(None, description="自定义Webhook URL列表")
    enable_email_notification: Optional[bool] = Field(None, description="是否启用邮件通知")
    enable_slack_notification: Optional[bool] = Field(None, description="是否启用Slack通知")
    enable_webhook_notification: Optional[bool] = Field(None, description="是否启用Webhook通知")


class SubscriptionResponse(SubscriptionBase):
    """订阅响应模式"""
    id: int
    user_id: int
    status: str
    repository_full_name: Optional[str]
    repository_description: Optional[str]
    repository_url: Optional[str]
    repository_language: Optional[str]
    repository_stars: Optional[int]
    repository_forks: Optional[int]
    exclude_authors: Optional[str] = None  # JSON字符串
    include_labels: Optional[str] = None   # JSON字符串
    exclude_labels: Optional[str] = None   # JSON字符串
    notification_emails: Optional[str] = None  # JSON字符串
    notification_slack_webhooks: Optional[str] = None  # JSON字符串
    notification_custom_webhooks: Optional[str] = None  # JSON字符串
    created_at: datetime
    updated_at: Optional[datetime]
    last_sync_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SubscriptionListResponse(BaseModel):
    """订阅列表响应模式"""
    subscriptions: List[SubscriptionResponse]
    total: int
    skip: int
    limit: int


class RepositoryActivityResponse(BaseModel):
    """仓库活动响应模式"""
    id: int
    subscription_id: int
    activity_type: str
    activity_id: str
    title: Optional[str]
    description: Optional[str]
    url: Optional[str]
    author_login: Optional[str]
    author_name: Optional[str]
    state: Optional[str]
    github_created_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True 