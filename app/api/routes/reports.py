"""
报告相关的API路由
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from app.services.report_service import ReportService
from app.schemas.report_schemas import (
    ReportCreate, ReportUpdate, ReportResponse, 
    ReportListResponse, ReportTemplateResponse
)
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=ReportListResponse)
async def get_reports(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="限制返回的记录数"),
    report_type: Optional[str] = Query(None, description="报告类型"),
    status: Optional[str] = Query(None, description="报告状态")
):
    """获取报告列表"""
    try:
        logger.info(f"📊 获取报告列表 - skip: {skip}, limit: {limit}")
        
        reports = await ReportService.get_all_reports(
            skip=skip, limit=limit, report_type=report_type, status=status
        )
        total = await ReportService.get_report_count(report_type=report_type, status=status)
        
        logger.info(f"✅ 获取到 {len(reports)} 个报告，总数: {total}")
        
        return ReportListResponse(
            reports=reports,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"💥 获取报告列表失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取报告列表失败: {str(e)}")


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: int):
    """根据ID获取报告"""
    try:
        logger.info(f"📄 获取报告详情 - ID: {report_id}")
        
        report = await ReportService.get_report(report_id)
        if not report:
            logger.warning(f"❌ 报告不存在 - ID: {report_id}")
            raise HTTPException(status_code=404, detail="报告不存在")
        
        logger.info(f"✅ 报告获取成功 - {report.title}")
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 获取报告失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取报告失败: {str(e)}")


@router.post("/", response_model=ReportResponse)
async def create_report(report_data: ReportCreate, background_tasks: BackgroundTasks):
    """创建新报告"""
    from datetime import datetime, timedelta
    try:
        logger.info(f"📝 开始创建报告: {report_data.title}")
        
        # 设置报告时间范围（默认为过去一天）
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=1)
        
        report = await ReportService.create_report(
            user_id=1,  # 临时使用固定用户ID，后续需要从认证中获取
            title=report_data.title,
            report_type=report_data.report_type,
            period_start=period_start,
            period_end=period_end,
            subscriptions_included=[report_data.subscription_id]
        )
        
        # 后台任务：生成报告内容
        background_tasks.add_task(generate_report_content, report.id)
        
        logger.info(f"✅ 报告创建成功: {report.title} (ID: {report.id})")
        return report
    except Exception as e:
        logger.error(f"💥 创建报告失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建报告失败: {str(e)}")


class GenerateReportRequest(BaseModel):
    subscription_id: int
    report_type: str = "daily"

@router.post("/generate")
async def generate_report(
    request: GenerateReportRequest,
    background_tasks: BackgroundTasks
):
    """手动生成报告"""
    from datetime import datetime, timedelta
    try:
        logger.info(f"🔄 手动生成报告 - 订阅ID: {request.subscription_id}, 类型: {request.report_type}")
        
        # 设置报告时间范围
        period_end = datetime.utcnow()
        if request.report_type == "daily":
            period_start = period_end - timedelta(days=1)
        elif request.report_type == "weekly":
            period_start = period_end - timedelta(weeks=1)
        else:
            period_start = period_end - timedelta(days=1)
        
        # 创建报告记录
        report = await ReportService.create_report(
            user_id=1,  # 临时使用固定用户ID
            title=f"{request.report_type.title()} Report",
            report_type=request.report_type,
            period_start=period_start,
            period_end=period_end,
            subscriptions_included=[request.subscription_id]
        )
        
        # 后台任务：生成报告内容
        background_tasks.add_task(generate_report_content, report.id)
        
        logger.info(f"✅ 报告生成任务已启动: {report.id}")
        return {
            "message": "报告生成已开始",
            "report_id": report.id,
            "status": "generating"
        }
    except Exception as e:
        logger.error(f"💥 生成报告失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成报告失败: {str(e)}")


@router.get("/templates/", response_model=List[ReportTemplateResponse])
async def get_report_templates():
    """获取报告模板列表"""
    try:
        logger.info("📋 获取报告模板列表")
        
        templates = await ReportService.get_report_templates()
        
        logger.info(f"✅ 获取到 {len(templates)} 个报告模板")
        return templates
    except Exception as e:
        logger.error(f"💥 获取报告模板失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取报告模板失败: {str(e)}")


@router.get("/stats/summary")
async def get_report_stats():
    """获取报告统计信息"""
    try:
        logger.info("📊 开始获取报告统计信息")
        
        total_reports = await ReportService.get_report_count()
        completed_reports = await ReportService.get_report_count(status="completed")
        generating_reports = await ReportService.get_report_count(status="generating")
        failed_reports = await ReportService.get_report_count(status="failed")
        
        stats = {
            "total_reports": total_reports,
            "completed_reports": completed_reports,
            "generating_reports": generating_reports,
            "failed_reports": failed_reports
        }
        
        logger.info(f"✅ 报告统计获取成功: {stats}")
        return stats
    except Exception as e:
        logger.error(f"💥 获取报告统计失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取报告统计失败: {str(e)}")


async def generate_report_content(report_id: int):
    """后台任务：生成报告内容"""
    try:
        logger.info(f"🔄 开始生成报告内容 - ID: {report_id}")
        
        # 更新状态为生成中
        await ReportService.update_report(report_id, status="generating")
        
        # 获取报告信息
        report = await ReportService.get_report(report_id)
        if not report:
            logger.error(f"❌ 报告不存在 - ID: {report_id}")
            return
        
        # 生成简单的报告内容（临时实现）
        content = f"""
# {report.title}

**报告类型**: {report.report_type}
**生成时间**: {report.created_at}
**时间范围**: {report.period_start} 到 {report.period_end}

## 概要
这是一个自动生成的GitHub仓库活动报告。

## 统计信息
- 总仓库数: 1
- 总活动数: 0
- 提交数: 0
- 问题数: 0
- 拉取请求数: 0
- 发布数: 0

*注意: 这是一个示例报告，实际数据收集功能正在开发中。*
        """
        
        # 更新报告内容和状态
        await ReportService.update_report(
            report_id=report_id,
            content=content,
            status="completed"
        )
        
        logger.info(f"✅ 报告内容生成完成 - ID: {report_id}")
        
    except Exception as e:
        logger.error(f"💥 生成报告内容失败 - ID: {report_id}, 错误: {str(e)}", exc_info=True)
        # 更新状态为失败
        try:
            await ReportService.update_report(report_id, status="failed")
        except:
            pass 