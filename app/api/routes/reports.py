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
from app.collectors.github_collector import GitHubCollector
from app.services.subscription_service import SubscriptionService
from app.utils.timezone_utils import beijing_now, format_beijing_time
import json
from datetime import datetime
from fastapi.responses import Response
import re

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
        period_end = datetime.now()
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
    format: str = "html"  # 添加格式选择，默认 html

@router.post("/generate")
async def generate_report(
    request: GenerateReportRequest,
    background_tasks: BackgroundTasks
):
    """手动生成报告"""
    from datetime import datetime, timedelta
    from app.utils.timezone_utils import beijing_now
    from app.services.subscription_service import SubscriptionService
    
    try:
        logger.info(f"🔄 手动生成报告 - 订阅ID: {request.subscription_id}, 类型: {request.report_type}")
        
        # 获取订阅信息
        subscription = await SubscriptionService.get_subscription(request.subscription_id)
        if not subscription:
            logger.error(f"❌ 订阅不存在 - ID: {request.subscription_id}")
            raise HTTPException(status_code=404, detail="订阅不存在")
        
        # 设置报告时间范围（使用北京时间）
        beijing_end = beijing_now()
        if request.report_type == "daily":
            beijing_start = beijing_end - timedelta(days=1)
        elif request.report_type == "weekly":
            beijing_start = beijing_end - timedelta(weeks=1)
        else:
            beijing_start = beijing_end - timedelta(days=1)
        
        # 直接使用北京时间存储到数据库
        period_start = beijing_start
        period_end = beijing_end
        
        # 创建报告记录
        report = await ReportService.create_report(
            user_id=subscription.user_id,  # 使用订阅的用户ID
            title=f"{subscription.repository} {request.report_type.title()} Report",
            description=f"Generated {request.report_type} report for {subscription.repository}",
            repository=subscription.repository,  # 添加repository字段
            report_type=request.report_type,
            format=request.format,
            period_start=period_start,
            period_end=period_end,
            subscriptions_included=[subscription.id]
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


@router.get("/{report_id}/download")
async def download_report(report_id: int):
    """下载报告"""
    from fastapi.responses import Response
    try:
        logger.info(f"📥 开始下载报告 - ID: {report_id}")
        
        # 获取报告
        report = await ReportService.get_report(report_id)
        if not report:
            logger.warning(f"❌ 报告不存在 - ID: {report_id}")
            raise HTTPException(status_code=404, detail="报告不存在")
        
        if not report.content:
            logger.warning(f"❌ 报告内容为空 - ID: {report_id}")
            raise HTTPException(status_code=400, detail="报告内容为空")
        
        # 生成带时间戳的文件名
        current_time = beijing_now()
        timestamp = current_time.strftime("%Y.%m.%d_%H.%M.%S")
        
        # 确定文件名和内容类型
        if report.format.lower() in ["markdown", "md"]:
            filename = f"{report.title}_{timestamp}.md"
            content_type = "text/markdown"
        else:
            filename = f"{report.title}_{timestamp}.html"
            content_type = "text/html"
        
        # 清理文件名中的特殊字符
        filename = re.sub(r'[^\w\s.-]', '', filename).strip()
        filename = re.sub(r'[-\s]+', '-', filename)
        
        logger.info(f"✅ 报告下载准备完成 - 文件名: {filename}")
        
        return Response(
            content=report.content,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": content_type
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 下载报告失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"下载报告失败: {str(e)}")


@router.delete("/{report_id}")
async def delete_report(report_id: int):
    """删除报告"""
    try:
        logger.info(f"🗑️ 开始删除报告 - ID: {report_id}")
        
        # 检查报告是否存在
        report = await ReportService.get_report(report_id)
        if not report:
            logger.warning(f"❌ 报告不存在 - ID: {report_id}")
            raise HTTPException(status_code=404, detail="报告不存在")
        
        # 删除报告
        success = await ReportService.delete_report(report_id)
        if not success:
            logger.error(f"💥 删除报告失败 - ID: {report_id}")
            raise HTTPException(status_code=500, detail="删除报告失败")
        
        logger.info(f"✅ 报告删除成功 - ID: {report_id}")
        return {"message": "报告删除成功", "report_id": report_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 删除报告失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"删除报告失败: {str(e)}")


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(report_id: int, report_data: ReportUpdate):
    """更新报告"""
    try:
        logger.info(f"📝 开始更新报告 - ID: {report_id}")
        
        updated_report = await ReportService.update_report(
            report_id=report_id,
            title=report_data.title,
            description=report_data.description,
            status=report_data.status
        )
        
        if not updated_report:
            logger.warning(f"❌ 报告不存在 - ID: {report_id}")
            raise HTTPException(status_code=404, detail="报告不存在")
        
        logger.info(f"✅ 报告更新成功: {updated_report.title}")
        return updated_report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 更新报告失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"更新报告失败: {str(e)}")


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
        
        # 获取订阅信息
        subscriptions_included = json.loads(report.subscriptions_included or "[]")
        if not subscriptions_included:
            logger.error(f"❌ 报告没有关联的订阅 - ID: {report_id}")
            await ReportService.update_report(report_id, status="failed", error_message="没有关联的订阅")
            return
        
        subscription_id = subscriptions_included[0]
        subscription = await SubscriptionService.get_subscription(subscription_id)
        if not subscription:
            logger.error(f"❌ 订阅不存在 - ID: {subscription_id}")
            await ReportService.update_report(report_id, status="failed", error_message="订阅不存在")
            return
        
        # 解析仓库信息
        repo_parts = subscription.repository.split('/')
        if len(repo_parts) != 2:
            logger.error(f"❌ 仓库格式错误: {subscription.repository}")
            await ReportService.update_report(report_id, status="failed", error_message="仓库格式错误")
            return
        
        owner, repo = repo_parts
        logger.info(f"📊 开始收集仓库数据: {owner}/{repo}")
        
        # 初始化GitHub收集器
        github_collector = GitHubCollector()
        
        # 收集仓库数据
        try:
            repo_data = await github_collector.collect_repository_data(owner, repo)
            logger.info(f"✅ 仓库数据收集完成: {repo_data['summary']}")
        except Exception as e:
            logger.error(f"💥 收集仓库数据失败: {e}")
            await ReportService.update_report(
                report_id, 
                status="failed", 
                error_message=f"收集仓库数据失败: {str(e)}"
            )
            return
        
        # 使用 AI 服务生成智能总结
        ai_summary = ""
        ai_analysis = ""
        try:
            from app.services.ai_service import AIService
            ai_service = AIService()
            
            # 准备 AI 分析的数据
            analysis_data = {
                "repository": repo_data['repository'],
                "commits": repo_data['commits'][:20],  # 最近20个提交
                "issues": repo_data['issues'][:10],    # 最近10个issues
                "pull_requests": repo_data['pull_requests'][:10],  # 最近10个PR
                "releases": repo_data['releases'][:5],  # 最近5个发布
                "period": {
                    "start": report.period_start.isoformat(),
                    "end": report.period_end.isoformat(),
                    "type": report.report_type
                }
            }
            logger.info(f"AI总结发送参数：{analysis_data}")
            # 生成 AI 总结
            ai_summary = await ai_service.generate_repository_summary(analysis_data)
            logger.info(f"✅ AI 总结生成完成")
            
            # 生成 AI 分析
            ai_analysis = await ai_service.analyze_repository_trends(analysis_data)
            logger.info(f"✅ AI 趋势分析完成")
            
        except Exception as e:
            logger.warning(f"⚠️ AI 服务调用失败，将使用默认总结: {e}")
            ai_summary = f"本报告涵盖了 {subscription.repository} 仓库在指定时间段内的活动情况。"
            ai_analysis = "AI 分析服务暂时不可用，请稍后重试。"
        
        # 生成报告内容
        current_time = beijing_now()
        
        # 根据格式生成不同的内容
        if report.format.lower() == "markdown" or report.format.lower() == "md":
            report_content = generate_markdown_report(
                report, subscription, repo_data, ai_summary, ai_analysis, current_time
            )
        else:
            report_content = generate_html_report(
                report, subscription, repo_data, ai_summary, ai_analysis, current_time
            )
        
        # 更新报告统计信息
        await ReportService.update_report_statistics(
            report_id,
            total_repositories=1,
            total_activities=len(repo_data['commits']) + len(repo_data['issues']) + len(repo_data['pull_requests']),
            total_commits=len(repo_data['commits']),
            total_issues=len(repo_data['issues']),
            total_pull_requests=len(repo_data['pull_requests']),
            total_releases=len(repo_data['releases'])
        )

        # 更新报告内容和状态
        await ReportService.update_report(
            report_id,
            status="completed",
            content=report_content,
            summary=ai_summary,
            ai_analysis=ai_analysis
        )

        logger.info(f"✅ 报告生成完成 - ID: {report_id}")
        
        # 发送邮件通知
        try:
            await send_report_notification(report_id, subscription, report)
        except Exception as e:
            logger.error(f"📧 发送邮件通知失败 - 报告ID: {report_id}, 错误: {e}", exc_info=True)
            # 邮件发送失败不影响报告生成状态

    except Exception as e:
        logger.error(f"💥 生成报告内容失败 - ID: {report_id}, 错误: {e}", exc_info=True)
        await ReportService.update_report(
            report_id,
            status="failed",
            error_message=str(e)
        )


