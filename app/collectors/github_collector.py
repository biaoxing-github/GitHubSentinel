"""
GitHub 数据收集器
用于获取 GitHub 仓库的最新信息并生成报告
"""

import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional

import httpx
from loguru import logger

from app.core.config import get_settings
from app.core.database import get_db_session
from app.models.subscription import Subscription, RepositoryActivity
from app.models.report import Report, ReportStatus, ReportType


class GitHubCollector:
    """GitHub 数据收集器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.headers = {
            "Authorization": f"token {self.settings.github.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Sentinel/1.0.0"
        }
        self.base_url = self.settings.github.api_url
        
    def _utc_now(self) -> datetime:
        """获取带时区信息的UTC当前时间"""
        return datetime.now(timezone.utc)

    def _parse_github_datetime(self, date_string: str) -> datetime:
        """解析GitHub API返回的时间字符串"""
        if date_string.endswith('Z'):
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        else:
            return datetime.fromisoformat(date_string)
        
    async def collect_repository_data(self, owner: str, repo: str) -> Dict[str, Any]:
        """收集单个仓库的完整数据"""
        logger.info(f"开始收集仓库数据: {owner}/{repo}")
        
        try:
            async with httpx.AsyncClient() as client:
                # 获取仓库基本信息
                repo_info = await self._get_repository_info(client, owner, repo)
                
                # 获取最新的提交
                commits = await self._get_recent_commits(client, owner, repo)
                
                # 获取最新的 Issues
                issues = await self._get_recent_issues(client, owner, repo)
                
                # 获取最新的 Pull Requests
                pull_requests = await self._get_recent_pull_requests(client, owner, repo)
                
                # 获取最新的 Releases
                releases = await self._get_recent_releases(client, owner, repo)
                
                # 汇总数据
                collected_data = {
                    "repository": repo_info,
                    "commits": commits,
                    "issues": issues,
                    "pull_requests": pull_requests,
                    "releases": releases,
                    "collected_at": self._utc_now().isoformat(),
                    "summary": {
                        "commits_count": len(commits),
                        "issues_count": len(issues),
                        "pull_requests_count": len(pull_requests),
                        "releases_count": len(releases)
                    }
                }
                
                logger.info(f"仓库数据收集完成: {owner}/{repo}")
                return collected_data
                
        except Exception as e:
            logger.error(f"收集仓库数据失败 {owner}/{repo}: {e}")
            raise
            
    async def _get_repository_info(self, client: httpx.AsyncClient, owner: str, repo: str) -> Dict[str, Any]:
        """获取仓库基本信息"""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = await client.get(url, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        return {
            "name": data["name"],
            "full_name": data["full_name"],
            "description": data.get("description", ""),
            "html_url": data["html_url"],
            "language": data.get("language", ""),
            "stargazers_count": data["stargazers_count"],
            "forks_count": data["forks_count"],
            "watchers_count": data["watchers_count"],
            "open_issues_count": data["open_issues_count"],
            "created_at": data["created_at"],
            "updated_at": data["updated_at"],
            "pushed_at": data["pushed_at"],
            "default_branch": data["default_branch"],
            "topics": data.get("topics", []),
            "license": data.get("license", {}).get("name", "") if data.get("license") else "",
            "size": data["size"]
        }
        
    async def _get_recent_commits(self, client: httpx.AsyncClient, owner: str, repo: str, days: int = 7) -> List[Dict[str, Any]]:
        """获取最近的提交"""
        since = (self._utc_now() - timedelta(days=days)).isoformat()
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {
            "since": since,
            "per_page": 50
        }
        
        response = await client.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        commits = []
        for commit_data in response.json():
            commits.append({
                "sha": commit_data["sha"],
                "message": commit_data["commit"]["message"],
                "author": {
                    "name": commit_data["commit"]["author"]["name"],
                    "email": commit_data["commit"]["author"]["email"],
                    "login": commit_data.get("author", {}).get("login", "") if commit_data.get("author") else ""
                },
                "date": commit_data["commit"]["author"]["date"],
                "html_url": commit_data["html_url"]
            })
            
        return commits
        
    async def _get_recent_issues(self, client: httpx.AsyncClient, owner: str, repo: str, days: int = 7) -> List[Dict[str, Any]]:
        """获取最近的 Issues"""
        since = (self._utc_now() - timedelta(days=days)).isoformat()
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {
            "state": "all",
            "since": since,
            "per_page": 50,
            "sort": "updated"
        }
        
        response = await client.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        issues = []
        for issue_data in response.json():
            # 跳过 Pull Requests
            if "pull_request" in issue_data:
                continue
                
            issues.append({
                "number": issue_data["number"],
                "title": issue_data["title"],
                "body": issue_data.get("body", "")[:500],
                "state": issue_data["state"],
                "user": {
                    "login": issue_data["user"]["login"],
                    "avatar_url": issue_data["user"]["avatar_url"]
                },
                "labels": [label["name"] for label in issue_data.get("labels", [])],
                "comments": issue_data["comments"],
                "created_at": issue_data["created_at"],
                "updated_at": issue_data["updated_at"],
                "html_url": issue_data["html_url"]
            })
            
        return issues
        
    async def _get_recent_pull_requests(self, client: httpx.AsyncClient, owner: str, repo: str, days: int = 7) -> List[Dict[str, Any]]:
        """获取最近的 Pull Requests"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        params = {
            "state": "all",
            "per_page": 50,
            "sort": "updated",
            "direction": "desc"
        }
        
        response = await client.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        cutoff_date = self._utc_now() - timedelta(days=days)
        pull_requests = []
        
        for pr_data in response.json():
            updated_at = self._parse_github_datetime(pr_data["updated_at"])
            if updated_at < cutoff_date:
                continue
                
            pull_requests.append({
                "number": pr_data["number"],
                "title": pr_data["title"],
                "state": pr_data["state"],
                "user": {
                    "login": pr_data["user"]["login"],
                    "avatar_url": pr_data["user"]["avatar_url"]
                },
                "merged": pr_data.get("merged", False),
                "created_at": pr_data["created_at"],
                "updated_at": pr_data["updated_at"],
                "html_url": pr_data["html_url"]
            })
            
        return pull_requests
        
    async def _get_recent_releases(self, client: httpx.AsyncClient, owner: str, repo: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的发布"""
        url = f"{self.base_url}/repos/{owner}/{repo}/releases"
        params = {
            "per_page": limit
        }
        
        response = await client.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        releases = []
        for release_data in response.json():
            releases.append({
                "id": release_data["id"],
                "tag_name": release_data["tag_name"],
                "name": release_data.get("name", ""),
                "body": release_data.get("body", "")[:1000],
                "draft": release_data["draft"],
                "prerelease": release_data["prerelease"],
                "author": {
                    "login": release_data["author"]["login"],
                    "avatar_url": release_data["author"]["avatar_url"]
                },
                "created_at": release_data["created_at"],
                "published_at": release_data["published_at"],
                "html_url": release_data["html_url"]
            })
            
        return releases
        
    async def generate_repository_report(self, owner: str, repo: str) -> str:
        """生成仓库报告"""
        logger.info(f"开始生成仓库报告: {owner}/{repo}")
        
        try:
            # 收集数据
            data = await self.collect_repository_data(owner, repo)
            
            # 生成报告
            report = await self._format_repository_report(data)
            
            logger.info(f"仓库报告生成完成: {owner}/{repo}")
            return report
            
        except Exception as e:
            logger.error(f"生成仓库报告失败 {owner}/{repo}: {e}")
            raise
            
    async def _format_repository_report(self, data: Dict[str, Any]) -> str:
        """格式化仓库报告"""
        repo = data["repository"]
        summary = data["summary"]
        
        # 生成 Markdown 格式的报告
        report_lines = [
            f"# 📊 {repo['full_name']} 仓库报告",
            f"",
            f"**生成时间**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            f"",
            f"## 📈 仓库概览",
            f"",
            f"- **描述**: {repo['description']}",
            f"- **主要语言**: {repo['language']}",
            f"- **Star 数**: {repo['stargazers_count']:,}",
            f"- **Fork 数**: {repo['forks_count']:,}",
            f"- **Watch 数**: {repo['watchers_count']:,}",
            f"- **Open Issues**: {repo['open_issues_count']:,}",
            f"- **仓库大小**: {repo['size']:,} KB",
            f"- **许可证**: {repo['license'] or '未知'}",
            f"- **创建时间**: {repo['created_at']}",
            f"- **最后更新**: {repo['updated_at']}",
            f"",
            f"**主题标签**: {', '.join(repo['topics']) if repo['topics'] else '无'}",
            f"",
            f"## 📊 最近活动统计（7天内）",
            f"",
            f"| 类型 | 数量 |",
            f"|------|------|",
            f"| 💾 Commits | {summary['commits_count']} |",
            f"| 🐛 Issues | {summary['issues_count']} |",
            f"| 🔧 Pull Requests | {summary['pull_requests_count']} |",
            f"| 🚀 Releases | {summary['releases_count']} |",
            f"",
        ]
        
        # 添加最新发布信息
        if data["releases"]:
            report_lines.extend([
                f"## 🚀 最新发布",
                f""
            ])
            latest_release = data["releases"][0]
            report_lines.extend([
                f"**{latest_release['tag_name']}** - {latest_release.get('name', '')}",
                f"",
                f"- **发布时间**: {latest_release['published_at']}",
                f"- **作者**: {latest_release['author']['login']}",
                f"- **预发布**: {'是' if latest_release['prerelease'] else '否'}",
                f"",
                f"**发布说明**:",
                f"```",
                f"{latest_release['body'][:500]}{'...' if len(latest_release['body']) > 500 else ''}",
                f"```",
                f""
            ])
        
        return "\n".join(report_lines)
        
    async def collect_daily_updates(self) -> Dict[str, Any]:
        """每日数据收集任务"""
        return {"success_count": 0, "error_count": 0}
        
    async def collect_weekly_updates(self) -> Dict[str, Any]:
        """每周数据收集任务"""
        return {"success_count": 0, "error_count": 0}
        
    async def collect_all(self) -> Dict[str, Any]:
        """收集所有订阅的仓库数据"""
        return {"success_count": 0, "error_count": 0}
        
    async def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """获取仓库基本信息（公开方法）"""
        async with httpx.AsyncClient() as client:
            return await self._get_repository_info(client, owner, repo) 