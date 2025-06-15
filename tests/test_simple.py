#!/usr/bin/env python3
"""
简单的配置测试脚本
"""

import sys
import os
from pathlib import Path

# 获取项目根目录并切换工作目录
project_root = Path(__file__).parent.parent
print(f"项目根目录: {project_root}")
print(f"切换前工作目录: {os.getcwd()}")

os.chdir(project_root)
print(f"切换后工作目录: {os.getcwd()}")

# 检查配置文件
config_yml = Path("config/config.yml")
config_yaml = Path("config/config.yaml")

print(f"\n配置文件检查:")
print(f"config/config.yml 存在: {config_yml.exists()}")
print(f"config/config.yaml 存在: {config_yaml.exists()}")

if config_yml.exists():
    print(f"config.yml 大小: {config_yml.stat().st_size} bytes")
if config_yaml.exists():
    print(f"config.yaml 大小: {config_yaml.stat().st_size} bytes")

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(project_root))

try:
    from app.core.config import get_settings
    print("\n正在加载配置...")
    settings = get_settings()
    print("✅ 配置加载成功!")
    print(f"GitHub Token: {'已配置' if settings.github.token and len(settings.github.token) > 20 else '未配置'}")
except Exception as e:
    print(f"❌ 配置加载失败: {e}")
    import traceback
    traceback.print_exc() 