def generate_html_report(report, subscription, repo_data, ai_summary, ai_analysis, current_time):
    """生成 HTML 格式的报告"""
    report_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{report.title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f8f9fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .section {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #007bff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .ai-section {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e9ecef;
            transition: transform 0.2s;
        }}
        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 28px;
            font-weight: bold;
            color: #007bff;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 14px;
            color: #666;
            font-weight: 500;
        }}
        .activity-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 10px;
            border-left: 3px solid #28a745;
            transition: background 0.2s;
        }}
        .activity-item:hover {{
            background: #e9ecef;
        }}
        .activity-title {{
            font-weight: 600;
            margin-bottom: 5px;
            color: #495057;
        }}
        .activity-meta {{
            font-size: 14px;
            color: #6c757d;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
        }}
        .ai-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 8px;
        }}
        h2 {{
            color: #495057;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 {report.title}</h1>
        <p>🏠 仓库: {subscription.repository}</p>
        <p>📅 报告时间: {format_beijing_time(current_time, '%Y年%m月%d日 %H:%M')}</p>
        <p>📊 数据范围: {format_beijing_time(report.period_start, '%Y-%m-%d')} 至 {format_beijing_time(report.period_end, '%Y-%m-%d')}</p>
    </div>
    
    <div class="ai-section">
        <h2>🤖 AI 智能总结 <span class="ai-badge">AI Generated</span></h2>
        <p>{ai_summary}</p>
    </div>
    
    <div class="section">
        <h2>📋 仓库概览</h2>
        <p><strong>仓库名称:</strong> {repo_data['repository']['name']}</p>
        <p><strong>描述:</strong> {repo_data['repository']['description'] or '无描述'}</p>
        <p><strong>主要语言:</strong> {repo_data['repository']['language'] or '未知'}</p>
        <p><strong>许可证:</strong> {repo_data['repository']['license'] or '无'}</p>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{repo_data['repository']['stargazers_count']}</div>
                <div class="stat-label">⭐ Stars</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{repo_data['repository']['forks_count']}</div>
                <div class="stat-label">🍴 Forks</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{repo_data['repository']['watchers_count']}</div>
                <div class="stat-label">👀 Watchers</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{repo_data['repository']['open_issues_count']}</div>
                <div class="stat-label">🐛 Open Issues</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>📊 活动统计</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(repo_data['commits'])}</div>
                <div class="stat-label">💻 最近提交</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(repo_data['issues'])}</div>
                <div class="stat-label">🐛 最近Issues</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(repo_data['pull_requests'])}</div>
                <div class="stat-label">🔀 最近PR</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(repo_data['releases'])}</div>
                <div class="stat-label">🚀 最近发布</div>
            </div>
        </div>
    </div>
    
    <div class="ai-section">
        <h2>📈 AI 趋势分析 <span class="ai-badge">AI Generated</span></h2>
        <p>{ai_analysis}</p>
    </div>
