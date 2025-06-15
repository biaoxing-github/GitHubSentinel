#!/usr/bin/env python3
"""
GitHub Sentinel 配置修复和测试脚本
"""

import sys
import os
from pathlib import Path

# 获取项目根目录并切换工作目录
project_root = Path(__file__).parent.parent
original_cwd = os.getcwd()
os.chdir(project_root)

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(project_root))

def test_configuration():
    """测试配置加载"""
    print("🔧 GitHub Sentinel 配置修复和测试")
    print("=" * 60)
    
    # 1. 检查工作目录
    print(f"原始工作目录: {original_cwd}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"项目根目录: {project_root}")
    
    # 2. 检查配置文件
    config_yml = project_root / "config" / "config.yml"
    config_yaml = project_root / "config" / "config.yaml"
    
    print(f"\n📁 配置文件检查:")
    print(f"config.yml 存在: {config_yml.exists()} - {config_yml}")
    print(f"config.yaml 存在: {config_yaml.exists()} - {config_yaml}")
    
    # 3. 测试配置加载
    try:
        from app.core.config import get_settings
        print(f"\n⚙️  正在测试配置加载...")
        
        settings = get_settings()
        
        print(f"✅ 配置加载成功!")
        print(f"   应用名称: {settings.app_name}")
        print(f"   GitHub Token: {'已配置' if settings.github.token and len(settings.github.token) > 20 else '未配置'}")
        print(f"   OpenAI Key: {'已配置' if settings.ai.openai_api_key and len(settings.ai.openai_api_key) > 20 else '未配置'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_langchain_report():
    """测试生成Langchain报告"""
    print(f"\n🚀 测试Langchain报告生成...")
    
    try:
        import asyncio
        from app.collectors.github_collector import GitHubCollector
        from app.core.config import get_settings
        
        async def generate_test_report():
            settings = get_settings()
            
            if not settings.github.token or len(settings.github.token) < 20:
                print("❌ GitHub Token 未正确配置")
                return False
                
            collector = GitHubCollector()
            
            # 只获取基本信息，不生成完整报告
            print("正在测试GitHub API连接...")
            repo_info = await collector.get_repository_info("langchain-ai", "langchain")
            
            if repo_info:
                print(f"✅ GitHub API 连接成功!")
                print(f"   仓库: {repo_info['full_name']}")
                print(f"   描述: {repo_info['description'][:100]}...")
                print(f"   Stars: {repo_info['stargazers_count']}")
                return True
            else:
                print("❌ GitHub API 连接失败")
                return False
        
        return asyncio.run(generate_test_report())
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    success = True
    
    # 测试配置
    if not test_configuration():
        success = False
    
    # 测试GitHub连接
    if success:
        if not test_langchain_report():
            success = False
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 所有测试通过! 现在可以运行:")
        print("   python scripts/generate_langchain_report.py")
        print("   python main.py init")
        print("   python main.py server")
    else:
        print("❌ 存在问题，请检查上述错误信息")
    print("=" * 60)

if __name__ == "__main__":
    main() 