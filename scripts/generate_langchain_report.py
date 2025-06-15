#!/usr/bin/env python3
"""
Langchain 仓库报告生成脚本
用于演示 GitHub Sentinel 的数据收集和报告生成功能
"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

# 获取项目根目录并切换工作目录
project_root = Path(__file__).parent.parent
os.chdir(project_root)
print(f"切换工作目录到: {project_root}")

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(project_root))

from app.collectors.github_collector import GitHubCollector
from app.core.config import get_settings
from loguru import logger


async def main():
    """主函数"""
    logger.info("开始生成 Langchain 仓库报告...")
    
    try:
        # 检查配置
        settings = get_settings()
        if not settings.github.token or settings.github.token == "your_github_token_here":
            logger.error("请先在 config/config.yml 中配置 GitHub Token")
            logger.info("配置文件路径: config/config.yml")
            logger.info("需要设置: github.token")
            return
            
        # 创建收集器
        collector = GitHubCollector()
        
        # 生成 Langchain 仓库报告
        owner = "langchain-ai"
        repo = "langchain"
        
        logger.info(f"正在收集 {owner}/{repo} 仓库数据...")
        
        # 生成报告
        report = await collector.generate_repository_report(owner, repo)
        
        # 保存报告到文件
        output_file = f"reports/langchain_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
            
        logger.success(f"报告已生成并保存到: {output_path}")
        logger.info("您可以查看报告内容了解 Langchain 仓库的最新动态")
        
        # 同时在控制台输出报告的前部分
        print("\n" + "="*80)
        print("📊 LANGCHAIN 仓库报告预览")
        print("="*80)
        print(report[:2000] + "\n...\n\n完整报告请查看文件: " + str(output_path))
        print("="*80)
        
    except Exception as e:
        logger.error(f"生成报告时发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 