"""

    # 添加最近提交
    if repo_data['commits']:
        report_content += """
    <div class="section">
        <h2>💻 最近提交</h2>
"""
        for commit in repo_data['commits'][:10]:  # 只显示前10个
            commit_date = datetime.fromisoformat(commit['date'].replace('Z', '+00:00'))
            report_content += f"""
        <div class="activity-item">
            <div class="activity-title">{commit['message'][:100]}{'...' if len(commit['message']) > 100 else ''}</div>
            <div class="activity-meta">
                👤 {commit['author']['name'] if isinstance(commit['author'], dict) else commit['author']} • 📅 {format_beijing_time(commit_date, '%Y-%m-%d %H:%M')} • 🔗 <a href="{commit.get('html_url', '#')}" target="_blank">{commit['sha'][:8]}</a>
            </div>
        </div>
"""
        report_content += "    </div>\n"

    # 添加最近Issues
    if repo_data['issues']:
        report_content += """
    <div class="section">
        <h2>🐛 最近Issues</h2>
"""
        for issue in repo_data['issues'][:10]:
            issue_date = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
            state_emoji = "🟢" if issue['state'] == 'open' else "🔴"
            report_content += f"""
        <div class="activity-item">
            <div class="activity-title">{state_emoji} #{issue['number']}: {issue['title']}</div>
            <div class="activity-meta">
                👤 {issue['user']} • 📅 {format_beijing_time(issue_date, '%Y-%m-%d %H:%M')} • 🔗 <a href="{issue['html_url']}" target="_blank">查看详情</a>
            </div>
        </div>
