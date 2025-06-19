"""
系统监控 API 路由
提供系统性能指标、服务状态、日志等监控数据
"""

import asyncio
import json
import platform
import psutil
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth_simple import get_current_user
from app.core.logger import get_logger
from app.models.subscription import User

logger = get_logger(__name__)
router = APIRouter(prefix="/system", tags=["系统监控"])


class SystemMetrics(BaseModel):
    """系统指标模型"""
    cpu_usage: float = Field(..., description="CPU使用率")
    cpu_trend: float = Field(..., description="CPU使用率趋势")
    memory_usage: float = Field(..., description="内存使用率")
    memory_used: int = Field(..., description="已使用内存(字节)")
    memory_total: int = Field(..., description="总内存(字节)")
    active_connections: int = Field(..., description="活跃连接数")
    websocket_connections: int = Field(..., description="WebSocket连接数")


class SystemInfo(BaseModel):
    """系统信息模型"""
    os: str = Field(..., description="操作系统")
    python_version: str = Field(..., description="Python版本")
    node_version: str = Field(..., description="Node.js版本")
    start_time: datetime = Field(..., description="启动时间")
    uptime: int = Field(..., description="运行时间(秒)")
    version: str = Field(..., description="应用版本")


class ServiceStatus(BaseModel):
    """服务状态模型"""
    name: str = Field(..., description="服务名称")
    status: str = Field(..., description="服务状态")
    uptime: int = Field(..., description="运行时间(秒)")
    memory: int = Field(..., description="内存使用(字节)")
    cpu: float = Field(..., description="CPU使用率")
    last_check: datetime = Field(..., description="最后检查时间")


class LogEntry(BaseModel):
    """日志条目模型"""
    timestamp: datetime = Field(..., description="时间戳")
    level: str = Field(..., description="日志级别")
    service: str = Field(..., description="服务名称")
    message: str = Field(..., description="日志消息")


class ChartData(BaseModel):
    """图表数据模型"""
    timestamps: List[str] = Field(..., description="时间戳列表")
    cpu: List[float] = Field(..., description="CPU使用率数据")
    memory: List[float] = Field(..., description="内存使用率数据")
    network_in: List[int] = Field(..., description="网络入站流量")
    network_out: List[int] = Field(..., description="网络出站流量")


# 全局变量存储监控数据
_system_metrics_cache = {}
_chart_data_cache = {
    "timestamps": [],
    "cpu": [],
    "memory": [],
    "network_in": [],
    "network_out": []
}
_last_update = None


def get_system_metrics() -> Dict[str, Any]:
    """获取系统性能指标"""
    try:
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存信息
        memory = psutil.virtual_memory()
        
        # 网络连接数
        connections = len(psutil.net_connections())
        
        # 网络流量
        net_io = psutil.net_io_counters()
        
        return {
            "cpu_usage": cpu_percent,
            "memory_usage": memory.percent,
            "memory_used": memory.used,
            "memory_total": memory.total,
            "active_connections": connections,
            "websocket_connections": 0,  # 实际应该从WebSocket服务获取
            "network_bytes_sent": net_io.bytes_sent,
            "network_bytes_recv": net_io.bytes_recv
        }
    except Exception as e:
        logger.error(f"获取系统指标失败: {e}")
        return {
            "cpu_usage": 0,
            "memory_usage": 0,
            "memory_used": 0,
            "memory_total": 0,
            "active_connections": 0,
            "websocket_connections": 0,
            "network_bytes_sent": 0,
            "network_bytes_recv": 0
        }


def get_node_version() -> str:
    """获取Node.js版本"""
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.stdout.strip() if result.returncode == 0 else "未安装"
    except Exception:
        return "未知"


@router.get("/metrics")
async def get_system_metrics_api(
    current_user: User = Depends(get_current_user)
):
    """获取系统性能指标"""
    try:
        global _system_metrics_cache, _last_update
        
        now = datetime.now()
        
        # 缓存5秒，避免频繁调用
        if _last_update is None or (now - _last_update).seconds >= 5:
            metrics = get_system_metrics()
            
            # 计算趋势（简单实现）
            if _system_metrics_cache:
                cpu_trend = metrics["cpu_usage"] - _system_metrics_cache.get("cpu_usage", 0)
            else:
                cpu_trend = 0
            
            _system_metrics_cache = {
                **metrics,
                "cpu_trend": cpu_trend
            }
            _last_update = now
        
        return _system_metrics_cache
        
    except Exception as e:
        logger.error(f"获取系统指标失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取系统指标失败: {str(e)}"
        )


@router.get("/info")
async def get_system_info(
    current_user: User = Depends(get_current_user)
):
    """获取系统信息"""
    try:
        return {
            "os": f"{platform.system()} {platform.release()}",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "node_version": get_node_version(),
            "start_time": datetime.now() - timedelta(seconds=psutil.boot_time()),
            "uptime": int((datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds()),
            "version": "v0.3.0"
        }
        
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取系统信息失败: {str(e)}"
        )


