"""
PWA (Progressive Web App) API 路由 (v0.3.0)
提供Web App Manifest、Service Worker、离线页面等PWA功能接口
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse, Response, HTMLResponse
from pydantic import BaseModel, Field

from app.core.auth_simple import get_current_user
from app.core.logger import get_logger
from app.models.subscription import User
from app.services.pwa_service import pwa_service

logger = get_logger(__name__)
router = APIRouter(prefix="/pwa", tags=["PWA功能"])


@router.get("/manifest.json")
async def get_manifest(request: Request):
    """获取 Web App Manifest"""
    try:
        manifest = pwa_service.generate_manifest(request)
        return JSONResponse(
            content=manifest,
            headers={
                "Content-Type": "application/manifest+json",
                "Cache-Control": "public, max-age=86400"  # 缓存1天
            }
        )
    except Exception as e:
        logger.error(f"💥 生成manifest失败: {e}")
        return JSONResponse(
            content={"error": "生成manifest失败"},
            status_code=500
        )


@router.get("/sw.js")
async def get_service_worker():
    """获取 Service Worker"""
    try:
        sw_content = pwa_service.generate_service_worker()
        return Response(
            content=sw_content,
            media_type="application/javascript",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    except Exception as e:
        logger.error(f"💥 生成Service Worker失败: {e}")
        return Response(
            content="// Service Worker 生成失败",
            media_type="application/javascript",
            status_code=500
        )


@router.get("/offline.html")
async def get_offline_page():
    """获取离线页面"""
    try:
        offline_html = pwa_service.generate_offline_page()
        return HTMLResponse(
            content=offline_html,
            headers={
                "Cache-Control": "public, max-age=86400"  # 缓存1天
            }
        )
    except Exception as e:
        logger.error(f"💥 生成离线页面失败: {e}")
        return HTMLResponse(
            content="<html><body><h1>离线页面不可用</h1></body></html>",
            status_code=500
        )


@router.get("/install-config")
async def get_install_config(
    current_user: User = Depends(get_current_user)
):
    """获取应用安装配置"""
    try:
        config = pwa_service.get_install_prompt_config()
        return config
    except Exception as e:
        logger.error(f"💥 获取安装配置失败: {e}")
        return {"error": "获取安装配置失败"}


@router.get("/notification-config")
async def get_notification_config(
    current_user: User = Depends(get_current_user)
):
    """获取通知配置"""
    try:
        config = pwa_service.get_notification_config()
        return config
    except Exception as e:
        logger.error(f"💥 获取通知配置失败: {e}")
        return {"error": "获取通知配置失败"}


@router.get("/client-config")
async def get_client_config():
    """获取客户端配置"""
    try:
        config = pwa_service.generate_client_config()
        return config
    except Exception as e:
        logger.error(f"💥 获取客户端配置失败: {e}")
        return {"error": "获取客户端配置失败"}


class InstallMetricsRequest(BaseModel):
    """安装统计请求模型"""
    event_type: str = Field(..., description="事件类型: prompt_shown, installed, dismissed")
    user_agent: str = Field(..., description="用户代理")
    platform: str = Field(..., description="平台信息")


@router.post("/install-metrics")
async def track_install_metrics(
    request: InstallMetricsRequest,
    current_user: User = Depends(get_current_user)
):
    """追踪应用安装统计"""
    try:
        # 这里可以记录安装统计数据
        logger.info(f"📊 PWA安装统计 - 用户: {current_user.id}, 事件: {request.event_type}, 平台: {request.platform}")
        
        return {
            "message": "统计数据已记录",
            "event_type": request.event_type,
            "user_id": current_user.id
        }
    except Exception as e:
        logger.error(f"💥 记录安装统计失败: {e}")
        return {"error": "记录统计数据失败"}


@router.get("/cache-status")
async def get_cache_status(
    current_user: User = Depends(get_current_user)
):
    """获取缓存状态"""
    try:
        # 这里可以返回缓存相关的状态信息
        return {
            "cache_version": pwa_service.cache_version,
            "app_name": pwa_service.app_name,
            "features": {
                "offline_support": True,
                "background_sync": True,
                "push_notifications": True,
                "install_prompt": True
            },
            "status": "active"
        }
    except Exception as e:
        logger.error(f"💥 获取缓存状态失败: {e}")
        return {"error": "获取缓存状态失败"} 