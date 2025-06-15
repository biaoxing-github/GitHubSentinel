#!/usr/bin/env python3
"""
GitHub Sentinel - 主入口文件
自动获取并汇总 GitHub 仓库动态的 AI Agent
"""

import asyncio
import sys
from pathlib import Path

import click
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import get_settings
from app.core.database import init_database
from app.core.scheduler import TaskScheduler
from app.api.main import api_router
from app.api.middleware.logging import LoggingMiddleware


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    settings = get_settings()
    
    app = FastAPI(
        title="GitHub Sentinel",
        description="自动获取并汇总 GitHub 仓库动态的 AI Agent",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # 添加日志记录中间件
    app.add_middleware(LoggingMiddleware)
    
    # 配置 CORS 中间件，支持前后端分离
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000", 
            "http://127.0.0.1:3000", 
            "http://localhost:4000",  # 前端Vite开发服务器
            "http://127.0.0.1:4000",
            "http://localhost:5173", 
            "http://127.0.0.1:5173",
            "http://localhost:8080",
            "http://127.0.0.1:8080"
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(api_router, prefix="/api/v1")
    
    # 添加异常处理器
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        from loguru import logger
        logger.warning(f"❌ 404错误: {request.method} {request.url}")
        return JSONResponse(
            status_code=404,
            content={
                "detail": "资源未找到",
                "path": str(request.url),
                "method": request.method,
                "available_endpoints": {
                    "health": "/api/v1/health",
                    "users": "/api/v1/users",
                    "subscriptions": "/api/v1/subscriptions", 
                    "settings": "/api/v1/settings",
                    "docs": "/docs"
                }
            }
        )
    
    @app.exception_handler(500)
    async def internal_error_handler(request, exc):
        from loguru import logger
        logger.error(f"💥 500错误: {request.method} {request.url} - {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "内部服务器错误",
                "path": str(request.url),
                "method": request.method
            }
        )
    
    # 应用启动事件
    @app.on_event("startup")
    async def startup_event():
        logger.info("GitHub Sentinel 正在启动...")
        
        # 初始化数据库
        await init_database()
        logger.info("数据库初始化完成")
        
        # 启动任务调度器
        scheduler = TaskScheduler()
        await scheduler.start()
        logger.info("任务调度器启动完成")
        
        logger.info("GitHub Sentinel 启动完成！")
    
    # 应用关闭事件
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("GitHub Sentinel 正在关闭...")
        
        # 停止任务调度器
        scheduler = TaskScheduler()
        await scheduler.stop()
        
        logger.info("GitHub Sentinel 已关闭")
    
    return app


@click.group()
def cli():
    """GitHub Sentinel CLI 工具"""
    pass


@cli.command()
@click.option("--host", default="0.0.0.0", help="服务器主机地址")
@click.option("--port", default=8000, help="服务器端口")
@click.option("--reload", is_flag=True, help="开发模式，代码变更时自动重启")
def serve(host: str, port: int, reload: bool):
    """启动 GitHub Sentinel 服务器"""
    logger.info(f"启动服务器 - {host}:{port}")
    
    uvicorn.run(
        "main:create_app",
        factory=True,
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


@cli.command()
def init():
    """初始化数据库和配置"""
    logger.info("正在初始化 GitHub Sentinel...")
    
    async def init_async():
        await init_database()
        logger.info("数据库初始化完成")
    
    asyncio.run(init_async())


@cli.command()
@click.option("--repo", required=True, help="GitHub 仓库 (格式: owner/repo)")
def add_subscription(repo: str):
    """添加 GitHub 仓库订阅"""
    from app.services.subscription_service import SubscriptionService
    
    async def add_async():
        service = SubscriptionService()
        await service.add_subscription(repository=repo)
        logger.info(f"已添加订阅: {repo}")
    
    asyncio.run(add_async())


@cli.command()
def collect():
    """手动触发数据收集任务"""
    from app.collectors.github_collector import GitHubCollector
    
    async def collect_async():
        collector = GitHubCollector()
        await collector.collect_all()
        logger.info("数据收集完成")
    
    asyncio.run(collect_async())


if __name__ == "__main__":
    # 使用全局日志配置
    from app.core.logger import app_logger as logger
    
    cli() 