"""
任务调度器
使用 APScheduler 实现定时任务管理
"""

import asyncio
from datetime import datetime, time
from typing import List, Dict, Any, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from loguru import logger
import pytz

from app.core.config import get_settings
from app.core.database import get_db_session
from app.models.subscription import User, Subscription, SubscriptionStatus
from app.models.report import TaskExecution


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.timezone = pytz.timezone(self.settings.schedule.timezone)
        
    async def start(self) -> None:
        """启动调度器"""
        if not self.settings.schedule.enabled:
            logger.info("任务调度器已禁用")
            return
            
        # 配置调度器
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=self.timezone
        )
        
        # 添加定时任务
        await self._add_scheduled_jobs()
        
        # 启动调度器
        self.scheduler.start()
        logger.info("任务调度器启动成功")
        
    async def stop(self) -> None:
        """停止调度器"""
        if self.scheduler:
            self.scheduler.shutdown(wait=True)
            logger.info("任务调度器已停止")
            
    async def _add_scheduled_jobs(self) -> None:
        """添加定时任务"""
        
        # 每日数据收集任务
        daily_time = time.fromisoformat(self.settings.schedule.daily_time)
        self.scheduler.add_job(
            self._daily_collection_task,
            CronTrigger(
                hour=daily_time.hour,
                minute=daily_time.minute,
                timezone=self.timezone
            ),
            id='daily_collection',
            name='每日数据收集',
            replace_existing=True
        )
        
        # 每周数据收集任务
        weekly_time = time.fromisoformat(self.settings.schedule.weekly_time)
        self.scheduler.add_job(
            self._weekly_collection_task,
            CronTrigger(
                day_of_week=self.settings.schedule.weekly_day - 1,  # APScheduler 使用 0-6
                hour=weekly_time.hour,
                minute=weekly_time.minute,
                timezone=self.timezone
            ),
            id='weekly_collection',
            name='每周数据收集',
            replace_existing=True
        )
        
        # 每小时清理任务
        self.scheduler.add_job(
            self._cleanup_task,
            CronTrigger(minute=0, timezone=self.timezone),
            id='hourly_cleanup',
            name='每小时清理任务',
            replace_existing=True
        )
        
        # 每日报告生成任务
        self.scheduler.add_job(
            self._daily_report_task,
            CronTrigger(
                hour=(daily_time.hour + 1) % 24,  # 数据收集后1小时
                minute=0,
                timezone=self.timezone
            ),
            id='daily_report',
            name='每日报告生成',
            replace_existing=True
        )
        
        logger.info("定时任务已添加")
        
    async def _daily_collection_task(self) -> None:
        """每日数据收集任务"""
        task_name = "每日数据收集"
        execution_id = await self._start_task_execution(task_name, "collection")
        
        try:
            logger.info("开始执行每日数据收集任务")
            
            # 导入收集器（避免循环导入）
            from app.collectors.github_collector import GitHubCollector
            
            collector = GitHubCollector()
            result = await collector.collect_daily_updates()
            
            await self._complete_task_execution(
                execution_id, 
                success_count=result.get('success_count', 0),
                error_count=result.get('error_count', 0),
                details=result
            )
            
            logger.info(f"每日数据收集任务完成: {result}")
            
        except Exception as e:
            logger.error(f"每日数据收集任务失败: {e}")
            await self._fail_task_execution(execution_id, str(e))
            
    async def _weekly_collection_task(self) -> None:
        """每周数据收集任务"""
        task_name = "每周数据收集"
        execution_id = await self._start_task_execution(task_name, "collection")
        
        try:
            logger.info("开始执行每周数据收集任务")
            
            from app.collectors.github_collector import GitHubCollector
            
            collector = GitHubCollector()
            result = await collector.collect_weekly_updates()
            
            await self._complete_task_execution(
                execution_id,
                success_count=result.get('success_count', 0),
                error_count=result.get('error_count', 0),
                details=result
            )
            
            logger.info(f"每周数据收集任务完成: {result}")
            
        except Exception as e:
            logger.error(f"每周数据收集任务失败: {e}")
            await self._fail_task_execution(execution_id, str(e))
            
    async def _daily_report_task(self) -> None:
        """每日报告生成任务"""
        task_name = "每日报告生成"
        execution_id = await self._start_task_execution(task_name, "report")
        
        try:
            logger.info("开始执行每日报告生成任务")
            
            from app.services.report_service import ReportService
            
            report_service = ReportService()
            result = await report_service.generate_daily_reports()
            
            await self._complete_task_execution(
                execution_id,
                success_count=result.get('success_count', 0),
                error_count=result.get('error_count', 0),
                details=result
            )
            
            logger.info(f"每日报告生成任务完成: {result}")
            
        except Exception as e:
            logger.error(f"每日报告生成任务失败: {e}")
            await self._fail_task_execution(execution_id, str(e))
            
    async def _cleanup_task(self) -> None:
        """清理任务"""
        task_name = "数据清理"
        execution_id = await self._start_task_execution(task_name, "cleanup")
        
        try:
            logger.info("开始执行数据清理任务")
            
            from app.services.cleanup_service import CleanupService
            
            cleanup_service = CleanupService()
            result = await cleanup_service.cleanup_old_data()
            
            await self._complete_task_execution(
                execution_id,
                processed_count=result.get('processed_count', 0),
                details=result
            )
            
            logger.info(f"数据清理任务完成: {result}")
            
        except Exception as e:
            logger.error(f"数据清理任务失败: {e}")
            await self._fail_task_execution(execution_id, str(e))
            
    async def _start_task_execution(self, task_name: str, task_type: str) -> int:
        """开始任务执行记录"""
        async with get_db_session() as session:
            execution = TaskExecution(
                task_name=task_name,
                task_type=task_type,
                status="running",
                started_at=datetime.utcnow()
            )
            session.add(execution)
            await session.flush()
            return execution.id
            
    async def _complete_task_execution(
        self, 
        execution_id: int, 
        success_count: int = 0,
        error_count: int = 0,
        processed_count: int = 0,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """完成任务执行记录"""
        async with get_db_session() as session:
            execution = await session.get(TaskExecution, execution_id)
            if execution:
                now = datetime.utcnow()
                execution.status = "completed"
                execution.completed_at = now
                execution.duration_seconds = int((now - execution.started_at).total_seconds())
                execution.success_count = success_count
                execution.error_count = error_count
                execution.processed_count = processed_count
                execution.details = details
                
    async def _fail_task_execution(self, execution_id: int, error_message: str) -> None:
        """失败任务执行记录"""
        async with get_db_session() as session:
            execution = await session.get(TaskExecution, execution_id)
            if execution:
                now = datetime.utcnow()
                execution.status = "failed"
                execution.completed_at = now
                execution.duration_seconds = int((now - execution.started_at).total_seconds())
                execution.error_message = error_message
                
    async def add_one_time_job(
        self, 
        func, 
        run_date: datetime, 
        job_id: str,
        args: tuple = None,
        kwargs: dict = None
    ) -> None:
        """添加一次性任务"""
        if self.scheduler:
            self.scheduler.add_job(
                func,
                'date',
                run_date=run_date,
                id=job_id,
                args=args,
                kwargs=kwargs,
                replace_existing=True
            )
            logger.info(f"已添加一次性任务: {job_id}")
            
    async def remove_job(self, job_id: str) -> None:
        """移除任务"""
        if self.scheduler:
            try:
                self.scheduler.remove_job(job_id)
                logger.info(f"已移除任务: {job_id}")
            except Exception as e:
                logger.warning(f"移除任务失败 {job_id}: {e}")
                
    def get_jobs(self) -> List[Dict[str, Any]]:
        """获取所有任务信息"""
        if not self.scheduler:
            return []
            
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs 