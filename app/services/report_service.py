"""
报告服务层
处理报告相关的业务逻辑
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, desc

from app.models.report import Report, ReportTemplate, TaskExecution, ReportType, ReportStatus, ReportFormat
from app.core.database import get_db_session


class ReportService:
    """报告服务类"""
    
    @staticmethod
    async def create_report(
        user_id: int,
        title: str,
        report_type: str,
        period_start: datetime,
        period_end: datetime,
        description: Optional[str] = None,
        format: str = ReportFormat.HTML,
        subscriptions_included: Optional[List[int]] = None
    ) -> Report:
        """创建新报告"""
        async with get_db_session() as session:
            report = Report(
                user_id=user_id,
                title=title,
                description=description,
                report_type=report_type,
                format=format,
                period_start=period_start,
                period_end=period_end,
                subscriptions_included=json.dumps(subscriptions_included or [])
            )
            session.add(report)
            await session.commit()
            await session.refresh(report)
            return report
    
    @staticmethod
    async def get_report(report_id: int) -> Optional[Report]:
        """根据ID获取报告"""
        async with get_db_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(Report)
                .options(selectinload(Report.user))
                .filter(Report.id == report_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_reports(
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        report_type: Optional[str] = None
    ) -> List[Report]:
        """获取用户的报告列表"""
        async with get_db_session() as session:
            query = session.query(Report).filter(Report.user_id == user_id)
            
            if status:
                query = query.filter(Report.status == status)
            
            if report_type:
                query = query.filter(Report.report_type == report_type)
            
            result = await session.execute(
                query.order_by(desc(Report.created_at))
                .offset(skip).limit(limit)
            )
            return result.scalars().all()
    
    @staticmethod
    async def get_all_reports(
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        report_type: Optional[str] = None
    ) -> List[Report]:
        """获取所有报告"""
        async with get_db_session() as session:
            from sqlalchemy import select
            
            query = select(Report)
            
            if status:
                query = query.filter(Report.status == status)
            
            if report_type:
                query = query.filter(Report.report_type == report_type)
            
            query = query.order_by(desc(Report.created_at)).offset(skip).limit(limit)
            
            result = await session.execute(query)
            return result.scalars().all()
    
    @staticmethod
    async def update_report(
        report_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        summary: Optional[str] = None,
        content: Optional[str] = None,
        ai_analysis: Optional[str] = None,
        raw_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> Optional[Report]:
        """更新报告"""
        async with get_db_session() as session:
            report = await session.get(Report, report_id)
            if not report:
                return None
            
            if title is not None:
                report.title = title
            if description is not None:
                report.description = description
            if status is not None:
                report.status = status
                if status == ReportStatus.COMPLETED:
                    report.generated_at = datetime.utcnow()
            if summary is not None:
                report.summary = summary
            if content is not None:
                report.content = content
            if ai_analysis is not None:
                report.ai_analysis = ai_analysis
            if raw_data is not None:
                report.raw_data = raw_data
            if error_message is not None:
                report.error_message = error_message
            
            await session.commit()
            await session.refresh(report)
            return report
    
    @staticmethod
    async def update_report_statistics(
        report_id: int,
        total_repositories: Optional[int] = None,
        total_activities: Optional[int] = None,
        total_commits: Optional[int] = None,
        total_issues: Optional[int] = None,
        total_pull_requests: Optional[int] = None,
        total_releases: Optional[int] = None
    ) -> Optional[Report]:
        """更新报告统计信息"""
        async with get_db_session() as session:
            report = await session.get(Report, report_id)
            if not report:
                return None
            
            if total_repositories is not None:
                report.total_repositories = total_repositories
            if total_activities is not None:
                report.total_activities = total_activities
            if total_commits is not None:
                report.total_commits = total_commits
            if total_issues is not None:
                report.total_issues = total_issues
            if total_pull_requests is not None:
                report.total_pull_requests = total_pull_requests
            if total_releases is not None:
                report.total_releases = total_releases
            
            await session.commit()
            await session.refresh(report)
            return report
    
    @staticmethod
    async def delete_report(report_id: int) -> bool:
        """删除报告"""
        async with get_db_session() as session:
            report = await session.get(Report, report_id)
            if not report:
                return False
            
            await session.delete(report)
            await session.commit()
            return True
    
    @staticmethod
    async def get_report_count(
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        report_type: Optional[str] = None
    ) -> int:
        """获取报告总数"""
        async with get_db_session() as session:
            from sqlalchemy import select, func
            
            query = select(func.count(Report.id))
            
            if user_id is not None:
                query = query.filter(Report.user_id == user_id)
            
            if status:
                query = query.filter(Report.status == status)
            
            if report_type:
                query = query.filter(Report.report_type == report_type)
            
            result = await session.execute(query)
            return result.scalar() or 0
    
    @staticmethod
    async def get_recent_reports(days: int = 7, limit: int = 10) -> List[Report]:
        """获取最近的报告"""
        async with get_db_session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            result = await session.execute(
                session.query(Report)
                .filter(Report.created_at >= cutoff_date)
                .order_by(desc(Report.created_at))
                .limit(limit)
            )
            return result.scalars().all()
    
    # 报告模板相关方法
    @staticmethod
    async def create_report_template(
        name: str,
        format: str,
        template_content: str,
        user_id: Optional[int] = None,
        description: Optional[str] = None,
        css_styles: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        variables: Optional[Dict[str, Any]] = None,
        is_default: bool = False
    ) -> ReportTemplate:
        """创建报告模板"""
        async with get_db_session() as session:
            template = ReportTemplate(
                user_id=user_id,
                name=name,
                description=description,
                format=format,
                template_content=template_content,
                css_styles=css_styles,
                config=config,
                variables=variables,
                is_default=is_default,
                is_system=user_id is None
            )
            session.add(template)
            await session.commit()
            await session.refresh(template)
            return template
    
    @staticmethod
    async def get_report_templates(
        user_id: Optional[int] = None,
        format: Optional[str] = None,
        is_system: Optional[bool] = None
    ) -> List[ReportTemplate]:
        """获取报告模板列表"""
        async with get_db_session() as session:
            query = session.query(ReportTemplate)
            
            if user_id is not None:
                # 获取用户自己的模板和系统模板
                query = query.filter(
                    or_(ReportTemplate.user_id == user_id, ReportTemplate.is_system == True)
                )
            
            if format:
                query = query.filter(ReportTemplate.format == format)
            
            if is_system is not None:
                query = query.filter(ReportTemplate.is_system == is_system)
            
            result = await session.execute(
                query.order_by(desc(ReportTemplate.is_default), desc(ReportTemplate.created_at))
            )
            return result.scalars().all()
    
    # 任务执行记录相关方法
    @staticmethod
    async def create_task_execution(
        task_name: str,
        task_type: str,
        status: str = "running"
    ) -> TaskExecution:
        """创建任务执行记录"""
        async with get_db_session() as session:
            execution = TaskExecution(
                task_name=task_name,
                task_type=task_type,
                status=status,
                started_at=datetime.utcnow()
            )
            session.add(execution)
            await session.commit()
            await session.refresh(execution)
            return execution
    
    @staticmethod
    async def update_task_execution(
        execution_id: int,
        status: Optional[str] = None,
        success_count: Optional[int] = None,
        error_count: Optional[int] = None,
        processed_count: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> Optional[TaskExecution]:
        """更新任务执行记录"""
        async with get_db_session() as session:
            execution = await session.get(TaskExecution, execution_id)
            if not execution:
                return None
            
            if status is not None:
                execution.status = status
                if status in ["completed", "failed"]:
                    execution.completed_at = datetime.utcnow()
                    if execution.started_at:
                        duration = execution.completed_at - execution.started_at
                        execution.duration_seconds = int(duration.total_seconds())
            
            if success_count is not None:
                execution.success_count = success_count
            if error_count is not None:
                execution.error_count = error_count
            if processed_count is not None:
                execution.processed_count = processed_count
            if details is not None:
                execution.details = details
            if error_message is not None:
                execution.error_message = error_message
            
            await session.commit()
            await session.refresh(execution)
            return execution 