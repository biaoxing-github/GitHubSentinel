"""
报告服务层
处理报告相关的业务逻辑
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, desc, select, func

from app.models.report import Report, ReportTemplate, TaskExecution, ReportType, ReportStatus, ReportFormat
from app.models.subscription import User, Subscription, SubscriptionStatus, ReportFrequency
from app.core.database import get_db_session
from app.core.logger import get_logger
from app.services.ai_service import AIService
from app.services.notification_service import NotificationService

logger = get_logger(__name__)


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
        repository: Optional[str] = None,
        format: str = ReportFormat.HTML,
        subscriptions_included: Optional[List[int]] = None
    ) -> Report:
        """创建新报告"""
        async with get_db_session() as session:
            report = Report(
                user_id=user_id,
                title=title,
                description=description,
                repository=repository,
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
            query = select(Report).filter(Report.user_id == user_id)
            
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
                    report.generated_at = datetime.now()
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
            cutoff_date = datetime.now() - timedelta(days=days)
            result = await session.execute(
                select(Report)
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
            query = select(ReportTemplate)
            
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
                started_at=datetime.now()
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
                    execution.completed_at = datetime.now()
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
    
    @staticmethod
    async def _generate_user_daily_report(
        user: User, 
        subscriptions: List[Subscription], 
        ai_service: AIService
    ) -> Optional[Report]:
        """为用户生成每日报告"""
        from app.models.subscription import RepositoryActivity
        from app.utils.timezone_utils import beijing_now, format_beijing_time
        
        today = beijing_now().date()
        yesterday = today - timedelta(days=1)
        
        # 生成包含仓库信息的标题
        repo_names = [sub.repository for sub in subscriptions]
        if len(repo_names) == 1:
            title = f"{repo_names[0]} - 每日报告 ({today.strftime('%Y-%m-%d')})"
        else:
            title = f"多仓库每日报告 ({len(repo_names)}个仓库) - {today.strftime('%Y-%m-%d')}"
        
        # 创建报告记录
        report = await ReportService.create_report(
            user_id=user.id,
            title=title,
            report_type=ReportType.DAILY,
            period_start=datetime.combine(yesterday, datetime.min.time()),
            period_end=datetime.combine(today, datetime.min.time()),
            description=f"用户 {user.username} 的每日GitHub活动报告 - 监控仓库: {', '.join(repo_names)}",
            format=ReportFormat.HTML
        )
        return report

    @staticmethod
    async def _send_report_notifications(
        report: Report,
        subscriptions: List[Subscription],
        notification_service: NotificationService
    ) -> None:
        """发送报告通知"""
        try:
            from app.utils.timezone_utils import format_beijing_time
            
            # 生成报告邮件内容
            email_subject = f"📊 GitHub Sentinel 每日报告 - {format_beijing_time(report.period_start, '%Y年%m月%d日')}"
            
            # 为每个订阅发送报告通知
            for subscription in subscriptions:
                # 检查是否启用邮件通知
                if not subscription.enable_email_notification:
                    continue
                
                # 获取通知邮箱列表
                notification_emails = []
                if subscription.notification_emails:
                    try:
                        notification_emails = json.loads(subscription.notification_emails)
                    except:
                        pass
                
                if not notification_emails:
                    continue
                
                # 生成邮件内容
                email_content = ReportService._generate_report_email_content(report, subscription)
                
                # 发送邮件
                for email in notification_emails:
                    try:
                        await notification_service.send_email_notification(
                            to_email=email,
                            subject=email_subject,
                            content=email_content,
                            content_type="html"
                        )
                        logger.info(f"✅ 报告邮件发送成功: {email}")
                    except Exception as e:
                        logger.error(f"💥 发送报告邮件失败 {email}: {e}")
                
                # 发送其他类型的通知
                report_data = {
                    "report_id": report.id,
                    "report_title": report.title,
                    "report_summary": report.summary or "每日GitHub活动报告",
                    "report_url": f"/reports/{report.id}",
                    "period_start": report.period_start.isoformat(),
                    "period_end": report.period_end.isoformat(),
                    "repository": subscription.repository
                }
                
                await notification_service.send_subscription_notification(
                    subscription,
                    report_data,
                    "report"
                )
                
        except Exception as e:
            logger.error(f"发送报告通知失败: {e}")

    @staticmethod
    def _generate_report_email_content(report: Report, subscription: Subscription) -> str:
        """生成报告邮件内容"""
        from app.utils.timezone_utils import format_beijing_time
        
        # 如果报告有HTML内容，直接使用
        if report.content and report.format == "html":
            return report.content
        
        # 否则生成简单的邮件内容
        email_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>GitHub Sentinel 每日报告</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #007bff;
                    margin-bottom: 20px;
                }}
                .footer {{
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e9ecef;
                }}
                .btn {{
                    display: inline-block;
                    padding: 12px 24px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 500;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 GitHub Sentinel 每日报告</h1>
                <p>仓库: {subscription.repository}</p>
                <p>日期: {format_beijing_time(report.period_start, '%Y年%m月%d日')}</p>
            </div>
            
            <div class="content">
                <h2>📋 报告摘要</h2>
                <p>{report.summary or '每日GitHub活动报告已生成'}</p>
                
                <h3>📊 统计信息</h3>
                <ul>
                    <li>监控仓库: {report.total_repositories or 1} 个</li>
                    <li>总活动数: {report.total_activities or 0} 项</li>
                    <li>代码提交: {report.total_commits or 0} 次</li>
                    <li>Issues: {report.total_issues or 0} 个</li>
                    <li>Pull Requests: {report.total_pull_requests or 0} 个</li>
                    <li>版本发布: {report.total_releases or 0} 个</li>
                </ul>
                
                <p style="text-align: center; margin-top: 20px;">
                    <a href="http://localhost:5173/reports/{report.id}" class="btn">查看完整报告</a>
                </p>
            </div>
            
            <div class="footer">
                <p>📅 报告生成时间: {format_beijing_time(report.created_at) if report.created_at else '未知'}</p>
                <p>🤖 由 GitHub Sentinel 自动生成并发送</p>
                <p>如不想接收此类邮件，请在系统中修改通知设置</p>
            </div>
        </body>
        </html>
        """
        
        return email_content 

    @staticmethod
    async def get_report_count_by_period(
        start_time: datetime,
        end_time: datetime,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        report_type: Optional[str] = None
    ) -> int:
        """按时间段获取报告数量"""
        async with get_db_session() as session:
            query = select(func.count(Report.id)).filter(
                and_(
                    Report.created_at >= start_time,
                    Report.created_at <= end_time
                )
            )
            
            if user_id:
                query = query.filter(Report.user_id == user_id)
            
            if status:
                query = query.filter(Report.status == status)
            
            if report_type:
                query = query.filter(Report.report_type == report_type)
            
            result = await session.execute(query)
            return result.scalar() or 0 