"""
订阅模型定义
管理用户订阅的 GitHub 仓库信息
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class SubscriptionStatus(str, Enum):
    """订阅状态枚举"""
    ACTIVE = "active"      # 活跃
    PAUSED = "paused"      # 暂停
    INACTIVE = "inactive"  # 非活跃


class ReportFrequency(str, Enum):
    """报告频率枚举"""
    DAILY = "daily"        # 每日
    WEEKLY = "weekly"      # 每周
    MONTHLY = "monthly"    # 每月


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(255), unique=True, index=True, nullable=False, comment="邮箱")
    full_name = Column(String(200), comment="全名")
    hashed_password = Column(String(255), comment="加密密码")
    is_active = Column(Boolean, default=True, comment="是否活跃")
    is_superuser = Column(Boolean, default=False, comment="是否超级用户")
    
    # 通知偏好
    notification_email = Column(Boolean, default=True, comment="是否启用邮件通知")
    notification_slack = Column(Boolean, default=False, comment="是否启用Slack通知")
    slack_webhook_url = Column(String(500), comment="Slack Webhook URL")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    last_login = Column(DateTime(timezone=True), comment="最后登录时间")
    
    # 关系
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user")


class Subscription(Base):
    """订阅模型"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    
    # 仓库信息
    repository = Column(String(200), nullable=False, index=True, comment="仓库名称 (owner/repo)")
    repository_full_name = Column(String(200), comment="仓库全名")
    repository_description = Column(Text, comment="仓库描述")
    repository_url = Column(String(500), comment="仓库URL")
    repository_language = Column(String(50), comment="主要编程语言")
    repository_stars = Column(Integer, default=0, comment="Star数量")
    repository_forks = Column(Integer, default=0, comment="Fork数量")
    
    # 订阅配置
    status = Column(String(20), default=SubscriptionStatus.ACTIVE, comment="订阅状态")
    frequency = Column(String(20), default=ReportFrequency.DAILY, comment="报告频率")
    
    # 监控配置
    monitor_commits = Column(Boolean, default=True, comment="监控提交")
    monitor_issues = Column(Boolean, default=True, comment="监控Issue")
    monitor_pull_requests = Column(Boolean, default=True, comment="监控PR")
    monitor_releases = Column(Boolean, default=True, comment="监控发布")
    monitor_discussions = Column(Boolean, default=False, comment="监控讨论")
    
    # 过滤配置
    exclude_authors = Column(Text, comment="排除的作者列表（JSON）")
    include_labels = Column(Text, comment="包含的标签列表（JSON）")
    exclude_labels = Column(Text, comment="排除的标签列表（JSON）")
    
    # 通知配置
    notification_emails = Column(Text, comment="通知邮箱列表（JSON）")
    notification_slack_webhooks = Column(Text, comment="Slack Webhook URL列表（JSON）")
    notification_custom_webhooks = Column(Text, comment="自定义Webhook URL列表（JSON）")
    enable_email_notification = Column(Boolean, default=True, comment="是否启用邮件通知")
    enable_slack_notification = Column(Boolean, default=False, comment="是否启用Slack通知")
    enable_webhook_notification = Column(Boolean, default=False, comment="是否启用Webhook通知")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间") 
    last_sync_at = Column(DateTime(timezone=True), comment="最后同步时间")
    
    # 关系
    user = relationship("User", back_populates="subscriptions")
    activities = relationship("RepositoryActivity", back_populates="subscription", cascade="all, delete-orphan")


class RepositoryActivity(Base):
    """仓库活动记录模型"""
    __tablename__ = "repository_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False, comment="订阅ID")
    
    # 活动基本信息
    activity_type = Column(String(50), nullable=False, index=True, comment="活动类型")
    activity_id = Column(String(100), nullable=False, comment="活动ID（GitHub ID）")
    title = Column(String(500), comment="标题")
    description = Column(Text, comment="描述")
    url = Column(String(500), comment="活动URL")
    
    # 作者信息
    author_login = Column(String(100), comment="作者用户名")
    author_name = Column(String(200), comment="作者姓名")
    author_avatar_url = Column(String(500), comment="作者头像URL")
    
    # 活动详情
    body = Column(Text, comment="活动内容")
    labels = Column(Text, comment="标签（JSON）")
    assignees = Column(Text, comment="指派人员（JSON）")
    milestone = Column(String(200), comment="里程碑")
    
    # 统计信息
    comments_count = Column(Integer, default=0, comment="评论数")
    reactions_count = Column(Integer, default=0, comment="反应数")
    
    # 状态信息
    state = Column(String(50), comment="状态（open/closed等）")
    is_draft = Column(Boolean, default=False, comment="是否草稿")
    is_merged = Column(Boolean, default=False, comment="是否已合并（PR）")
    
    # 时间信息
    github_created_at = Column(DateTime(timezone=True), comment="GitHub创建时间")
    github_updated_at = Column(DateTime(timezone=True), comment="GitHub更新时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="本地创建时间")
    
    # 关系
    subscription = relationship("Subscription", back_populates="activities")
    
    # 创建复合索引
    __table_args__ = (
        {'comment': '仓库活动记录'},
    ) 