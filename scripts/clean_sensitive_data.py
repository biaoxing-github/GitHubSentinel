#!/usr/bin/env python3
"""
清理项目中的敏感信息脚本
用于在提交代码前清理所有敏感数据
"""

import os
import re
import shutil
from pathlib import Path


def clean_config_files():
    """清理配置文件中的敏感信息"""
    print("🧹 清理配置文件...")
    
    # 删除包含真实密钥的配置文件
    sensitive_configs = [
        "config/config.yaml",
        "config/config.yml"
    ]
    
    for config_file in sensitive_configs:
        if os.path.exists(config_file):
            print(f"  删除敏感配置文件: {config_file}")
            os.remove(config_file)
    
    print("  ✅ 配置文件清理完成")


def clean_log_files():
    """清理日志文件"""
    print("🧹 清理日志文件...")
    
    log_patterns = [
        "logs/*.log",
        "*.log",
        "logs/github_sentinel.log"
    ]
    
    for pattern in log_patterns:
        for log_file in Path(".").glob(pattern):
            if log_file.exists():
                print(f"  删除日志文件: {log_file}")
                log_file.unlink()
    
    # 重新创建空的日志目录
    os.makedirs("logs", exist_ok=True)
    
    print("  ✅ 日志文件清理完成")


def clean_database_files():
    """清理数据库文件"""
    print("🧹 清理数据库文件...")
    
    db_files = [
        "github_sentinel.db",
        "*.sqlite",
        "*.sqlite3",
        "*.db"
    ]
    
    for pattern in db_files:
        for db_file in Path(".").glob(pattern):
            if db_file.exists():
                print(f"  删除数据库文件: {db_file}")
                db_file.unlink()
    
    print("  ✅ 数据库文件清理完成")


def clean_temp_files():
    """清理临时文件"""
    print("🧹 清理临时文件...")
    
    temp_patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        "dist",
        "build",
        "*.egg-info",
        ".DS_Store",
        "Thumbs.db",
        "*.swp",
        "*.swo",
        "*~"
    ]
    
    for pattern in temp_patterns:
        for temp_file in Path(".").rglob(pattern):
            if temp_file.exists():
                if temp_file.is_dir():
                    print(f"  删除临时目录: {temp_file}")
                    shutil.rmtree(temp_file)
                else:
                    print(f"  删除临时文件: {temp_file}")
                    temp_file.unlink()
    
    print("  ✅ 临时文件清理完成")


def clean_frontend_files():
    """清理前端构建文件"""
    print("🧹 清理前端文件...")
    
    frontend_patterns = [
        "frontend/node_modules",
        "frontend/dist",
        "frontend/build",
        "frontend/.vite",
        "frontend/.cache"
    ]
    
    for pattern in frontend_patterns:
        path = Path(pattern)
        if path.exists():
            if path.is_dir():
                print(f"  删除前端目录: {path}")
                shutil.rmtree(path)
            else:
                print(f"  删除前端文件: {path}")
                path.unlink()
    
    print("  ✅ 前端文件清理完成")


def verify_gitignore():
    """验证.gitignore文件是否正确配置"""
    print("🔍 验证 .gitignore 配置...")
    
    required_patterns = [
        "config/config.yaml",
        "config/config.yml",
        "*.log",
        "logs/",
        "*.db",
        "*.sqlite",
        "github_sentinel.db",
        "__pycache__/",
        "node_modules/",
        ".env"
    ]
    
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print("  ❌ .gitignore 文件不存在")
        return False
    
    gitignore_content = gitignore_path.read_text(encoding='utf-8')
    
    missing_patterns = []
    for pattern in required_patterns:
        if pattern not in gitignore_content:
            missing_patterns.append(pattern)
    
    if missing_patterns:
        print(f"  ⚠️  .gitignore 中缺少以下模式: {missing_patterns}")
        return False
    
    print("  ✅ .gitignore 配置正确")
    return True


def create_example_config():
    """确保示例配置文件存在"""
    print("📝 检查示例配置文件...")
    
    example_config = Path("config/config.example.yaml")
    if not example_config.exists():
        print("  ❌ config.example.yaml 不存在")
        return False
    
    print("  ✅ 示例配置文件存在")
    return True


def main():
    """主函数"""
    print("🚀 开始清理项目敏感信息...")
    print("=" * 50)
    
    # 清理各种敏感文件
    clean_config_files()
    clean_log_files()
    clean_database_files()
    clean_temp_files()
    clean_frontend_files()
    
    print("\n" + "=" * 50)
    print("🔍 验证项目配置...")
    
    # 验证配置
    gitignore_ok = verify_gitignore()
    example_config_ok = create_example_config()
    
    print("\n" + "=" * 50)
    
    if gitignore_ok and example_config_ok:
        print("✅ 项目清理完成！可以安全提交代码。")
        print("\n📋 下一步操作：")
        print("1. 复制配置文件: cp config/config.example.yaml config/config.yaml")
        print("2. 编辑配置文件: nano config/config.yaml")
        print("3. 设置必要的密钥和配置")
        print("4. 提交代码: git add . && git commit -m 'feat: clean sensitive data'")
    else:
        print("❌ 项目清理过程中发现问题，请检查上述错误信息。")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 