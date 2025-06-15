"""
API 路由主文件
聚合所有 API 路由
"""

from fastapi import APIRouter
from app.api.routes import users, subscriptions, settings, reports, dashboard

# 创建主路由器
api_router = APIRouter()

# 根路由
@api_router.get("/")
async def root():
    """API根路由"""
    from loguru import logger
    logger.info("📡 API根路由访问")
    return {
        "message": "GitHub Sentinel API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

# 健康检查路由
@api_router.get("/health")
async def health_check():
    """健康检查接口"""
    from loguru import logger
    logger.info("💓 健康检查请求")
    return {
        "status": "healthy",
        "service": "GitHub Sentinel",
        "version": "1.0.0"
    }

# 添加路由模块
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"]) 