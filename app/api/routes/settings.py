"""
系统设置相关的API路由
"""

import os
import yaml
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

CONFIG_FILE_PATH = "config/config.yml"

from app.core.logger import get_logger
logger = get_logger(__name__)


class SystemSettings(BaseModel):
    """系统设置模型"""
    # GitHub 配置
    github_token: str = ""
    github_api_base_url: str = "https://api.github.com"
    
    # 数据库配置
    database_url: str = "sqlite:///./github_sentinel.db"
    
    # Redis 配置
    redis_url: str = "redis://localhost:6379/0"
    
    # 邮件配置
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    
    # Slack 配置
    slack_webhook_url: str = ""
    
    # 调度配置
    schedule_enabled: bool = True
    default_report_frequency: str = "daily"
    
    # AI 配置
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    
    # 系统配置
    log_level: str = "INFO"
    max_workers: int = 4
    enable_notifications: bool = True


def load_config_file() -> Dict[str, Any]:
    """加载配置文件"""
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        else:
            return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取配置文件失败: {str(e)}")


def save_config_file(config: Dict[str, Any]):
    """保存配置文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)
        
        with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置文件失败: {str(e)}")


def config_to_settings(config: Dict[str, Any]) -> SystemSettings:
    """将配置字典转换为设置对象"""
    # 提取各个部分的配置
    github_config = config.get('github', {})
    database_config = config.get('database', {})
    redis_config = config.get('redis', {})
    notification_config = config.get('notification', {})
    ai_config = config.get('ai', {})
    schedule_config = config.get('schedule', {})
    
    # 构建Redis URL
    redis_url = f"redis://{redis_config.get('host', 'localhost')}:{redis_config.get('port', 6379)}/{redis_config.get('db', 0)}"
    if redis_config.get('password'):
        redis_url = f"redis://:{redis_config['password']}@{redis_config.get('host', 'localhost')}:{redis_config.get('port', 6379)}/{redis_config.get('db', 0)}"
    
    return SystemSettings(
        # GitHub 配置
        github_token=github_config.get('token', ''),
        github_api_base_url=github_config.get('api_url', 'https://api.github.com'),
        
        # 数据库配置
        database_url=database_config.get('url', 'sqlite:///./github_sentinel.db'),
        
        # Redis 配置
        redis_url=redis_url,
        
        # 邮件配置
        smtp_server=notification_config.get('email_smtp_host', ''),
        smtp_port=notification_config.get('email_smtp_port', 587),
        smtp_username=notification_config.get('email_username', ''),
        smtp_password=notification_config.get('email_password', ''),
        smtp_use_tls=True,  # 默认启用TLS
        
        # Slack 配置
        slack_webhook_url=notification_config.get('slack_webhook_url', ''),
        
        # 调度配置
        schedule_enabled=schedule_config.get('enabled', True),
        default_report_frequency='daily',  # 固定为daily
        
        # AI 配置
        openai_api_key=ai_config.get('openai_api_key', ''),
        openai_model=ai_config.get('openai_model', 'gpt-3.5-turbo'),
        
        # 系统配置
        log_level=config.get('log_level', 'INFO'),
        max_workers=4,  # 固定值
        enable_notifications=notification_config.get('enabled', True)
    )


def settings_to_config(settings: SystemSettings) -> Dict[str, Any]:
    """将设置对象转换为配置字典"""
    # 解析Redis URL
    redis_parts = settings.redis_url.replace('redis://', '').split('@')
    if len(redis_parts) == 2:
        # 有密码
        password = redis_parts[0].split(':')[1] if ':' in redis_parts[0] else None
        host_port_db = redis_parts[1]
    else:
        password = None
        host_port_db = redis_parts[0]
    
    host_port, db = host_port_db.split('/') if '/' in host_port_db else (host_port_db, '0')
    host, port = host_port.split(':') if ':' in host_port else (host_port, '6379')
    
    return {
        'app_name': "GitHub Sentinel",
        'app_version': "1.0.0",
        'debug': True,
        'github': {
            'token': settings.github_token,
            'api_url': settings.github_api_base_url,
            'max_requests_per_hour': 5000,
            'retry_attempts': 3,
            'retry_delay': 60
        },
        'database': {
            'url': settings.database_url,
            'echo': False,
            'pool_size': 5,
            'max_overflow': 10
        },
        'redis': {
            'host': host,
            'port': int(port),
            'password': password,
            'db': int(db),
            'enabled': False
        },
        'ai': {
            'provider': 'openai',
            'openai_api_key': settings.openai_api_key,
            'openai_model': settings.openai_model,
            'ollama_url': 'http://localhost:11434',
            'ollama_model': 'llama2',
            'max_tokens': 1000,
            'temperature': 0.7
        },
        'schedule': {
            'enabled': settings.schedule_enabled,
            'daily_time': '08:00',
            'weekly_day': 1,
            'weekly_time': '08:00',
            'timezone': 'Asia/Shanghai'
        },
        'notification': {
            'enabled': settings.enable_notifications,
            'email_enabled': bool(settings.smtp_server),
            'email_smtp_host': settings.smtp_server,
            'email_smtp_port': settings.smtp_port,
            'email_username': settings.smtp_username,
            'email_password': settings.smtp_password,
            'email_from': settings.smtp_username,
            'email_to': [settings.smtp_username] if settings.smtp_username else [],
            'slack_enabled': bool(settings.slack_webhook_url),
            'slack_webhook_url': settings.slack_webhook_url,
            'slack_channel': '#general',
            'webhook_enabled': False,
            'webhook_urls': []
        },
        'log_level': settings.log_level,
        'log_file': 'logs/github_sentinel.log',
        'secret_key': 'github-sentinel-secret-key-2024',
        'access_token_expire_minutes': 30000
    }


@router.get("/", response_model=SystemSettings)
@router.get("", response_model=SystemSettings)  # 添加不带斜杠的路由
async def get_settings():
    """获取系统设置"""

    try:
        logger.info("🔧 开始获取系统设置")
        logger.debug(f"📁 配置文件路径: {CONFIG_FILE_PATH}")
        logger.debug(f"📁 配置文件是否存在: {os.path.exists(CONFIG_FILE_PATH)}")
        
        config = load_config_file()
        logger.info(f"📋 原始配置内容: {config}")
        
        settings = config_to_settings(config)
        logger.info(f"⚙️ 转换后的设置: {settings.dict()}")
        logger.info("✅ 系统设置获取成功")
        
        return settings
    except Exception as e:
        logger.error(f"💥 获取系统设置失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取系统设置失败: {str(e)}")


@router.put("/", response_model=SystemSettings)
@router.put("", response_model=SystemSettings)  # 添加不带斜杠的路由
async def update_settings(settings: SystemSettings):
    """更新系统设置"""
    try:
        config = settings_to_config(settings)
        save_config_file(config)
        
        # 返回更新后的设置
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新系统设置失败: {str(e)}")


@router.get("/config-file")
async def get_config_file():
    """获取原始配置文件内容"""
    try:
        config = load_config_file()
        return {"config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置文件失败: {str(e)}")


@router.post("/reload")
async def reload_config():
    """重新加载配置"""
    try:
        config = load_config_file()
        settings = config_to_settings(config)
        return {
            "message": "配置重新加载成功", 
            "settings": settings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新加载配置失败: {str(e)}")


@router.get("/validation")
async def validate_settings():
    """验证当前设置"""
    try:
        config = load_config_file()
        settings = config_to_settings(config)
        
        validation_results = {
            "github_token": bool(settings.github_token),
            "database_configured": bool(settings.database_url),
            "redis_configured": bool(settings.redis_url),
            "email_configured": bool(settings.smtp_server and settings.smtp_username),
            "slack_configured": bool(settings.slack_webhook_url),
            "openai_configured": bool(settings.openai_api_key)
        }
        
        return {
            "validation_results": validation_results,
            "overall_valid": all(validation_results.values())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证设置失败: {str(e)}") 