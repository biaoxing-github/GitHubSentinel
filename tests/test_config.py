#!/usr/bin/env python3
"""
测试配置加载功能
"""

import sys
from pathlib import Path
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import get_settings

def main():
    """测试配置加载"""
    print("=" * 60)
    print("GitHub Sentinel 配置测试")
    print("=" * 60)
    
    # 显示当前工作目录
    print(f"当前工作目录: {os.getcwd()}")
    print(f"脚本目录: {Path(__file__).parent}")
    print(f"项目根目录: {Path(__file__).parent.parent}")
    
    # 检查配置文件是否存在
    config_yml = Path("config/config.yml")
    config_yaml = Path("config/config.yaml")
    
    print(f"\n配置文件检查:")
    print(f"config/config.yml 存在: {config_yml.exists()}")
    print(f"config/config.yaml 存在: {config_yaml.exists()}")
    
    # 尝试加载配置
    try:
        print(f"\n正在加载配置...")
        settings = get_settings()
        
        print(f"应用名称: {settings.app_name}")
        print(f"应用版本: {settings.app_version}")
        print(f"调试模式: {settings.debug}")
        
        # 检查GitHub配置
        print(f"\nGitHub 配置:")
        print(f"Token: {settings.github.token[:20]}..." if settings.github.token else "未配置")
        print(f"API URL: {settings.github.api_url}")
        
        # 检查AI配置
        print(f"\nAI 配置:")
        print(f"提供商: {settings.ai.provider}")
        print(f"OpenAI Key: {settings.ai.openai_api_key[:20]}..." if settings.ai.openai_api_key else "未配置")
        print(f"OpenAI 模型: {settings.ai.openai_model}")
        
        print(f"\n✅ 配置加载成功！")
        
        # 检查是否可以运行GitHub收集器
        if settings.github.token and settings.github.token != "your_github_token_here":
            print(f"✅ GitHub Token 已配置，可以运行数据收集")
        else:
            print(f"❌ GitHub Token 未正确配置")
            
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 