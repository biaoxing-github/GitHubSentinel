"""
Slack通知器
支持Webhook消息发送和富文本格式
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx

from app.core.config import get_config
from app.core.logger import get_logger

logger = get_logger(__name__)


class SlackNotifier:
    """Slack通知器"""
    
    def __init__(self):
        self.config = get_config()
        self.notification_config = self.config.notification
    
    async def send_message(
        self,
        text: str,
        blocks: Optional[List[Dict]] = None,
        channel: Optional[str] = None,
        username: Optional[str] = None,
        icon_emoji: Optional[str] = None
    ) -> bool:
        """发送Slack消息"""
        try:
            # 检查配置
            if not self.notification_config.slack_enabled:
                logger.warning("Slack通知未启用")
                return False
            
            if not self.notification_config.slack_webhook_url:
                logger.error("Slack Webhook URL未配置")
                return False
            
            # 构建消息payload
            payload = {
                "text": text,
                "channel": channel or self.notification_config.slack_channel,
                "username": username or "GitHub Sentinel",
                "icon_emoji": icon_emoji or ":robot_face:"
            }
            
            # 添加富文本块
            if blocks:
                payload["blocks"] = blocks
            
            # 发送消息
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.notification_config.slack_webhook_url,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info("Slack消息发送成功")
                    return True
                else:
                    logger.error(f"Slack消息发送失败: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Slack消息发送异常: {str(e)}")
            return False
    
    def _create_report_blocks(self, report_data: Dict[str, Any]) -> List[Dict]:
        """创建报告消息的Slack块"""
        blocks = []
        
        # 标题块
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📊 GitHub Sentinel {report_data.get('type', '报告')}"
            }
        })
        
        # 日期和统计信息
        total_repos = len(report_data.get('repositories', []))
        total_activities = sum(len(repo.get('activities', [])) for repo in report_data.get('repositories', []))
        
        blocks.append({
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*日期:* {report_data.get('date', datetime.now().strftime('%Y-%m-%d'))}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*监控仓库:* {total_repos}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*总活动数:* {total_activities}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*生成时间:* {datetime.now().strftime('%H:%M:%S')}"
                }
            ]
        })
        
        # 分隔线
        blocks.append({"type": "divider"})
        
        # 仓库详情
        for repo in report_data.get('repositories', [])[:5]:  # 限制显示前5个仓库
            repo_name = repo.get('name', '未知仓库')
            activities_count = len(repo.get('activities', []))
            summary = repo.get('summary', '暂无摘要')
            
            # 仓库标题
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📁 {repo_name}*\n{summary[:200]}{'...' if len(summary) > 200 else ''}"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": f"查看 ({activities_count})"
                    },
                    "url": f"https://github.com/{repo_name}",
                    "action_id": f"view_repo_{repo_name.replace('/', '_')}"
                }
            })
            
            # 显示部分活动
            if repo.get('activities'):
                activity_text = ""
                for activity in repo.get('activities', [])[:3]:  # 显示前3个活动
                    activity_type = activity.get('type', 'OTHER')
                    activity_title = activity.get('title', '无标题')
                    activity_author = activity.get('author', '未知')
                    
                    # 活动类型图标
                    type_icons = {
                        'commit': '💾',
                        'issue': '🐛',
                        'pull_request': '🔀',
                        'release': '🚀',
                        'discussion': '💬'
                    }
                    icon = type_icons.get(activity_type.lower(), '📝')
                    
                    activity_text += f"{icon} {activity_title[:50]}{'...' if len(activity_title) > 50 else ''} _by {activity_author}_\n"
                
                if activity_text:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": activity_text.strip()
                        }
                    })
        
        # 如果有更多仓库，显示提示
        if len(report_data.get('repositories', [])) > 5:
            remaining = len(report_data.get('repositories', [])) - 5
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"还有 {remaining} 个仓库的详细信息，请查看完整报告。"
                    }
                ]
            })
        
        # 底部信息
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "🤖 此报告由 GitHub Sentinel 自动生成"
                }
            ]
        })
        
        return blocks
    
    async def send_report_notification(
        self,
        report_data: Dict[str, Any],
        channel: Optional[str] = None
    ) -> bool:
        """发送报告通知到Slack"""
        try:
            # 创建简单文本消息
            total_repos = len(report_data.get('repositories', []))
            total_activities = sum(len(repo.get('activities', [])) for repo in report_data.get('repositories', []))
            
            text = f"📊 GitHub Sentinel {report_data.get('type', '报告')} - {report_data.get('date', datetime.now().strftime('%Y-%m-%d'))}\n"
            text += f"监控了 {total_repos} 个仓库，共 {total_activities} 个活动"
            
            # 创建富文本块
            blocks = self._create_report_blocks(report_data)
            
            return await self.send_message(
                text=text,
                blocks=blocks,
                channel=channel
            )
            
        except Exception as e:
            logger.error(f"发送Slack报告通知失败: {str(e)}")
            return False
    
    async def send_subscription_notification(
        self,
        subscription_data: Dict[str, Any],
        channel: Optional[str] = None
    ) -> bool:
        """发送订阅通知到Slack"""
        try:
            repository = subscription_data.get('repository', '未知仓库')
            activity_type = subscription_data.get('activity_type', '未知')
            activity_title = subscription_data.get('activity_title', '无标题')
            activity_author = subscription_data.get('activity_author', '未知')
            activity_url = subscription_data.get('activity_url', '#')
            
            # 活动类型图标
            type_icons = {
                'commit': '💾',
                'issue': '🐛',
                'pull_request': '🔀',
                'release': '🚀',
                'discussion': '💬'
            }
            icon = type_icons.get(activity_type.lower(), '📝')
            
            text = f"{icon} {repository} 有新的 {activity_type} 活动"
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"📢 订阅通知 - {repository}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{icon} *{activity_title}*\n_by {activity_author}_"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "查看详情"
                        },
                        "url": activity_url,
                        "action_id": "view_activity"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"🕒 {subscription_data.get('activity_time', '刚刚')}"
                        }
                    ]
                }
            ]
            
            return await self.send_message(
                text=text,
                blocks=blocks,
                channel=channel
            )
            
        except Exception as e:
            logger.error(f"发送Slack订阅通知失败: {str(e)}")
            return False
    
    async def send_simple_message(
        self,
        message: str,
        channel: Optional[str] = None,
        emoji: str = ":information_source:"
    ) -> bool:
        """发送简单消息"""
        return await self.send_message(
            text=f"{emoji} {message}",
            channel=channel
        )
    
    async def test_connection(self) -> bool:
        """测试Slack连接"""
        try:
            test_message = f"🧪 GitHub Sentinel 连接测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            return await self.send_simple_message(test_message)
        except Exception as e:
            logger.error(f"Slack连接测试失败: {str(e)}")
            return False 