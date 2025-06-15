"""
报告相关的 Pydantic 模型
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ReportBase(BaseModel):
    """报告基础模型"""
    title: str = Field(..., description="报告标题")
    report_type: str = Field(..., description="报告类型")


class ReportCreate(ReportBase):
    """创建报告的请求模型"""
    subscription_id: int = Field(..., description="订阅ID")
    template_id: Optional[int] = Field(None, description="模板ID")


class ReportUpdate(BaseModel):
    """更新报告的请求模型"""
    title: Optional[str] = Field(None, description="报告标题")
    content: Optional[str] = Field(None, description="报告内容")
    status: Optional[str] = Field(None, description="报告状态")


class ReportResponse(ReportBase):
    """报告响应模型"""
    id: int = Field(..., description="报告ID")
    user_id: int = Field(..., description="用户ID")
    description: Optional[str] = Field(None, description="报告描述")
    status: str = Field(..., description="报告状态")
    format: str = Field(..., description="报告格式")
    period_start: datetime = Field(..., description="报告开始时间")
    period_end: datetime = Field(..., description="报告结束时间")
    summary: Optional[str] = Field(None, description="报告摘要")
    content: Optional[str] = Field(None, description="报告内容")
    ai_analysis: Optional[str] = Field(None, description="AI分析结果")
    total_repositories: int = Field(0, description="总仓库数")
    total_activities: int = Field(0, description="总活动数")
    total_commits: int = Field(0, description="总提交数")
    total_issues: int = Field(0, description="总Issue数")
    total_pull_requests: int = Field(0, description="总PR数")
    total_releases: int = Field(0, description="总发布数")
    file_path: Optional[str] = Field(None, description="文件路径")
    file_size: Optional[int] = Field(None, description="文件大小")
    sent_at: Optional[datetime] = Field(None, description="发送时间")
    error_message: Optional[str] = Field(None, description="错误信息")
    retry_count: int = Field(0, description="重试次数")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    generated_at: Optional[datetime] = Field(None, description="生成完成时间")

    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    """报告列表响应模型"""
    reports: List[ReportResponse] = Field(..., description="报告列表")
    total: int = Field(..., description="总数量")
    skip: int = Field(..., description="跳过数量")
    limit: int = Field(..., description="限制数量")


class ReportTemplateBase(BaseModel):
    """报告模板基础模型"""
    name: str = Field(..., description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    template_content: str = Field(..., description="模板内容")
    report_type: str = Field(..., description="报告类型")


class ReportTemplateCreate(ReportTemplateBase):
    """创建报告模板的请求模型"""
    pass


class ReportTemplateUpdate(BaseModel):
    """更新报告模板的请求模型"""
    name: Optional[str] = Field(None, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    template_content: Optional[str] = Field(None, description="模板内容")
    report_type: Optional[str] = Field(None, description="报告类型")
    is_active: Optional[bool] = Field(None, description="是否激活")


class ReportTemplateResponse(ReportTemplateBase):
    """报告模板响应模型"""
    id: int = Field(..., description="模板ID")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True 