"""
        report_content += "    </div>\n"

    # 添加最近PR
    if repo_data['pull_requests']:
        report_content += """
    <div class="section">
        <h2>🔀 最近Pull Requests</h2>
"""
        for pr in repo_data['pull_requests'][:10]:
            pr_date = datetime.fromisoformat(pr['created_at'].replace('Z', '+00:00'))
            state_emoji = "🟢" if pr['state'] == 'open' else "🟣" if pr['merged'] else "🔴"
            report_content += f"""
        <div class="activity-item">
            <div class="activity-title">{state_emoji} #{pr['number']}: {pr['title']}</div>
            <div class="activity-meta">
                👤 {pr['user']} • 📅 {format_beijing_time(pr_date, '%Y-%m-%d %H:%M')} • 🔗 <a href="{pr['html_url']}" target="_blank">查看详情</a>
            </div>
        </div>
"""
        report_content += "    </div>\n"

    # 添加最近发布
    if repo_data['releases']:
        report_content += """
    <div class="section">
        <h2>🚀 最近发布</h2>
"""
        for release in repo_data['releases'][:5]:
            release_date = datetime.fromisoformat(release['published_at'].replace('Z', '+00:00'))
            report_content += f"""
        <div class="activity-item">
            <div class="activity-title">🏷️ {release['tag_name']}: {release['name'] or release['tag_name']}</div>
            <div class="activity-meta">
                📅 {format_beijing_time(release_date, '%Y-%m-%d %H:%M')} • 🔗 <a href="{release['html_url']}" target="_blank">查看发布</a>
            </div>
        </div>
"""
        report_content += "    </div>\n"

    # 添加页脚
    report_content += f"""
    <div class="footer">
        <p>📊 本报告由 GitHub Sentinel 自动生成</p>
        <p>🤖 包含 AI 智能分析和总结</p>
        <p>⏰ 生成时间: {format_beijing_time(current_time, '%Y年%m月%d日 %H:%M:%S')} (北京时间)</p>
    </div>
</body>
</html>
"""
    return report_content


def generate_markdown_report(report, subscription, repo_data, ai_summary, ai_analysis, current_time):
    """生成 Markdown 格式的报告"""
    report_content = f"""# 📊 {report.title}

**🏠 仓库:** {subscription.repository}  
**📅 报告时间:** {format_beijing_time(current_time, '%Y年%m月%d日 %H:%M')}  
**📊 数据范围:** {format_beijing_time(report.period_start, '%Y-%m-%d')} 至 {format_beijing_time(report.period_end, '%Y-%m-%d')}

---

## 🤖 AI 智能总结 *(AI Generated)*

{ai_summary}

---

## 📋 仓库概览

- **仓库名称:** {repo_data['repository']['name']}
- **描述:** {repo_data['repository']['description'] or '无描述'}
- **主要语言:** {repo_data['repository']['language'] or '未知'}
- **许可证:** {repo_data['repository']['license'] or '无'}

### 📊 仓库统计

| 指标 | 数量 |
|------|------|
| ⭐ Stars | {repo_data['repository']['stargazers_count']} |
| 🍴 Forks | {repo_data['repository']['forks_count']} |
| 👀 Watchers | {repo_data['repository']['watchers_count']} |
| 🐛 Open Issues | {repo_data['repository']['open_issues_count']} |

---

## 📊 活动统计

