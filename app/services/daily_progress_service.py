"""
每日进展服务
获取项目的issues和pull requests，生成Markdown文件
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from app.core.logger import get_logger
from app.collectors.github_collector import GitHubCollector
from app.utils.timezone_utils import beijing_now, format_beijing_time

logger = get_logger(__name__)


class DailyProgressService:
    """每日进展服务"""
    
    def __init__(self):
        self.github_collector = GitHubCollector()
        self.output_dir = Path("reports/daily_progress")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_daily_progress(self, repository: str, date: Optional[datetime] = None) -> str:
        """
        生成指定仓库的每日进展Markdown文件
        
        Args:
            repository: 仓库名称 (owner/repo)
            date: 指定日期，默认为昨天
        
        Returns:
            str: 生成的Markdown文件路径
        """
        if date is None:
            date = beijing_now().date() - timedelta(days=1)
        
        logger.info(f"开始生成 {repository} 的每日进展报告 - {date}")
        
        try:
            owner, repo = repository.split('/')
            
            # 获取issues和pull requests
            issues_data = await self._get_daily_issues(owner, repo, date)
            prs_data = await self._get_daily_pull_requests(owner, repo, date)
            
            # 生成Markdown内容
            markdown_content = self._generate_markdown_content(
                repository, date, issues_data, prs_data
            )
            
            # 保存文件
            filename = f"{repository.replace('/', '_')}_{date.strftime('%Y-%m-%d')}.md"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"每日进展报告已生成: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"生成每日进展报告失败: {e}")
            raise
    
    async def _get_daily_issues(self, owner: str, repo: str, date: datetime) -> List[Dict[str, Any]]:
        """获取指定日期的issues"""
        try:
            # 设置时间范围（北京时间）
            start_time = datetime.combine(date, datetime.min.time())
            end_time = start_time + timedelta(days=1)
            
            async with self.github_collector._get_client() as client:
                issues = await self.github_collector._get_recent_issues_by_state(
                    client, owner, repo, days=1, include_states=['open', 'closed']
                )
                
                # 过滤指定日期的issues
                daily_issues = []
                for issue in issues:
                    created_at = self.github_collector._parse_github_datetime(issue['created_at'])
                    updated_at = self.github_collector._parse_github_datetime(issue['updated_at'])
                    
                    # 检查是否在指定日期创建或更新
                    if (start_time <= created_at < end_time or 
                        start_time <= updated_at < end_time):
                        daily_issues.append(issue)
                
                return daily_issues
                
        except Exception as e:
            logger.error(f"获取issues失败: {e}")
            return []
    
    async def _get_daily_pull_requests(self, owner: str, repo: str, date: datetime) -> List[Dict[str, Any]]:
        """获取指定日期的pull requests"""
        try:
            # 设置时间范围
            start_time = datetime.combine(date, datetime.min.time())
            end_time = start_time + timedelta(days=1)
            
            async with self.github_collector._get_client() as client:
                prs = await self.github_collector._get_recent_pull_requests_by_state(
                    client, owner, repo, days=1, include_states=['open', 'closed', 'merged']
                )
                
                # 过滤指定日期的PRs
                daily_prs = []
                for pr in prs:
                    created_at = self.github_collector._parse_github_datetime(pr['created_at'])
                    updated_at = self.github_collector._parse_github_datetime(pr['updated_at'])
                    
                    # 检查是否在指定日期创建或更新
                    if (start_time <= created_at < end_time or 
                        start_time <= updated_at < end_time):
                        daily_prs.append(pr)
                
                return daily_prs
                
        except Exception as e:
            logger.error(f"获取pull requests失败: {e}")
            return []
    
    def _generate_markdown_content(
        self, 
        repository: str, 
        date: datetime, 
        issues: List[Dict[str, Any]], 
        prs: List[Dict[str, Any]]
    ) -> str:
        """生成Markdown内容"""
        
        content = f"""# {repository} 每日进展报告

