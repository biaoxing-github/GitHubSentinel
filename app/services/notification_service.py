"""
通知服务
根据订阅配置选择合适的通知类型并发送通知
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.logger import get_logger
from app.models.subscription import Subscription
from app.notifiers.email_notifier import EmailNotifier
from app.notifiers.slack_notifier import SlackNotifier
from app.notifiers.webhook_notifier import WebhookNotifier

logger = get_logger(__name__)


class NotificationService:
    """通知服务"""
    
    def __init__(self):
        self.email_notifier = EmailNotifier()
        self.slack_notifier = SlackNotifier()
        self.webhook_notifier = WebhookNotifier()
    
    def _parse_json_field(self, field_value: Optional[str]) -> List[str]:
        """解析JSON字段为列表"""
        if not field_value:
            return []
        
        try:
            parsed = json.loads(field_value)
            if isinstance(parsed, list):
                return [str(item) for item in parsed if item]
            elif isinstance(parsed, str):
                return [parsed] if parsed else []
            else:
                return []
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"无法解析JSON字段: {field_value}")
            return []
    
    async def send_subscription_notification(
        self,
        subscription: Subscription,
        activity_data: Dict[str, Any],
        notification_type: str = "activity"
    ) -> Dict[str, bool]:
        """
        根据订阅配置发送通知
        
        Args:
            subscription: 订阅对象
            activity_data: 活动数据
            notification_type: 通知类型 (activity, report, system)
        
        Returns:
            Dict[str, bool]: 各种通知方式的发送结果
        """
        results = {
            "email": False,
            "slack": False,
            "webhook": False
        }
        
        # 准备通知数据
        notification_data = {
            "subscription_id": subscription.id,
            "user_id": subscription.user_id,
            "repository": subscription.repository,
            "notification_type": notification_type,
            "timestamp": datetime.now().isoformat(),
            **activity_data
        }
        
        # 并发发送所有启用的通知
        tasks = []
        
        # 邮件通知
        if subscription.enable_email_notification:
            email_addresses = self._parse_json_field(subscription.notification_emails)
            if email_addresses:
                tasks.append(self._send_email_notification(email_addresses, notification_data))
        
        # Slack通知
        if subscription.enable_slack_notification:
            slack_webhooks = self._parse_json_field(subscription.notification_slack_webhooks)
            if slack_webhooks:
                tasks.append(self._send_slack_notification(slack_webhooks, notification_data))
        
        # Webhook通知
        if subscription.enable_webhook_notification:
            webhook_urls = self._parse_json_field(subscription.notification_custom_webhooks)
            if webhook_urls:
                tasks.append(self._send_webhook_notification(webhook_urls, notification_data))
        
        # 执行所有通知任务
        if tasks:
            task_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            task_index = 0
            if subscription.enable_email_notification and self._parse_json_field(subscription.notification_emails):
                results["email"] = task_results[task_index] if not isinstance(task_results[task_index], Exception) else False
                task_index += 1
            
            if subscription.enable_slack_notification and self._parse_json_field(subscription.notification_slack_webhooks):
                results["slack"] = task_results[task_index] if not isinstance(task_results[task_index], Exception) else False
                task_index += 1
            
            if subscription.enable_webhook_notification and self._parse_json_field(subscription.notification_custom_webhooks):
                results["webhook"] = task_results[task_index] if not isinstance(task_results[task_index], Exception) else False
                task_index += 1
        
        # 记录通知结果
        success_count = sum(1 for success in results.values() if success)
        total_count = sum(1 for enabled in [
            subscription.enable_email_notification and bool(self._parse_json_field(subscription.notification_emails)),
            subscription.enable_slack_notification and bool(self._parse_json_field(subscription.notification_slack_webhooks)),
            subscription.enable_webhook_notification and bool(self._parse_json_field(subscription.notification_custom_webhooks))
        ] if enabled)
        
        if total_count > 0:
            logger.info(f"订阅 {subscription.id} 通知发送完成: {success_count}/{total_count} 成功")
        else:
            logger.warning(f"订阅 {subscription.id} 没有启用任何通知方式")
        
        return results
    
    async def _send_email_notification(
        self,
        email_addresses: List[str],
        notification_data: Dict[str, Any]
    ) -> bool:
        """发送邮件通知"""
        try:
            subject = self._generate_email_subject(notification_data)
            html_content = self._generate_email_content(notification_data)
            
            return await self.email_notifier.send_email(
                to_emails=email_addresses,
                subject=subject,
                html_content=html_content
            )
        except Exception as e:
            logger.error(f"邮件通知发送失败: {str(e)}")
            return False
    
    async def _send_slack_notification(
        self,
        slack_webhooks: List[str],
        notification_data: Dict[str, Any]
    ) -> bool:
        """发送Slack通知"""
        try:
            # 临时保存原始配置
            original_webhook = self.slack_notifier.notification_config.slack_webhook_url
            original_enabled = self.slack_notifier.notification_config.slack_enabled
            
            success_count = 0
            for webhook_url in slack_webhooks:
                # 临时设置webhook URL
                self.slack_notifier.notification_config.slack_webhook_url = webhook_url
                self.slack_notifier.notification_config.slack_enabled = True
                
                # 发送通知
                success = await self.slack_notifier.send_subscription_notification(notification_data)
                if success:
                    success_count += 1
            
            # 恢复原始配置
            self.slack_notifier.notification_config.slack_webhook_url = original_webhook
            self.slack_notifier.notification_config.slack_enabled = original_enabled
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Slack通知发送失败: {str(e)}")
            return False
    
    async def _send_webhook_notification(
        self,
        webhook_urls: List[str],
        notification_data: Dict[str, Any]
    ) -> bool:
        """发送Webhook通知"""
        try:
            success_count = 0
            for webhook_url in webhook_urls:
                success = await self.webhook_notifier.send_webhook(
                    url=webhook_url,
                    data=notification_data
                )
                if success:
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Webhook通知发送失败: {str(e)}")
            return False
    
    def _generate_email_subject(self, notification_data: Dict[str, Any]) -> str:
        """生成邮件主题"""
        repo = notification_data.get("repository", "Unknown")
        notification_type = notification_data.get("notification_type", "activity")
        
        if notification_type == "activity":
            activity_type = notification_data.get("activity_type", "activity")
            return f"[GitHub Sentinel] {repo} - 新{activity_type}活动"
        elif notification_type == "report":
            return f"[GitHub Sentinel] {repo} - 定期报告"
        else:
            return f"[GitHub Sentinel] {repo} - 系统通知"
    
    def _generate_email_content(self, notification_data: Dict[str, Any]) -> str:
        """生成邮件内容"""
        repo = notification_data.get("repository", "Unknown")
        activity_type = notification_data.get("activity_type", "activity")
        activity_title = notification_data.get("activity_title", "")
        activity_author = notification_data.get("activity_author", "")
        activity_url = notification_data.get("activity_url", "")
        activity_description = notification_data.get("activity_description", "")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>GitHub Sentinel 通知</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #007bff;
                }}
                .activity-info {{
                    background: white;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 15px 0;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    background: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #666;
                    font-size: 12px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🔔 GitHub Sentinel 通知</h2>
                <p>仓库: {repo}</p>
            </div>
            
            <div class="content">
                <h3>📝 {activity_type.upper()} 活动</h3>
                
                <div class="activity-info">
                    <h4>{activity_title}</h4>
                    <p><strong>作者:</strong> {activity_author}</p>
                    <p><strong>时间:</strong> {notification_data.get('timestamp', '')}</p>
                    {f'<p><strong>描述:</strong> {activity_description}</p>' if activity_description else ''}
                </div>
                
                {f'<a href="{activity_url}" class="button">查看详情</a>' if activity_url else ''}
            </div>
            
            <div class="footer">
                <p>此邮件由 GitHub Sentinel 自动发送</p>
                <p>如需取消订阅，请登录系统进行设置</p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    async def send_batch_notifications(
        self,
        subscriptions: List[Subscription],
        activity_data: Dict[str, Any],
        notification_type: str = "activity"
    ) -> Dict[int, Dict[str, bool]]:
        """
        批量发送通知
        
        Args:
            subscriptions: 订阅列表
            activity_data: 活动数据
            notification_type: 通知类型
        
        Returns:
            Dict[int, Dict[str, bool]]: 每个订阅的通知发送结果
        """
        results = {}
        
        # 并发发送所有订阅的通知
        tasks = []
        subscription_ids = []
        
        for subscription in subscriptions:
            tasks.append(self.send_subscription_notification(subscription, activity_data, notification_type))
            subscription_ids.append(subscription.id)
        
        if tasks:
            task_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(task_results):
                subscription_id = subscription_ids[i]
                if isinstance(result, Exception):
                    logger.error(f"订阅 {subscription_id} 通知发送异常: {str(result)}")
                    results[subscription_id] = {"email": False, "slack": False, "webhook": False}
                else:
                    results[subscription_id] = result
        
        return results
    
    async def test_subscription_notifications(self, subscription: Subscription) -> Dict[str, bool]:
        """
        测试订阅的通知配置
        
        Args:
            subscription: 订阅对象
        
        Returns:
            Dict[str, bool]: 各种通知方式的测试结果
        """
        test_data = {
            "activity_type": "test",
            "activity_title": "通知配置测试",
            "activity_author": "GitHub Sentinel",
            "activity_description": "这是一条测试通知，用于验证您的通知配置是否正常工作。",
            "activity_url": "https://github.com"
        }
        
        return await self.send_subscription_notification(subscription, test_data, "test")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False
    ) -> bool:
        """
        发送单个邮件
        
        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            body: 邮件内容
            is_html: 是否为HTML格式
        
        Returns:
            bool: 发送是否成功
        """
        try:
            logger.info(f"📧 发送邮件到: {to_email}")
            
            if is_html:
                return await self.email_notifier.send_email(
                    to_emails=[to_email],
                    subject=subject,
                    html_content=body
                )
            else:
                return await self.email_notifier.send_email(
                    to_emails=[to_email],
                    subject=subject,
                    text_content=body
                )
                
        except Exception as e:
            logger.error(f"💥 发送邮件失败: {e}", exc_info=True)
            return False 