| 活动类型 | 数量 |
|----------|------|
| 💻 最近提交 | {len(repo_data['commits'])} |
| 🐛 最近Issues | {len(repo_data['issues'])} |
| 🔀 最近PR | {len(repo_data['pull_requests'])} |
| 🚀 最近发布 | {len(repo_data['releases'])} |

---

## 📈 AI 趋势分析 *(AI Generated)*

{ai_analysis}

---
"""

    # 添加最近提交
    if repo_data['commits']:
        report_content += "\n## 💻 最近提交\n\n"
        for commit in repo_data['commits'][:10]:  # 只显示前10个
            commit_date = datetime.fromisoformat(commit['date'].replace('Z', '+00:00'))
            commit_message = commit['message'][:100] + ('...' if len(commit['message']) > 100 else '')
            report_content += f"### {commit_message}\n"
            report_content += f"👤 **作者:** {commit['author']['name'] if isinstance(commit['author'], dict) else commit['author']}  \n"
            report_content += f"📅 **时间:** {format_beijing_time(commit_date, '%Y-%m-%d %H:%M')}  \n"
            report_content += f"🔗 **链接:** [{commit['sha'][:8]}]({commit.get('html_url', '#')})\n\n"

    # 添加最近Issues
    if repo_data['issues']:
        report_content += "\n## 🐛 最近Issues\n\n"
        for issue in repo_data['issues'][:10]:
            issue_date = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
            state_emoji = "🟢" if issue['state'] == 'open' else "🔴"
            report_content += f"### {state_emoji} #{issue['number']}: {issue['title']}\n"
            report_content += f"👤 **创建者:** {issue['user']}  \n"
            report_content += f"📅 **时间:** {format_beijing_time(issue_date, '%Y-%m-%d %H:%M')}  \n"
            report_content += f"🔗 **链接:** [查看详情]({issue['html_url']})\n\n"

    # 添加最近PR
    if repo_data['pull_requests']:
        report_content += "\n## 🔀 最近Pull Requests\n\n"
        for pr in repo_data['pull_requests'][:10]:
            pr_date = datetime.fromisoformat(pr['created_at'].replace('Z', '+00:00'))
            state_emoji = "🟢" if pr['state'] == 'open' else "🟣" if pr['merged'] else "🔴"
            report_content += f"### {state_emoji} #{pr['number']}: {pr['title']}\n"
            report_content += f"👤 **创建者:** {pr['user']}  \n"
            report_content += f"📅 **时间:** {format_beijing_time(pr_date, '%Y-%m-%d %H:%M')}  \n"
            report_content += f"🔗 **链接:** [查看详情]({pr['html_url']})\n\n"

    # 添加最近发布
    if repo_data['releases']:
        report_content += "\n## 🚀 最近发布\n\n"
        for release in repo_data['releases'][:5]:
            release_date = datetime.fromisoformat(release['published_at'].replace('Z', '+00:00'))
            report_content += f"### 🏷️ {release['tag_name']}: {release['name'] or release['tag_name']}\n"
            report_content += f"📅 **发布时间:** {format_beijing_time(release_date, '%Y-%m-%d %H:%M')}  \n"
            report_content += f"🔗 **链接:** [查看发布]({release['html_url']})\n\n"

    # 添加页脚
    report_content += f"""
---

## 📄 报告信息

