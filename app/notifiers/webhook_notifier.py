"""
Webhook通知器
支持自定义HTTP请求和多个端点
"""

import json
import hashlib
import hmac
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx

from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class WebhookNotifier:
    """Webhook通知器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.notification_config = self.settings.notification
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """生成Webhook签名"""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def send_webhook(
        self,
        url: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None
    ) -> bool:
        """发送Webhook请求"""
        try:
            # 准备请求数据
            payload = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            
            # 准备请求头
            request_headers = {
                "Content-Type": "application/json",
                "User-Agent": "GitHub-Sentinel/1.0",
                "X-GitHub-Sentinel-Event": data.get("event_type", "notification"),
                "X-GitHub-Sentinel-Delivery": str(hash(payload + str(datetime.now().timestamp())))
            }
            
            # 添加自定义头部
            if headers:
                request_headers.update(headers)
            
            # 添加签名
            if secret:
                signature = self._generate_signature(payload, secret)
                request_headers["X-GitHub-Sentinel-Signature"] = f"sha256={signature}"
            
            # 发送请求
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    content=payload,
                    headers=request_headers,
                    timeout=30.0
                )
                
                if 200 <= response.status_code < 300:
                    logger.info(f"Webhook发送成功: {url} - {response.status_code}")
                    return True
                else:
                    logger.error(f"Webhook发送失败: {url} - {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Webhook发送异常: {url} - {str(e)}")
            return False
    
    async def send_to_all_webhooks(
        self,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> List[bool]:
        """发送到所有配置的Webhook端点"""
        if not self.notification_config.webhook_enabled:
            logger.warning("Webhook通知未启用")
            return []
        
        if not self.notification_config.webhook_urls:
            logger.warning("没有配置Webhook URL")
            return []
        
        results = []
        for url in self.notification_config.webhook_urls:
            result = await self.send_webhook(url, data, headers)
            results.append(result)
        
        return results
    
    def _create_report_payload(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建报告Webhook载荷"""
        return {
            "timestamp": datetime.now().isoformat(),
            "event_type": "report_generated",
            "source": "github_sentinel",
            "version": "1.0.0",
            "data": {
                "report_id": report_data.get("id"),
                "report_type": report_data.get("type", "daily"),
                "date": report_data.get("date", datetime.now().strftime('%Y-%m-%d')),
                "user_id": report_data.get("user_id"),
                "repositories": [
                    {
                        "name": repo.get("name"),
                        "activities_count": len(repo.get("activities", [])),
                        "summary": repo.get("summary", ""),
                        "activities": [
                            {
                                "type": activity.get("type"),
                                "title": activity.get("title"),
                                "author": activity.get("author"),
                                "created_at": activity.get("created_at"),
                                "url": activity.get("url")
                            }
                            for activity in repo.get("activities", [])[:10]  # 限制活动数量
                        ]
                    }
                    for repo in report_data.get("repositories", [])
                ],
                "statistics": {
                    "total_repositories": len(report_data.get("repositories", [])),
                    "total_activities": sum(len(repo.get("activities", [])) for repo in report_data.get("repositories", [])),
                    "activity_types": self._count_activity_types(report_data.get("repositories", []))
                },
                "period": {
                    "start": report_data.get("period_start"),
                    "end": report_data.get("period_end")
                }
            }
        }
    
    def _create_subscription_payload(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建订阅Webhook载荷"""
        return {
            "timestamp": datetime.now().isoformat(),
            "event_type": "subscription_activity",
            "source": "github_sentinel",
            "version": "1.0.0",
            "data": {
                "subscription_id": subscription_data.get("subscription_id"),
                "user_id": subscription_data.get("user_id"),
                "repository": subscription_data.get("repository"),
                "activity": {
                    "type": subscription_data.get("activity_type"),
                    "title": subscription_data.get("activity_title"),
                    "description": subscription_data.get("activity_description"),
                    "author": subscription_data.get("activity_author"),
                    "created_at": subscription_data.get("activity_time"),
                    "url": subscription_data.get("activity_url")
                },
                "notification_time": datetime.now().isoformat()
            }
        }
    
    def _count_activity_types(self, repositories: List[Dict[str, Any]]) -> Dict[str, int]:
        """统计活动类型数量"""
        type_counts = {}
        for repo in repositories:
            for activity in repo.get("activities", []):
                activity_type = activity.get("type", "unknown")
                type_counts[activity_type] = type_counts.get(activity_type, 0) + 1
        return type_counts
    
    async def send_report_notification(
        self,
        report_data: Dict[str, Any],
        custom_headers: Optional[Dict[str, str]] = None
    ) -> List[bool]:
        """发送报告通知Webhook"""
        try:
            payload = self._create_report_payload(report_data)
            
            headers = {
                "X-Report-Type": report_data.get("type", "daily"),
                "X-Report-Date": report_data.get("date", datetime.now().strftime('%Y-%m-%d'))
            }
            
            if custom_headers:
                headers.update(custom_headers)
            
            results = await self.send_to_all_webhooks(payload, headers)
            
            success_count = sum(1 for r in results if r)
            total_count = len(results)
            
            if success_count > 0:
                logger.info(f"报告Webhook通知: {success_count}/{total_count} 成功")
            else:
                logger.error("所有报告Webhook通知都失败了")
            
            return results
            
        except Exception as e:
            logger.error(f"发送报告Webhook通知失败: {str(e)}")
            return []
    
    async def send_subscription_notification(
        self,
        subscription_data: Dict[str, Any],
        custom_headers: Optional[Dict[str, str]] = None
    ) -> List[bool]:
        """发送订阅通知Webhook"""
        try:
            payload = self._create_subscription_payload(subscription_data)
            
            headers = {
                "X-Repository": subscription_data.get("repository", ""),
                "X-Activity-Type": subscription_data.get("activity_type", "")
            }
            
            if custom_headers:
                headers.update(custom_headers)
            
            results = await self.send_to_all_webhooks(payload, headers)
            
            success_count = sum(1 for r in results if r)
            total_count = len(results)
            
            if success_count > 0:
                logger.info(f"订阅Webhook通知: {success_count}/{total_count} 成功")
            else:
                logger.error("所有订阅Webhook通知都失败了")
            
            return results
            
        except Exception as e:
            logger.error(f"发送订阅Webhook通知失败: {str(e)}")
            return []
    
    async def send_system_notification(
        self,
        event_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> List[bool]:
        """发送系统通知Webhook"""
        try:
            payload = {
                "timestamp": datetime.now().isoformat(),
                "event_type": f"system_{event_type}",
                "source": "github_sentinel",
                "version": "1.0.0",
                "data": {
                    "message": message,
                    "details": data or {}
                }
            }
            
            headers = {
                "X-Event-Type": event_type,
                "X-System-Message": "true"
            }
            
            return await self.send_to_all_webhooks(payload, headers)
            
        except Exception as e:
            logger.error(f"发送系统Webhook通知失败: {str(e)}")
            return []
    
    async def test_connection(self) -> bool:
        """测试Webhook连接"""
        try:
            test_payload = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "connection_test",
                "source": "github_sentinel",
                "version": "1.0.0",
                "data": {
                    "message": "GitHub Sentinel Webhook连接测试",
                    "test_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
            results = await self.send_to_all_webhooks(test_payload)
            success_count = sum(1 for r in results if r)
            
            if success_count > 0:
                logger.info(f"Webhook连接测试: {success_count}/{len(results)} 成功")
                return True
            else:
                logger.error("所有Webhook连接测试都失败了")
                return False
                
        except Exception as e:
            logger.error(f"Webhook连接测试失败: {str(e)}")
            return False 