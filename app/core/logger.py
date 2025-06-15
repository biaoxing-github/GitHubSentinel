"""
全局日志配置模块
统一管理整个应用的日志配置
"""

import sys
import os
from pathlib import Path
from loguru import logger
from app.core.config import get_settings


def setup_logger():
    """设置全局日志配置"""
    settings = get_settings()
    
    # 移除默认的logger
    logger.remove()
    
    # 确保日志目录存在
    log_file_path = Path(settings.log_file)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 控制台日志配置
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # 文件日志配置
    logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="1 day",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
        encoding="utf-8"
    )
    
    # 错误日志单独文件
    error_log_file = log_file_path.parent / "error.log"
    logger.add(
        str(error_log_file),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="1 day",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
        encoding="utf-8"
    )
    
    logger.info(f"📝 日志系统初始化完成 - 级别: {settings.log_level}, 文件: {settings.log_file}")
    return logger


def get_logger(name: str = None):
    """获取logger实例"""
    if name:
        return logger.bind(name=name)
    return logger


# 全局logger实例
app_logger = setup_logger() 