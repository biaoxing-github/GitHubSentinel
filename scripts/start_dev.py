#!/usr/bin/env python3
"""
GitHub Sentinel 开发环境启动脚本
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import yaml
        print("✓ PyYAML 已安装")
    except ImportError:
        print("✗ PyYAML 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "PyYAML"], check=True)
        print("✓ PyYAML 安装完成")

def check_config():
    """检查配置文件"""
    config_path = Path("config/config.yml")
    if not config_path.exists():
        print(f"✗ 配置文件不存在: {config_path}")
        return False
    print("✓ 配置文件存在")
    return True

def init_database():
    """初始化数据库"""
    try:
        subprocess.run([sys.executable, "main.py", "init"], check=True)
        print("✓ 数据库初始化成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 数据库初始化失败: {e}")
        return False

def start_backend():
    """启动后端服务"""
    print("启动后端服务...")
    try:
        subprocess.run([sys.executable, "main.py", "server"], check=True)
    except KeyboardInterrupt:
        print("\n后端服务已停止")

def start_frontend():
    """启动前端开发服务器"""
    print("启动前端开发服务器...")
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("✗ 前端目录不存在")
        return False
    
    try:
        os.chdir(frontend_path)
        # 检查是否安装了依赖
        if not Path("node_modules").exists():
            print("安装前端依赖...")
            subprocess.run(["npm", "install"], check=True)
        
        subprocess.run(["npm", "run", "dev"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"✗ 前端启动失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n前端服务已停止")

def main():
    """主函数"""
    print("GitHub Sentinel 开发环境启动")
    print("=" * 40)
    
    # 检查依赖
    check_dependencies()
    
    # 检查配置
    if not check_config():
        print("请先配置 config/config.yml 文件")
        return
    
    # 初始化数据库
    if not init_database():
        print("数据库初始化失败，请检查配置")
        return
    
    # 选择启动模式
    print("\n选择启动模式:")
    print("1. 只启动后端")
    print("2. 只启动前端")
    print("3. 同时启动前端和后端")
    
    choice = input("请输入选择 (1-3): ").strip()
    
    if choice == "1":
        start_backend()
    elif choice == "2":
        start_frontend()
    elif choice == "3":
        print("同时启动模式需要手动操作:")
        print("1. 在一个终端运行: python main.py server")
        print("2. 在另一个终端运行: cd frontend && npm run dev")
    else:
        print("无效选择")

if __name__ == "__main__":
    main() 