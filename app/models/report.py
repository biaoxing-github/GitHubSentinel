"""
报告模型定义
管理生成的报告信息
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.utils.timezone_utils import beijing_now


class ReportType(str, Enum):
    """报告类型枚举"""
    DAILY = "daily"      # 每日报告
    WEEKLY = "weekly"    # 每周报告
    MONTHLY = "monthly"  # 每月报告
    CUSTOM = "custom"    # 自定义报告


class ReportStatus(str, Enum):
    """报告状态枚举"""
    PENDING = "pending"      # 待生成
    GENERATING = "generating" # 生成中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"        # 生成失败
    SENT = "sent"            # 已发送


class ReportFormat(str, Enum):
    """报告格式枚举"""
    HTML = "html"
    MARKDOWN = "markdown"
    JSON = "json"
    PDF = "pdf"


class Report(Base):
    """报告模型"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    
    # 报告基本信息
    title = Column(String(500), nullable=False, comment="报告标题")
    description = Column(Text, comment="报告描述")
    repository = Column(String(200), comment="关联的仓库名称 (owner/repo)")
    report_type = Column(String(20), nullable=False, comment="报告类型")
    status = Column(String(20), default=ReportStatus.PENDING, comment="报告状态")
    format = Column(String(20), default=ReportFormat.HTML, comment="报告格式")
    
    # 报告时间范围
    period_start = Column(DateTime(timezone=True), nullable=False, comment="报告开始时间")
    period_end = Column(DateTime(timezone=True), nullable=False, comment="报告结束时间")
    
    # 报告内容
    summary = Column(Text, comment="报告摘要")
    content = Column(Text, comment="报告内容")
    ai_analysis = Column(Text, comment="AI分析结果")
    raw_data = Column(JSON, comment="原始数据（JSON）")
    
    # 统计信息
    total_repositories = Column(Integer, default=0, comment="总仓库数")
    total_activities = Column(Integer, default=0, comment="总活动数")
    total_commits = Column(Integer, default=0, comment="总提交数")
    total_issues = Column(Integer, default=0, comment="总Issue数")
    total_pull_requests = Column(Integer, default=0, comment="总PR数")
    total_releases = Column(Integer, default=0, comment="总发布数")
    
    # 文件信息
    file_path = Column(String(1000), comment="报告文件路径")
    file_size = Column(Integer, comment="文件大小（字节）")
    file_hash = Column(String(100), comment="文件哈希值")
    
    # 发送信息
    sent_at = Column(DateTime(timezone=True), comment="发送时间")
    sent_to = Column(JSON, comment="发送目标（JSON）")
    notification_channels = Column(JSON, comment="通知渠道（JSON）")
    
    # 错误信息
    error_message = Column(Text, comment="错误信息")
    retry_count = Column(Integer, default=0, comment="重试次数")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), default=beijing_now, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=beijing_now, comment="更新时间")
    generated_at = Column(DateTime(timezone=True), comment="生成完成时间")
    
    # 关系
    user = relationship("User", back_populates="reports")
    subscriptions_included = Column(JSON, comment="包含的订阅ID列表（JSON）")


class ReportTemplate(Base):
    """报告模板模型"""
    __tablename__ = "report_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="用户ID（为空表示系统模板）")
    
    # 模板基本信息
    name = Column(String(200), nullable=False, comment="模板名称")
    description = Column(Text, comment="模板描述")
    format = Column(String(20), nullable=False, comment="模板格式")
    is_default = Column(Boolean, default=False, comment="是否默认模板")
    is_system = Column(Boolean, default=False, comment="是否系统模板")
    
    # 模板内容
    template_content = Column(Text, nullable=False, comment="模板内容")
    css_styles = Column(Text, comment="CSS样式（HTML模板用）")
    
    # 模板配置
    config = Column(JSON, comment="模板配置（JSON）")
    variables = Column(JSON, comment="模板变量定义（JSON）")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), default=beijing_now, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=beijing_now, comment="更新时间")
    
    # 关系（如果有用户ID）
    user = relationship("User", foreign_keys=[user_id])


class TaskExecution(Base):
    """任务执行记录模型"""
    __tablename__ = "task_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 任务基本信息
    task_name = Column(String(200), nullable=False, comment="任务名称")
    task_type = Column(String(50), nullable=False, comment="任务类型")
    status = Column(String(20), nullable=False, comment="执行状态")
    
    # 执行信息
    started_at = Column(DateTime(timezone=True), nullable=False, comment="开始时间")
    completed_at = Column(DateTime(timezone=True), comment="完成时间")
    duration_seconds = Column(Integer, comment="执行时长（秒）")
    
    # 结果信息
    success_count = Column(Integer, default=0, comment="成功数量")
    error_count = Column(Integer, default=0, comment="错误数量")
    processed_count = Column(Integer, default=0, comment="处理数量")
    
    # 详细信息
    details = Column(JSON, comment="执行详情（JSON）")
    error_message = Column(Text, comment="错误信息")
    log_data = Column(Text, comment="日志数据")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), default=beijing_now, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=beijing_now, comment="更新时间") 