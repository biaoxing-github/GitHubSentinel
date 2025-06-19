"""
报告生成进度跟踪服务
支持WebSocket实时进度推送
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Callable, Optional
from enum import Enum

from app.core.logger import get_logger

logger = get_logger(__name__)


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 等待中
    RUNNING = "running"      # 执行中  
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 已取消


class ReportProgressService:
    """报告生成进度服务"""
    
    def __init__(self):
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.progress_callbacks: Dict[str, Callable] = {}
    
    def register_progress_callback(self, task_id: str, callback: Callable):
        """注册进度回调函数（用于WebSocket推送）"""
        self.progress_callbacks[task_id] = callback
        logger.info(f"已注册任务 {task_id} 的进度回调")
    
    def unregister_progress_callback(self, task_id: str):
        """取消注册进度回调"""
        if task_id in self.progress_callbacks:
            del self.progress_callbacks[task_id]
            logger.info(f"已取消任务 {task_id} 的进度回调")
    
    async def update_progress(
        self, 
        task_id: str, 
        progress: int, 
        status: TaskStatus, 
        message: str = "", 
        data: Optional[Dict[str, Any]] = None
    ):
        """更新任务进度"""
        # 更新任务状态
        self.active_tasks[task_id] = {
            "task_id": task_id,
            "progress": progress,
            "status": status.value,
            "message": message,
            "data": data or {},
            "updated_at": datetime.now().isoformat()
        }
        
        # 推送进度更新
        if task_id in self.progress_callbacks:
            try:
                callback = self.progress_callbacks[task_id]
                await callback({
                    "type": "progress_update",
                    "task_id": task_id,
                    "progress": progress,
                    "status": status.value,
                    "message": message,
                    "data": data or {},
                    "timestamp": datetime.now().isoformat()
                })
                logger.info(f"已推送任务 {task_id} 进度: {progress}% - {message}")
            except Exception as e:
                logger.error(f"推送任务 {task_id} 进度失败: {e}")
    
    async def start_task(self, task_id: str, task_name: str = ""):
        """开始任务"""
        await self.update_progress(
            task_id, 
            0, 
            TaskStatus.RUNNING, 
            f"开始执行任务: {task_name}"
        )
    
    async def complete_task(self, task_id: str, result_data: Optional[Dict[str, Any]] = None):
        """完成任务"""
        await self.update_progress(
            task_id, 
            100, 
            TaskStatus.COMPLETED, 
            "任务执行完成",
            result_data
        )
        
        # 清理回调
        self.unregister_progress_callback(task_id)
    
    async def fail_task(self, task_id: str, error_message: str):
        """任务失败"""
        await self.update_progress(
            task_id, 
            0, 
            TaskStatus.FAILED, 
            f"任务执行失败: {error_message}"
        )
        
        # 清理回调
        self.unregister_progress_callback(task_id)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        return self.active_tasks.get(task_id)
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """获取所有任务状态"""
        return self.active_tasks.copy()
    
    async def cancel_task(self, task_id: str):
        """取消任务"""
        await self.update_progress(
            task_id, 
            0, 
            TaskStatus.CANCELLED, 
            "任务已取消"
        )
        
        # 清理回调
        self.unregister_progress_callback(task_id)


# 全局进度服务实例
progress_service = ReportProgressService()


async def simulate_report_generation(
    task_id: str, 
    report_type: str = "monthly",
    repo_name: str = "unknown"
) -> Dict[str, Any]:
    """真实报告生成过程（集成实际业务逻辑）"""
    from app.api.routes.reports import generate_report_content
    from app.services.report_service import ReportService
    from app.services.subscription_service import SubscriptionService
    from datetime import datetime, timedelta
    from app.utils.timezone_utils import beijing_now
    
    try:
        await progress_service.start_task(task_id, f"生成 {repo_name} 的 {report_type} 报告")
        
        # 步骤1: 初始化和验证 (10%)
        await asyncio.sleep(0.5)
        await progress_service.update_progress(
            task_id, 10, TaskStatus.RUNNING, "初始化报告生成..."
        )
        
        # 查找对应的订阅
        subscriptions = await SubscriptionService.get_all_subscriptions()
        subscription = None
        for sub in subscriptions:
            if repo_name in sub.repository:
                subscription = sub
                break
        
        # 步骤2: 创建报告记录 (20%)
        await asyncio.sleep(0.5)
        await progress_service.update_progress(
            task_id, 20, TaskStatus.RUNNING, "创建报告记录..."
        )
        
        # 设置时间范围
        beijing_end = beijing_now()
        if report_type == "daily":
            beijing_start = beijing_end - timedelta(days=1)
        elif report_type == "weekly":
            beijing_start = beijing_end - timedelta(weeks=1)
        else:
            beijing_start = beijing_end - timedelta(days=1)
        
        subscription_id = subscription.id if subscription else 1
        
        # 创建报告记录
        report = await ReportService.create_report(
            user_id=subscription.user_id if subscription else 1,
            title=f"{repo_name} {report_type.title()} Report",
            description=f"Generated {report_type} report for {repo_name}",
            repository=repo_name,
            report_type=report_type,
            format="html",
            period_start=beijing_start,
            period_end=beijing_end,
            subscriptions_included=[subscription_id]
        )
        
        # 步骤3: 收集仓库数据 (50%)
        await asyncio.sleep(1.5)
        await progress_service.update_progress(
            task_id, 50, TaskStatus.RUNNING, "正在收集仓库数据..."
        )
        
        # 步骤4: 分析数据和AI处理 (80%)
        await asyncio.sleep(2)
        await progress_service.update_progress(
            task_id, 80, TaskStatus.RUNNING, "正在分析数据并生成AI洞察..."
        )
        
        # 调用真实的报告生成逻辑
        await generate_report_content(report.id)
        
        # 步骤5: 完成报告生成 (100%)
        await asyncio.sleep(0.5)
        await progress_service.update_progress(
            task_id, 95, TaskStatus.RUNNING, "正在完成报告生成..."
        )
        
        # 重新获取更新后的报告
        updated_report = await ReportService.get_report(report.id)
        
        report_data = {
            "report_id": updated_report.id,
            "repo_name": repo_name,
            "report_type": report_type,
            "title": updated_report.title,
            "status": updated_report.status,
            "generated_at": updated_report.updated_at.isoformat() if updated_report.updated_at else datetime.now().isoformat(),
            "statistics": {
                "total_commits": updated_report.total_commits,
                "total_issues": updated_report.total_issues,
                "total_prs": updated_report.total_pull_requests,
                "total_activities": updated_report.total_activities,
                "total_releases": updated_report.total_releases
            },
            "summary": updated_report.summary or f"{repo_name} 在本{report_type}期间表现活跃。",
            "content_length": len(updated_report.content) if updated_report.content else 0,
            "has_ai_analysis": bool(updated_report.ai_analysis)
        }
        
        await progress_service.complete_task(task_id, {"report": report_data})
        
        logger.info(f"报告生成完成: {task_id}, 报告ID: {report.id}")
        return report_data
        
    except Exception as e:
        await progress_service.fail_task(task_id, str(e))
        logger.error(f"报告生成失败: {task_id} - {e}")
        raise


async def simulate_ai_analysis(
    task_id: str, 
    analysis_type: str = "comprehensive",
    repo_name: str = "unknown"
) -> Dict[str, Any]:
    """模拟AI分析过程（带进度推送）"""
    try:
        await progress_service.start_task(task_id, f"AI分析 {repo_name} - {analysis_type}")
        
        # 步骤1: 预处理数据 (15%)
        await asyncio.sleep(0.8)
        await progress_service.update_progress(
            task_id, 15, TaskStatus.RUNNING, "正在预处理代码和数据..."
        )
        
        # 步骤2: 代码质量分析 (35%)
        await asyncio.sleep(1.2)
        await progress_service.update_progress(
            task_id, 35, TaskStatus.RUNNING, "正在分析代码质量和架构..."
        )
        
        # 步骤3: 安全性扫描 (55%)
        await asyncio.sleep(1.0)
        await progress_service.update_progress(
            task_id, 55, TaskStatus.RUNNING, "正在进行安全性扫描..."
        )
        
        # 步骤4: 性能评估 (75%)
        await asyncio.sleep(1.1)
        await progress_service.update_progress(
            task_id, 75, TaskStatus.RUNNING, "正在评估性能指标..."
        )
        
        # 步骤5: 生成AI建议 (95%)
        await asyncio.sleep(0.7)
        await progress_service.update_progress(
            task_id, 95, TaskStatus.RUNNING, "正在生成AI分析建议..."
        )
        
        # 完成
        await asyncio.sleep(0.3)
        
        analysis_result = {
            "analysis_id": task_id,
            "repo_name": repo_name,
            "analysis_type": analysis_type,
            "completed_at": datetime.now().isoformat(),
            "score": {
                "code_quality": 85,
                "security": 92,
                "performance": 78,
                "maintainability": 88
            },
            "recommendations": [
                "建议优化数据库查询性能",
                "增加单元测试覆盖率",
                "更新依赖包到最新安全版本"
            ],
            "detailed_report_url": f"/analysis/{task_id}/detail"
        }
        
        await progress_service.complete_task(task_id, {"analysis": analysis_result})
        
        logger.info(f"AI分析完成: {task_id}")
        return analysis_result
        
    except Exception as e:
        await progress_service.fail_task(task_id, str(e))
        logger.error(f"AI分析失败: {task_id} - {e}")
        raise 