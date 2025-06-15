"""
仪表板相关的API路由
提供统计数据和图表数据
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, and_, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db_session
from app.models.subscription import User, Subscription, RepositoryActivity
from app.models.report import Report
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats():
    """获取仪表板统计数据"""
    try:
        logger.info("📊 开始获取仪表板统计数据")
        
        async with get_db_session() as session:
            # 用户统计
            total_users = await session.scalar(
                func.count(User.id)
            )
            active_users = await session.scalar(
                func.count(User.id).filter(User.is_active == True)
            )
            
            # 订阅统计
            total_subscriptions = await session.scalar(
                func.count(Subscription.id)
            )
            active_subscriptions = await session.scalar(
                func.count(Subscription.id).filter(Subscription.status == 'active')
            )
            paused_subscriptions = await session.scalar(
                func.count(Subscription.id).filter(Subscription.status == 'paused')
            )
            
            # 报告统计
            total_reports = await session.scalar(
                func.count(Report.id)
            )
            completed_reports = await session.scalar(
                func.count(Report.id).filter(Report.status == 'completed')
            )
            
            # 今日活动统计
            today = datetime.now().date()
            today_activities = await session.scalar(
                func.count(RepositoryActivity.id).filter(
                    func.date(RepositoryActivity.created_at) == today
                )
            )
            
            # 本周活动统计
            week_start = datetime.now() - timedelta(days=7)
            week_activities = await session.scalar(
                func.count(RepositoryActivity.id).filter(
                    RepositoryActivity.created_at >= week_start
                )
            )
            
            stats = {
                "users": {
                    "total": total_users or 0,
                    "active": active_users or 0
                },
                "subscriptions": {
                    "total": total_subscriptions or 0,
                    "active": active_subscriptions or 0,
                    "paused": paused_subscriptions or 0
                },
                "reports": {
                    "total": total_reports or 0,
                    "completed": completed_reports or 0
                },
                "activities": {
                    "today": today_activities or 0,
                    "this_week": week_activities or 0
                }
            }
            
            logger.info(f"✅ 仪表板统计数据获取成功: {stats}")
            return stats
            
    except Exception as e:
        logger.error(f"❌ 获取仪表板统计数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@router.get("/activity-chart")
async def get_activity_chart_data(days: int = Query(7, ge=1, le=30, description="天数")):
    """获取活动图表数据"""
    try:
        logger.info(f"📈 开始获取 {days} 天的活动图表数据")
        
        async with get_db_session() as session:
            # 计算日期范围
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days-1)
            
            # 生成日期列表
            date_list = []
            current_date = start_date
            while current_date <= end_date:
                date_list.append(current_date)
                current_date += timedelta(days=1)
            
            # 查询每日活动数据
            activity_data = {}
            for date in date_list:
                # 查询当日各类型活动数量
                commits = await session.scalar(
                    func.count(RepositoryActivity.id).filter(
                        and_(
                            func.date(RepositoryActivity.created_at) == date,
                            RepositoryActivity.activity_type == 'commit'
                        )
                    )
                ) or 0
                
                issues = await session.scalar(
                    func.count(RepositoryActivity.id).filter(
                        and_(
                            func.date(RepositoryActivity.created_at) == date,
                            RepositoryActivity.activity_type == 'issue'
                        )
                    )
                ) or 0
                
                pull_requests = await session.scalar(
                    func.count(RepositoryActivity.id).filter(
                        and_(
                            func.date(RepositoryActivity.created_at) == date,
                            RepositoryActivity.activity_type == 'pull_request'
                        )
                    )
                ) or 0
                
                releases = await session.scalar(
                    func.count(RepositoryActivity.id).filter(
                        and_(
                            func.date(RepositoryActivity.created_at) == date,
                            RepositoryActivity.activity_type == 'release'
                        )
                    )
                ) or 0
                
                activity_data[date.strftime('%Y-%m-%d')] = {
                    'commits': commits,
                    'issues': issues,
                    'pull_requests': pull_requests,
                    'releases': releases
                }
            
            # 格式化为前端需要的格式
            chart_data = {
                'dates': [date.strftime('%m-%d') for date in date_list],
                'commits': [activity_data[date.strftime('%Y-%m-%d')]['commits'] for date in date_list],
                'issues': [activity_data[date.strftime('%Y-%m-%d')]['issues'] for date in date_list],
                'pull_requests': [activity_data[date.strftime('%Y-%m-%d')]['pull_requests'] for date in date_list],
                'releases': [activity_data[date.strftime('%Y-%m-%d')]['releases'] for date in date_list]
            }
            
            logger.info(f"✅ 活动图表数据获取成功，共 {len(date_list)} 天数据")
            return chart_data
            
    except Exception as e:
        logger.error(f"❌ 获取活动图表数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取图表数据失败: {str(e)}")


@router.get("/repository-stats")
async def get_repository_stats():
    """获取仓库统计数据"""
    try:
        logger.info("📊 开始获取仓库统计数据")
        
        async with get_db_session() as session:
            # 获取最活跃的仓库
            from sqlalchemy import select
            
            # 查询每个仓库的活动数量
            repo_activity_query = select(
                Subscription.repository,
                func.count(RepositoryActivity.id).label('activity_count')
            ).select_from(
                Subscription
            ).outerjoin(
                RepositoryActivity, 
                Subscription.repository == RepositoryActivity.repository_full_name
            ).group_by(
                Subscription.repository
            ).order_by(
                desc('activity_count')
            ).limit(10)
            
            result = await session.execute(repo_activity_query)
            top_repositories = []
            
            for row in result:
                repo_name = row.repository
                activity_count = row.activity_count or 0
                
                # 获取订阅状态
                subscription = await session.scalar(
                    select(Subscription).filter(Subscription.repository == repo_name)
                )
                
                top_repositories.append({
                    'name': repo_name,
                    'activity_count': activity_count,
                    'status': subscription.status if subscription else 'unknown',
                    'frequency': subscription.frequency if subscription else 'unknown'
                })
            
            # 获取活动类型分布
            activity_types = {}
            for activity_type in ['commit', 'issue', 'pull_request', 'release', 'discussion']:
                count = await session.scalar(
                    func.count(RepositoryActivity.id).filter(
                        RepositoryActivity.activity_type == activity_type
                    )
                ) or 0
                activity_types[activity_type] = count
            
            stats = {
                'top_repositories': top_repositories,
                'activity_types': activity_types
            }
            
            logger.info(f"✅ 仓库统计数据获取成功")
            return stats
            
    except Exception as e:
        logger.error(f"❌ 获取仓库统计数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取仓库统计失败: {str(e)}")


@router.get("/recent-activities")
async def get_recent_activities(limit: int = Query(10, ge=1, le=50, description="限制数量")):
    """获取最近活动"""
    try:
        logger.info(f"📋 开始获取最近 {limit} 条活动")
        
        async with get_db_session() as session:
            from sqlalchemy import select
            
            # 查询最近的活动
            query = select(RepositoryActivity).order_by(
                desc(RepositoryActivity.created_at)
            ).limit(limit)
            
            result = await session.execute(query)
            activities = result.scalars().all()
            
            recent_activities = []
            for activity in activities:
                recent_activities.append({
                    'id': activity.id,
                    'repository': activity.repository_full_name,
                    'type': activity.activity_type,
                    'title': activity.title,
                    'author': activity.author,
                    'created_at': activity.created_at.isoformat() if activity.created_at else None,
                    'url': activity.url
                })
            
            logger.info(f"✅ 最近活动获取成功，共 {len(recent_activities)} 条")
            return recent_activities
            
    except Exception as e:
        logger.error(f"❌ 获取最近活动失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取最近活动失败: {str(e)}")


@router.get("/system-health")
async def get_system_health():
    """获取系统健康状态"""
    try:
        logger.info("🏥 开始获取系统健康状态")
        
        async with get_db_session() as session:
            # 检查数据库连接
            db_status = "healthy"
            try:
                await session.scalar(func.count(User.id))
            except Exception:
                db_status = "unhealthy"
            
            # 检查最近的活动
            recent_activity_time = await session.scalar(
                select(func.max(RepositoryActivity.created_at))
            )
            
            # 检查最近的报告
            recent_report_time = await session.scalar(
                select(func.max(Report.created_at))
            )
            
            # 计算系统运行时间（简化版本）
            uptime_hours = 24  # 这里可以实现真实的运行时间计算
            
            health_data = {
                'database': {
                    'status': db_status,
                    'last_check': datetime.now().isoformat()
                },
                'last_activity': recent_activity_time.isoformat() if recent_activity_time else None,
                'last_report': recent_report_time.isoformat() if recent_report_time else None,
                'uptime_hours': uptime_hours,
                'status': 'healthy' if db_status == 'healthy' else 'degraded'
            }
            
            logger.info(f"✅ 系统健康状态获取成功: {health_data['status']}")
            return health_data
            
    except Exception as e:
        logger.error(f"❌ 获取系统健康状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取系统状态失败: {str(e)}") 