📊 **生成工具:** GitHub Sentinel  
🤖 **AI 支持:** 包含智能分析和总结  
⏰ **生成时间:** {format_beijing_time(current_time, '%Y年%m月%d日 %H:%M:%S')} (北京时间)
"""
    
    return report_content 

async def send_report_notification(report_id: int, subscription, report):
    """发送报告生成完成的邮件通知"""
    logger.info(f"📧 开始发送报告邮件通知 - 报告ID: {report_id}")
    
    try:
        # 获取邮件配置
        from app.core.config import get_settings
        settings = get_settings()
        
        if not settings.notification.email_enabled:
            logger.info(f"📧 邮件服务未启用，跳过通知发送")
            return
        
        # 获取收件人邮箱列表
        notification_emails = []
        
        # 从订阅配置中获取邮箱
        if subscription.notification_emails:
            import json
            try:
                emails = json.loads(subscription.notification_emails)
                if isinstance(emails, list):
                    notification_emails.extend(emails)
                logger.info(f"📧 从订阅配置获取邮箱: {emails}")
            except json.JSONDecodeError:
                logger.warning(f"📧 订阅邮箱配置格式错误: {subscription.notification_emails}")
        
        # 如果没有配置邮箱，使用默认邮箱
        if not notification_emails:
            if settings.notification.email_to:
                notification_emails.extend(settings.notification.email_to)
                logger.info(f"📧 使用默认邮箱: {settings.notification.email_to}")
            else:
                logger.warning(f"📧 没有配置收件人邮箱，跳过邮件发送")
                return
        
        # 准备邮件内容
        subject = f"📊 GitHub Sentinel 报告生成完成 - {subscription.repository}"
        
        # 生成邮件正文
        from app.utils.timezone_utils import beijing_now, format_beijing_time
        current_time = beijing_now()
        
        # 获取完整的报告内容
        report_content = report.content or "报告内容生成中..."
        
        # 如果是HTML格式，直接使用；如果是Markdown，转换为HTML
        if report.format.lower() in ['markdown', 'md']:
            # 简单的Markdown到HTML转换
            html_content = report_content.replace('\n', '<br>')
            html_content = html_content.replace('# ', '<h1>').replace('\n', '</h1>\n')
            html_content = html_content.replace('## ', '<h2>').replace('\n', '</h2>\n')
            html_content = html_content.replace('### ', '<h3>').replace('\n', '</h3>\n')
            html_content = html_content.replace('**', '<strong>').replace('**', '</strong>')
            html_content = html_content.replace('*', '<em>').replace('*', '</em>')
        else:
            # 如果是HTML格式，提取body内容
            if '<body>' in report_content and '</body>' in report_content:
                start = report_content.find('<body>') + 6
                end = report_content.find('</body>')
                html_content = report_content[start:end]
            else:
                html_content = report_content
        
        email_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #4285f4; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; }}
        .report-content {{ background: white; padding: 20px; margin: 20px 0; border-radius: 5px; border: 1px solid #ddd; }}
        .info-box {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #4285f4; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; border-radius: 0 0 8px 8px; background: #f9f9f9; padding: 15px; }}
        .button {{ display: inline-block; background: #4285f4; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
        h1, h2, h3 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 GitHub Sentinel</h1>
            <p>仓库监控报告</p>
        </div>
        <div class="content">
            <div class="info-box">
                <h3>📋 报告信息</h3>
                <p><strong>仓库:</strong> {subscription.repository}</p>
                <p><strong>报告类型:</strong> {report.report_type}</p>
                <p><strong>报告格式:</strong> {report.format.upper()}</p>
                <p><strong>生成时间:</strong> {format_beijing_time(current_time, '%Y年%m月%d日 %H:%M:%S')} (北京时间)</p>
                <p><strong>报告状态:</strong> ✅ 生成完成</p>
            </div>
            
            <div class="report-content">
                <h2>📊 完整报告内容</h2>
                {html_content}
            </div>
            
            <div class="info-box">
                <h3>🔗 在线查看</h3>
                <p>您也可以登录 GitHub Sentinel 系统在线查看报告：</p>
                <a href="http://localhost:4000/reports" class="button">在线查看</a>
            </div>
        </div>
        <div class="footer">
            <p>此邮件由 GitHub Sentinel 自动发送，包含完整的报告内容。</p>
            <p>如需取消订阅，请登录系统进行设置。</p>
        </div>
    </div>
</body>
</html>
"""
        
        # 发送邮件
        from app.services.notification_service import NotificationService
        notification_service = NotificationService()
        
        logger.info(f"📧 准备发送邮件到: {notification_emails}")
        logger.info(f"📧 邮件主题: {subject}")
        logger.info(f"📧 邮件内容长度: {len(email_body)} 字符")
        
        for email in notification_emails:
            try:
                logger.info(f"📧 开始发送邮件到: {email}")
                
                success = await notification_service.send_email(
                    to_email=email,
                    subject=subject,
                    body=email_body,
                    is_html=True
                )
                
                if success:
                    logger.info(f"✅ 邮件发送成功: {email}")
                else:
                    logger.error(f"❌ 邮件发送失败: {email}")
                    
            except Exception as e:
                logger.error(f"💥 发送邮件到 {email} 时出错: {e}", exc_info=True)
        
        logger.info(f"📧 报告邮件通知发送完成 - 报告ID: {report_id}")
        
    except Exception as e:
        logger.error(f"💥 发送报告邮件通知失败: {e}")
        raise 