**日期**: {date.strftime('%Y年%m月%d日')}  
**生成时间**: {format_beijing_time(beijing_now())}  
**仓库**: [{repository}](https://github.com/{repository})

---

## 📊 概览

- **Issues**: {len(issues)} 个
- **Pull Requests**: {len(prs)} 个
- **总活动**: {len(issues) + len(prs)} 项

---

## 🐛 Issues ({len(issues)})

"""
        
        if issues:
            # 按状态分组
            open_issues = [i for i in issues if i['state'] == 'open']
            closed_issues = [i for i in issues if i['state'] == 'closed']
            
            if open_issues:
                content += f"### 🔓 新增/更新的开放Issues ({len(open_issues)})\n\n"
                for issue in open_issues:
                    content += self._format_issue_item(issue)
                content += "\n"
            
            if closed_issues:
                content += f"### ✅ 已关闭的Issues ({len(closed_issues)})\n\n"
                for issue in closed_issues:
                    content += self._format_issue_item(issue)
                content += "\n"
        else:
            content += "今日无Issues活动。\n\n"
        
        content += f"""---

## 🔄 Pull Requests ({len(prs)})

"""
        
        if prs:
            # 按状态分组
            open_prs = [p for p in prs if p['state'] == 'open']
            merged_prs = [p for p in prs if p.get('merged', False)]
            closed_prs = [p for p in prs if p['state'] == 'closed' and not p.get('merged', False)]
            
            if open_prs:
                content += f"### 🔓 新增/更新的开放PRs ({len(open_prs)})\n\n"
                for pr in open_prs:
                    content += self._format_pr_item(pr)
                content += "\n"
            
            if merged_prs:
                content += f"### ✅ 已合并的PRs ({len(merged_prs)})\n\n"
                for pr in merged_prs:
                    content += self._format_pr_item(pr)
                content += "\n"
            
            if closed_prs:
                content += f"### ❌ 已关闭的PRs ({len(closed_prs)})\n\n"
                for pr in closed_prs:
                    content += self._format_pr_item(pr)
                content += "\n"
        else:
            content += "今日无Pull Request活动。\n\n"
        
        content += """---

## 📈 活动统计

| 类型 | 数量 | 状态分布 |
|------|------|----------|
"""
        
        if issues:
            open_count = len([i for i in issues if i['state'] == 'open'])
            closed_count = len([i for i in issues if i['state'] == 'closed'])
            content += f"| Issues | {len(issues)} | 开放: {open_count}, 关闭: {closed_count} |\n"
        
        if prs:
            open_count = len([p for p in prs if p['state'] == 'open'])
            merged_count = len([p for p in prs if p.get('merged', False)])
            closed_count = len([p for p in prs if p['state'] == 'closed' and not p.get('merged', False)])
            content += f"| Pull Requests | {len(prs)} | 开放: {open_count}, 合并: {merged_count}, 关闭: {closed_count} |\n"
        
        content += f"""
---

*报告由 GitHub Sentinel 自动生成*
"""
        
        return content
    
    def _format_issue_item(self, issue: Dict[str, Any]) -> str:
        """格式化Issue条目"""
        labels = ", ".join([f"`{label}`" for label in issue.get('labels', [])])
        labels_text = f" 🏷️ {labels}" if labels else ""
        
        assignees = ", ".join([f"@{assignee}" for assignee in issue.get('assignees', [])])
        assignees_text = f" 👤 {assignees}" if assignees else ""
        
        return f"""- **[#{issue['number']}]({issue['html_url']})** {issue['title']}
  - 👤 作者: @{issue['user']['login']}
  - 📅 创建: {format_beijing_time(self.github_collector._parse_github_datetime(issue['created_at']))}
  - 📅 更新: {format_beijing_time(self.github_collector._parse_github_datetime(issue['updated_at']))}
  - 💬 评论: {issue['comments']} 条{labels_text}{assignees_text}

"""
    
    def _format_pr_item(self, pr: Dict[str, Any]) -> str:
        """格式化PR条目"""
        labels = ", ".join([f"`{label}`" for label in pr.get('labels', [])])
        labels_text = f" 🏷️ {labels}" if labels else ""
        
        changes_text = f" 📝 +{pr['additions']}/-{pr['deletions']}" if 'additions' in pr else ""
        
        status_emoji = "✅" if pr.get('merged') else ("🔓" if pr['state'] == 'open' else "❌")
        
        return f"""- **{status_emoji} [#{pr['number']}]({pr['html_url']})** {pr['title']}
  - 👤 作者: @{pr['user']['login']}
  - 📅 创建: {format_beijing_time(self.github_collector._parse_github_datetime(pr['created_at']))}
  - 📅 更新: {format_beijing_time(self.github_collector._parse_github_datetime(pr['updated_at']))}
  - 💬 评论: {pr['comments']} 条{changes_text}{labels_text}

"""
    
    async def batch_generate_daily_progress(self, repositories: List[str], date: Optional[datetime] = None) -> List[str]:
        """批量生成多个仓库的每日进展报告"""
        generated_files = []
        
        for repository in repositories:
            try:
                filepath = await self.generate_daily_progress(repository, date)
                generated_files.append(filepath)
            except Exception as e:
                logger.error(f"生成 {repository} 的每日进展报告失败: {e}")
        
        return generated_files 