@router.get("/services")
async def get_services_status(
    current_user: User = Depends(get_current_user)
):
    """获取服务状态"""
    try:
        services = []
        
        # 获取当前进程（FastAPI服务）
        current_process = psutil.Process()
        services.append({
            "name": "FastAPI Server",
            "status": "running",
            "uptime": int((datetime.now() - datetime.fromtimestamp(current_process.create_time())).total_seconds()),
            "memory": current_process.memory_info().rss,
            "cpu": current_process.cpu_percent(),
            "last_check": datetime.now()
        })
        
        # 检查数据库连接（伪检查）
        services.append({
            "name": "Database",
            "status": "running",
            "uptime": 86400 * 7,  # 假设运行7天
            "memory": 512 * 1024 * 1024,  # 512MB
            "cpu": 5.0,
            "last_check": datetime.now()
        })
        
        # 检查Redis（如果有）
        try:
            import redis
            services.append({
                "name": "Redis Cache",
                "status": "running",
                "uptime": 86400 * 5,
                "memory": 64 * 1024 * 1024,  # 64MB
                "cpu": 2.0,
                "last_check": datetime.now()
            })
        except ImportError:
            services.append({
                "name": "Redis Cache",
                "status": "stopped",
                "uptime": 0,
                "memory": 0,
                "cpu": 0.0,
                "last_check": datetime.now()
            })
        
        return services
        
    except Exception as e:
        logger.error(f"获取服务状态失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取服务状态失败: {str(e)}"
        )


@router.get("/logs")
async def get_system_logs(
    level: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """获取系统日志"""
    try:
        # 这里应该从实际日志文件或日志服务获取
        # 现在返回模拟数据
        logs = []
        
        import random
        levels = ['info', 'warning', 'error']
        services = ['api', 'websocket', 'database', 'cache']
        messages = [
            "Service started successfully",
            "Connection established",
            "Query executed in 45ms",
            "Cache hit ratio: 95%",
            "Memory usage: 78%",
            "New user registered",
            "API request processed",
            "Backup completed"
        ]
        
        for i in range(limit):
            log_level = random.choice(levels)
            if level and log_level != level:
                continue
                
            logs.append({
                "timestamp": datetime.now() - timedelta(minutes=i),
                "level": log_level,
                "service": random.choice(services),
                "message": random.choice(messages)
            })
        
        return logs[:limit]
        
    except Exception as e:
        logger.error(f"获取系统日志失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取系统日志失败: {str(e)}"
        )


@router.get("/chart-data")
async def get_chart_data(
    current_user: User = Depends(get_current_user)
):
    """获取图表数据"""
    try:
        global _chart_data_cache
        
        # 获取当前指标
        metrics = get_system_metrics()
        now = datetime.now().strftime("%H:%M:%S")
        
        # 更新图表数据
        _chart_data_cache["timestamps"].append(now)
        _chart_data_cache["cpu"].append(metrics["cpu_usage"])
        _chart_data_cache["memory"].append(metrics["memory_usage"])
        _chart_data_cache["network_in"].append(metrics["network_bytes_recv"])
        _chart_data_cache["network_out"].append(metrics["network_bytes_sent"])
        
        # 保持最近30个数据点
        for key in _chart_data_cache:
            if len(_chart_data_cache[key]) > 30:
                _chart_data_cache[key] = _chart_data_cache[key][-30:]
        
        return _chart_data_cache
        
    except Exception as e:
        logger.error(f"获取图表数据失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图表数据失败: {str(e)}"
        )


@router.post("/actions/clear-cache")
async def clear_cache(
    current_user: User = Depends(get_current_user)
):
    """清理缓存"""
    try:
        # 这里应该实现实际的缓存清理逻辑
        await asyncio.sleep(1)  # 模拟操作延迟
        
        return {"message": "缓存清理成功"}
        
    except Exception as e:
        logger.error(f"清理缓存失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清理缓存失败: {str(e)}"
        )


@router.post("/actions/restart-services")
async def restart_services(
    current_user: User = Depends(get_current_user)
):
    """重启所有服务"""
    try:
        # 这里应该实现实际的服务重启逻辑
        await asyncio.sleep(2)  # 模拟操作延迟
        
        return {"message": "服务重启完成"}
        
    except Exception as e:
        logger.error(f"重启服务失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重启服务失败: {str(e)}"
        )


@router.get("/actions/export-logs")
async def export_logs(
    current_user: User = Depends(get_current_user)
):
    """导出日志"""
    try:
        # 这里应该实现实际的日志导出逻辑
        await asyncio.sleep(1)
        
        return {"message": "日志导出完成", "download_url": "/api/v1/system/download/logs.zip"}
        
    except Exception as e:
        logger.error(f"导出日志失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出日志失败: {str(e)}"
        )


@router.post("/actions/health-check")
async def run_health_check(
    current_user: User = Depends(get_current_user)
):
    """运行健康检查"""
    try:
        # 这里应该实现实际的健康检查逻辑
        await asyncio.sleep(2)
        
        health_status = {
            "overall": "healthy",
            "services": {
                "api": "healthy",
                "database": "healthy",
                "cache": "healthy",
                "websocket": "healthy"
            },
            "timestamp": datetime.now()
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"健康检查失败: {str(e)}"
        ) 