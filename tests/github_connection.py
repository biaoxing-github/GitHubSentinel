#!/usr/bin/env python3
"""
测试GitHub API连接
"""

import sys
import os
import asyncio
from pathlib import Path

# 获取项目根目录并切换工作目录
project_root = Path(__file__).parent.parent
os.chdir(project_root)
print(f"切换工作目录到: {project_root}")

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(project_root))

async def main():
    try:
        from app.collectors.github_collector import GitHubCollector
        from app.core.config import get_settings
        
        print("🔧 测试GitHub API连接")
        print("=" * 50)
        
        # 检查配置
        settings = get_settings()
        if not settings.github.token or len(settings.github.token) < 20:
            print("❌ GitHub Token 未正确配置")
            return
        
        print(f"✅ GitHub Token 已配置: {settings.github.token[:20]}...")
        
        # 创建收集器
        collector = GitHubCollector()
        
        # 测试获取仓库信息
        print("\n🚀 测试获取langchain仓库信息...")
        repo_info = await collector.get_repository_info("langchain-ai", "langchain")
        
        print(f"✅ API连接成功!")
        print(f"仓库名称: {repo_info['full_name']}")
        print(f"描述: {repo_info['description'][:100]}...")
        print(f"Stars: {repo_info['stargazers_count']}")
        print(f"语言: {repo_info['language']}")
        print(f"创建时间: {repo_info['created_at']}")
        
        print(f"\n🎉 GitHub API连接测试成功！现在可以生成完整报告了。")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 