"""
配置管理模块
使用 Pydantic Settings 管理应用配置
"""

import os
import yaml
from functools import lru_cache
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    """数据库配置"""
    url: str = Field(default="sqlite+aiosqlite:///./github_sentinel.db", description="数据库连接URL")
    echo: bool = Field(default=False, description="是否打印SQL语句")
    pool_size: int = Field(default=5, description="连接池大小")
    max_overflow: int = Field(default=10, description="连接池最大溢出")


class RedisConfig(BaseModel):
    """Redis 配置"""
    host: str = Field(default="localhost", description="Redis主机")
    port: int = Field(default=6379, description="Redis端口")
    password: Optional[str] = Field(default=None, description="Redis密码")
    db: int = Field(default=0, description="Redis数据库")
    enabled: bool = Field(default=False, description="是否启用Redis")


class GitHubConfig(BaseModel):
    """GitHub API 配置"""
    token: str = Field(description="GitHub Personal Access Token")
    api_url: str = Field(default="https://api.github.com", description="GitHub API URL")
    max_requests_per_hour: int = Field(default=5000, description="每小时最大请求数")
    retry_attempts: int = Field(default=3, description="重试次数")
    retry_delay: int = Field(default=60, description="重试延迟(秒)")


class AIConfig(BaseModel):
    """AI 服务配置"""
    provider: str = Field(default="openai", description="AI服务提供商 (openai/ollama)")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API Key")
    openai_model: str = Field(default="gpt-3.5-turbo", description="OpenAI模型")
    ollama_url: str = Field(default="http://localhost:11434", description="Ollama服务URL")
    ollama_model: str = Field(default="llama2", description="Ollama模型")
    max_tokens: int = Field(default=1000, description="最大生成tokens")
    temperature: float = Field(default=0.7, description="生成温度")


class ScheduleConfig(BaseModel):
    """调度配置"""
    enabled: bool = Field(default=True, description="是否启用调度")
    daily_time: str = Field(default="08:00", description="每日执行时间")
    weekly_day: int = Field(default=1, description="每周执行日期(1-7)")
    weekly_time: str = Field(default="08:00", description="每周执行时间")
    timezone: str = Field(default="Asia/Shanghai", description="时区")


class NotificationConfig(BaseModel):
    """通知配置"""
    enabled: bool = Field(default=True, description="是否启用通知")
    
    # 邮件配置
    email_enabled: bool = Field(default=False, description="是否启用邮件通知")
    email_smtp_host: str = Field(default="smtp.gmail.com", description="SMTP主机")
    email_smtp_port: int = Field(default=587, description="SMTP端口")
    email_username: str = Field(default="", description="邮件用户名")
    email_password: str = Field(default="", description="邮件密码")
    email_from: str = Field(default="", description="发件人")
    email_to: List[str] = Field(default_factory=list, description="收件人列表")
    
    # Slack配置
    slack_enabled: bool = Field(default=False, description="是否启用Slack通知")
    slack_webhook_url: str = Field(default="", description="Slack Webhook URL")
    slack_channel: str = Field(default="#general", description="Slack频道")
    
    # Webhook配置
    webhook_enabled: bool = Field(default=False, description="是否启用Webhook通知")
    webhook_urls: List[str] = Field(default_factory=list, description="Webhook URL列表")


def load_yaml_config(config_path: str = "config/config.yml") -> Dict[str, Any]:
    """加载YAML配置文件"""
    # 优先顺序：config.yml -> config.yaml -> 默认配置
    config_files_to_try = [
        "config/config.yml",
        "config/config.yaml"
    ]
    
    config_data = {}
    config_loaded = False
    
    for config_file in config_files_to_try:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
                    print(f"Info: 成功加载配置文件: {config_file}")
                    config_loaded = True
                    break
            except Exception as e:
                print(f"Error: 读取配置文件 {config_file} 失败: {e}")
                continue
    
    if not config_loaded:
        print(f"Warning: 未找到配置文件 ({', '.join(config_files_to_try)})，使用默认配置")
    
    return config_data


class Settings(BaseSettings):
    """应用配置"""
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore"
    )
    
    # 应用基础配置
    app_name: str = Field(default="GitHub Sentinel", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    
    # 各模块配置
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    github: GitHubConfig = Field(default_factory=lambda: GitHubConfig(token=""))
    ai: AIConfig = Field(default_factory=AIConfig)
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)
    notification: NotificationConfig = Field(default_factory=NotificationConfig)
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: str = Field(default="logs/github_sentinel.log", description="日志文件")
    
    # 安全配置
    secret_key: str = Field(default="your-secret-key-here", description="密钥")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间(分钟)")

    def __init__(self, **kwargs):
        # 加载YAML配置
        yaml_config = load_yaml_config()
        
        # 合并YAML配置到kwargs
        for key, value in yaml_config.items():
            if key not in kwargs:
                kwargs[key] = value
        
        super().__init__(**kwargs)


@lru_cache()
def get_settings() -> Settings:
    """获取应用配置实例"""
    return Settings() 