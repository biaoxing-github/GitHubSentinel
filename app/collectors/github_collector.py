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
from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import get_db_session
from app.models.subscription import Subscription, RepositoryActivity, SubscriptionStatus, ReportFrequency
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
        if not date_string:
            return None
            
        try:
            if date_string.endswith('Z'):
                # GitHub API返回的UTC时间格式
                return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            else:
                return datetime.fromisoformat(date_string)
        except ValueError:
            # 如果解析失败，尝试其他格式
            try:
                return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
            except ValueError:
                logger.warning(f"无法解析时间字符串: {date_string}")
                return None
        
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
            logger.error(f"收集仓库数据失败 {owner}/{repo}: {e}", exc_info=True)
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
                "body": (issue_data.get("body") or "")[:1000],  # 限制长度
                "state": issue_data["state"],
                "user": {
                    "login": issue_data.get("user", {}).get("login", "unknown") if issue_data.get("user") else "unknown",
                    "avatar_url": issue_data.get("user", {}).get("avatar_url", "") if issue_data.get("user") else ""
                },
                "labels": [label["name"] for label in issue_data.get("labels", [])],
                "assignees": [assignee["login"] for assignee in issue_data.get("assignees", [])],
                "milestone": issue_data.get("milestone", {}).get("title", "") if issue_data.get("milestone") else "",
                "comments": issue_data.get("comments", 0),
                "created_at": issue_data["created_at"],
                "updated_at": issue_data["updated_at"],
                "closed_at": issue_data.get("closed_at"),
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
                    "login": pr_data.get("user", {}).get("login", "unknown") if pr_data.get("user") else "unknown",
                    "avatar_url": pr_data.get("user", {}).get("avatar_url", "") if pr_data.get("user") else ""
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
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC",
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
        """收集每日更新数据"""
        logger.info("开始收集每日更新数据")
        
        async with get_db_session() as session:
            # 获取所有活跃订阅
            subscriptions = await session.execute(
                select(Subscription).where(
                    Subscription.status == SubscriptionStatus.ACTIVE,
                    Subscription.frequency.in_([ReportFrequency.DAILY])
                )
            )
            subscriptions = subscriptions.scalars().all()
            
            success_count = 0
            error_count = 0
            collected_data = []
            
            for subscription in subscriptions:
                try:
                    owner, repo = subscription.repository.split('/')
                    data = await self.collect_repository_activities(
                        subscription, 
                        days=1,
                        include_states=['open', 'closed', 'merged']
                    )
                    collected_data.append(data)
                    success_count += 1
                    
                    # 发送通知
                    await self._send_activity_notifications(subscription, data)
                    
                except Exception as e:
                    logger.error(f"收集订阅 {subscription.id} 数据失败: {e}")
                    error_count += 1
            
            return {
                "success_count": success_count,
                "error_count": error_count,
                "collected_data": collected_data,
                "total_subscriptions": len(subscriptions)
            }

    async def collect_weekly_updates(self) -> Dict[str, Any]:
        """收集每周更新数据"""
        logger.info("开始收集每周更新数据")
        
        async with get_db_session() as session:
            # 获取所有活跃的周报订阅
            subscriptions = await session.execute(
                select(Subscription).where(
                    Subscription.status == SubscriptionStatus.ACTIVE,
                    Subscription.frequency.in_([ReportFrequency.WEEKLY])
                )
            )
            subscriptions = subscriptions.scalars().all()
            
            success_count = 0
            error_count = 0
            collected_data = []
            
            for subscription in subscriptions:
                try:
                    data = await self.collect_repository_activities(
                        subscription, 
                        days=7,
                        include_states=['open', 'closed', 'merged']
                    )
                    collected_data.append(data)
                    success_count += 1
                    
                    # 发送通知
                    await self._send_activity_notifications(subscription, data)
                    
                except Exception as e:
                    logger.error(f"收集订阅 {subscription.id} 数据失败: {e}")
                    error_count += 1
            
            return {
                "success_count": success_count,
                "error_count": error_count,
                "collected_data": collected_data,
                "total_subscriptions": len(subscriptions)
            }

    async def collect_repository_activities(
        self, 
        subscription: Subscription, 
        days: int = 7,
        include_states: List[str] = None
    ) -> Dict[str, Any]:
        """
        收集仓库活动数据并存储到数据库
        
        Args:
            subscription: 订阅对象
            days: 收集天数
            include_states: 包含的状态列表
        """
        if include_states is None:
            include_states = ['open', 'closed']
            
        owner, repo = subscription.repository.split('/')
        logger.info(f"收集仓库活动: {owner}/{repo} (最近{days}天)")
        
        try:
            async with httpx.AsyncClient() as client:
                activities = []
                
                # 根据订阅配置收集不同类型的活动
                if subscription.monitor_commits:
                    commits = await self._get_recent_commits(client, owner, repo, days)
                    activities.extend(self._convert_commits_to_activities(commits, subscription.id))
                
                if subscription.monitor_issues:
                    issues = await self._get_recent_issues_by_state(client, owner, repo, days, include_states)
                    activities.extend(self._convert_issues_to_activities(issues, subscription.id))
                
                if subscription.monitor_pull_requests:
                    prs = await self._get_recent_pull_requests_by_state(client, owner, repo, days, include_states)
                    activities.extend(self._convert_prs_to_activities(prs, subscription.id))
                
                if subscription.monitor_releases:
                    releases = await self._get_recent_releases(client, owner, repo, limit=10)
                    activities.extend(self._convert_releases_to_activities(releases, subscription.id))
                
                # 存储活动数据到数据库
                stored_activities = await self._store_activities(activities)
                
                # 更新订阅的最后同步时间
                await self._update_subscription_sync_time(subscription.id)
                
                return {
                    "subscription_id": subscription.id,
                    "repository": subscription.repository,
                    "activities": stored_activities,
                    "total_activities": len(stored_activities),
                    "collected_at": self._utc_now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"收集仓库活动失败 {owner}/{repo}: {e}")
            raise

    async def _get_recent_issues_by_state(
        self, 
        client: httpx.AsyncClient, 
        owner: str, 
        repo: str, 
        days: int,
        include_states: List[str]
    ) -> List[Dict[str, Any]]:
        """根据状态获取最近的Issues"""
        since = (self._utc_now() - timedelta(days=days)).isoformat()
        all_issues = []
        
        for state in include_states:
            if state not in ['open', 'closed', 'all']:
                continue
                
            url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            params = {
                "state": state,
                "since": since,
                "per_page": 50,
                "sort": "updated"
            }
            
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            for issue_data in response.json():
                # 跳过 Pull Requests
                if "pull_request" in issue_data:
                    continue
                    
                all_issues.append({
                    "number": issue_data["number"],
                    "title": issue_data["title"],
                    "body": (issue_data.get("body") or "")[:1000],  # 限制长度
                    "state": issue_data["state"],
                    "user": {
                        "login": issue_data.get("user", {}).get("login", "unknown") if issue_data.get("user") else "unknown",
                        "avatar_url": issue_data.get("user", {}).get("avatar_url", "") if issue_data.get("user") else ""
                    },
                    "labels": [label["name"] for label in issue_data.get("labels", [])],
                    "assignees": [assignee["login"] for assignee in issue_data.get("assignees", [])],
                    "milestone": issue_data.get("milestone", {}).get("title", "") if issue_data.get("milestone") else "",
                    "comments": issue_data.get("comments", 0),
                    "created_at": issue_data["created_at"],
                    "updated_at": issue_data["updated_at"],
                    "closed_at": issue_data.get("closed_at"),
                    "html_url": issue_data["html_url"]
                })
        
        # 去重（同一个issue可能在不同状态查询中出现）
        unique_issues = {}
        for issue in all_issues:
            unique_issues[issue["number"]] = issue
        
        return list(unique_issues.values())

    async def _get_recent_pull_requests_by_state(
        self, 
        client: httpx.AsyncClient, 
        owner: str, 
        repo: str, 
        days: int,
        include_states: List[str]
    ) -> List[Dict[str, Any]]:
        """根据状态获取最近的Pull Requests"""
        cutoff_date = self._utc_now() - timedelta(days=days)
        all_prs = []
        
        for state in include_states:
            if state not in ['open', 'closed', 'all']:
                continue
                
            url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
            params = {
                "state": state,
                "per_page": 50,
                "sort": "updated",
                "direction": "desc"
            }
            
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            for pr_data in response.json():
                updated_at = self._parse_github_datetime(pr_data["updated_at"])
                if updated_at < cutoff_date:
                    continue
                    
                all_prs.append({
                    "number": pr_data["number"],
                    "title": pr_data["title"],
                    "body": (pr_data.get("body") or "")[:1000],
                    "state": pr_data["state"],
                    "user": {
                        "login": pr_data.get("user", {}).get("login", "unknown") if pr_data.get("user") else "unknown",
                        "avatar_url": pr_data.get("user", {}).get("avatar_url", "") if pr_data.get("user") else ""
                    },
                    "labels": [label["name"] for label in pr_data.get("labels", [])],
                    "assignees": [assignee["login"] for assignee in pr_data.get("assignees", [])],
                    "milestone": pr_data.get("milestone", {}).get("title", "") if pr_data.get("milestone") else "",
                    "comments": pr_data.get("comments", 0),
                    "commits": pr_data.get("commits", 0),
                    "additions": pr_data.get("additions", 0),
                    "deletions": pr_data.get("deletions", 0),
                    "changed_files": pr_data.get("changed_files", 0),
                    "merged": pr_data.get("merged", False),
                    "merged_at": pr_data.get("merged_at"),
                    "draft": pr_data.get("draft", False),
                    "created_at": pr_data["created_at"],
                    "updated_at": pr_data["updated_at"],
                    "closed_at": pr_data.get("closed_at"),
                    "html_url": pr_data["html_url"]
                })
        
        # 去重
        unique_prs = {}
        for pr in all_prs:
            unique_prs[pr["number"]] = pr
        
        return list(unique_prs.values())

    def _convert_commits_to_activities(self, commits: List[Dict], subscription_id: int) -> List[Dict]:
        """将提交数据转换为活动记录"""
        activities = []
        for commit in commits:
            activities.append({
                "subscription_id": subscription_id,
                "activity_type": "commit",
                "activity_id": commit["sha"],
                "title": commit["message"].split('\n')[0][:500],  # 取第一行作为标题
                "description": commit["message"][:1000],
                "url": commit["html_url"],
                "author_login": commit["author"]["login"],
                "author_name": commit["author"]["name"],
                "github_created_at": self._parse_github_datetime(commit["date"]),
                "github_updated_at": self._parse_github_datetime(commit["date"])
            })
        return activities

    def _convert_issues_to_activities(self, issues: List[Dict], subscription_id: int) -> List[Dict]:
        """将Issue数据转换为活动记录"""
        activities = []
        for issue in issues:
            activities.append({
                "subscription_id": subscription_id,
                "activity_type": "issue",
                "activity_id": str(issue["number"]),
                "title": issue["title"][:500],
                "description": issue["body"][:1000],
                "url": issue["html_url"],
                "author_login": issue["user"]["login"],
                "author_avatar_url": issue["user"]["avatar_url"],
                "labels": json.dumps(issue["labels"]),
                "assignees": json.dumps(issue["assignees"]),
                "milestone": issue["milestone"],
                "comments_count": issue.get("comments", 0),
                "state": issue["state"],
                "github_created_at": self._parse_github_datetime(issue["created_at"]),
                "github_updated_at": self._parse_github_datetime(issue["updated_at"])
            })
        return activities

    def _convert_prs_to_activities(self, prs: List[Dict], subscription_id: int) -> List[Dict]:
        """将PR数据转换为活动记录"""
        activities = []
        for pr in prs:
            activities.append({
                "subscription_id": subscription_id,
                "activity_type": "pull_request",
                "activity_id": str(pr["number"]),
                "title": pr["title"][:500],
                "description": pr["body"][:1000],
                "url": pr["html_url"],
                "author_login": pr["user"]["login"],
                "author_avatar_url": pr["user"]["avatar_url"],
                "labels": json.dumps(pr["labels"]),
                "assignees": json.dumps(pr["assignees"]),
                "milestone": pr["milestone"],
                "comments_count": pr.get("comments", 0),
                "state": pr["state"],
                "is_draft": pr.get("draft", False),
                "is_merged": pr.get("merged", False),
                "github_created_at": self._parse_github_datetime(pr["created_at"]),
                "github_updated_at": self._parse_github_datetime(pr["updated_at"])
            })
        return activities

    def _convert_releases_to_activities(self, releases: List[Dict], subscription_id: int) -> List[Dict]:
        """将Release数据转换为活动记录"""
        activities = []
        for release in releases:
            activities.append({
                "subscription_id": subscription_id,
                "activity_type": "release",
                "activity_id": str(release["id"]),
                "title": release["name"] or release["tag_name"],
                "description": release["body"][:1000],
                "url": release["html_url"],
                "author_login": release["author"]["login"],
                "author_avatar_url": release["author"]["avatar_url"],
                "github_created_at": self._parse_github_datetime(release["created_at"]),
                "github_updated_at": self._parse_github_datetime(release["published_at"] or release["created_at"])
            })
        return activities

    async def _store_activities(self, activities: List[Dict]) -> List[Dict]:
        """存储活动数据到数据库"""
        if not activities:
            return []
            
        async with get_db_session() as session:
            stored_activities = []
            
            for activity_data in activities:
                # 检查是否已存在
                existing = await session.execute(
                    select(RepositoryActivity).where(
                        RepositoryActivity.subscription_id == activity_data["subscription_id"],
                        RepositoryActivity.activity_type == activity_data["activity_type"],
                        RepositoryActivity.activity_id == activity_data["activity_id"]
                    )
                )
                existing = existing.scalar_one_or_none()
                
                if existing:
                    # 更新现有记录
                    for key, value in activity_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    stored_activities.append(existing)
                else:
                    # 创建新记录
                    activity = RepositoryActivity(**activity_data)
                    session.add(activity)
                    stored_activities.append(activity)
            
            await session.commit()
            
            # 转换为字典格式返回
            return [
                {
                    "id": activity.id,
                    "activity_type": activity.activity_type,
                    "title": activity.title,
                    "author_login": activity.author_login,
                    "created_at": activity.github_created_at.isoformat() if activity.github_created_at else None,
                    "url": activity.url
                }
                for activity in stored_activities
            ]

    async def _update_subscription_sync_time(self, subscription_id: int) -> None:
        """更新订阅的最后同步时间"""
        async with get_db_session() as session:
            subscription = await session.get(Subscription, subscription_id)
            if subscription:
                subscription.last_sync_at = self._utc_now()
                await session.commit()

    async def _send_activity_notifications(self, subscription: Subscription, data: Dict[str, Any]) -> None:
        """发送活动通知"""
        if not data.get("activities"):
            return
            
        try:
            from app.services.notification_service import NotificationService
            
            notification_service = NotificationService()
            
            # 为每个新活动发送通知
            for activity in data["activities"]:
                activity_data = {
                    "activity_type": activity["activity_type"],
                    "activity_title": activity["title"],
                    "activity_author": activity["author_login"],
                    "activity_url": activity["url"],
                    "activity_time": activity["created_at"]
                }
                
                await notification_service.send_subscription_notification(
                    subscription, 
                    activity_data, 
                    "activity"
                )
                
        except Exception as e:
            logger.error(f"发送活动通知失败: {e}")

    async def collect_all(self) -> Dict[str, Any]:
        """收集所有订阅的仓库数据"""
        return {"success_count": 0, "error_count": 0}
        
    async def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """获取仓库基本信息（公开方法）"""
        async with httpx.AsyncClient() as client:
            return await self._get_repository_info(client, owner, repo) 