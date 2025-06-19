"""
WebSocket 实时通知服务 (v0.3.0)
提供实时通知推送、智能通知规则和多平台集成功能
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import uuid

import socketio
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.logger import get_logger
from app.core.database import get_db_session
from app.models.subscription import User

logger = get_logger(__name__)


class NotificationRule:
    """智能通知规则"""
    
    def __init__(
        self,
        rule_id: str,
        user_id: int,
        rule_type: str,
        conditions: Dict[str, Any],
        actions: Dict[str, Any],
        enabled: bool = True
    ):
        self.rule_id = rule_id
        self.user_id = user_id
        self.rule_type = rule_type  # activity, threshold, schedule, ai_insight
        self.conditions = conditions
        self.actions = actions
        self.enabled = enabled
        self.created_at = datetime.now()


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 活跃连接 {user_id: {connection_id: websocket}}
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}
        # 用户订阅的频道 {user_id: set(channels)}
        self.user_channels: Dict[int, Set[str]] = {}
        # 通知规则 {user_id: [NotificationRule]}
        self.notification_rules: Dict[int, List[NotificationRule]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: int, connection_id: str):
        """建立WebSocket连接"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        
        self.active_connections[user_id][connection_id] = websocket
        
        # 初始化用户频道订阅
        if user_id not in self.user_channels:
            self.user_channels[user_id] = set()
            # 默认订阅用户自己的频道
            self.user_channels[user_id].add(f"user_{user_id}")
        
        logger.info(f"✅ WebSocket连接建立 - 用户: {user_id}, 连接: {connection_id}")
        
        # 发送连接成功消息
        await self.send_personal_message({
            "type": "connection_established",
            "message": "实时通知连接已建立",
            "user_id": user_id,
            "connection_id": connection_id,
            "timestamp": datetime.now().isoformat()
        }, user_id, connection_id)
    
    async def disconnect(self, user_id: int, connection_id: str):
        """断开WebSocket连接"""
        if user_id in self.active_connections:
            if connection_id in self.active_connections[user_id]:
                del self.active_connections[user_id][connection_id]
                
                # 如果用户没有其他连接，清理用户数据
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                    
        logger.info(f"❌ WebSocket连接断开 - 用户: {user_id}, 连接: {connection_id}")
    
    async def send_personal_message(
        self, 
        message: Dict[str, Any], 
        user_id: int, 
        connection_id: Optional[str] = None
    ):
        """发送个人消息"""
        if user_id not in self.active_connections:
            return
        
        connections = self.active_connections[user_id]
        
        # 如果指定了连接ID，只发送给该连接
        if connection_id and connection_id in connections:
            try:
                await connections[connection_id].send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"💥 发送个人消息失败 - 用户: {user_id}, 连接: {connection_id}, 错误: {e}")
                # 清理无效连接
                del connections[connection_id]
        else:
            # 发送给用户的所有连接
            invalid_connections = []
            for conn_id, websocket in connections.items():
                try:
                    await websocket.send_text(json.dumps(message, ensure_ascii=False))
                except Exception as e:
                    logger.error(f"💥 发送个人消息失败 - 用户: {user_id}, 连接: {conn_id}, 错误: {e}")
                    invalid_connections.append(conn_id)
            
            # 清理无效连接
            for conn_id in invalid_connections:
                del connections[conn_id]
    
    async def broadcast_to_channel(self, message: Dict[str, Any], channel: str):
        """向频道广播消息"""
        target_users = []
        
        # 找到订阅该频道的所有用户
        for user_id, channels in self.user_channels.items():
            if channel in channels:
                target_users.append(user_id)
        
        # 发送消息
        for user_id in target_users:
            await self.send_personal_message(message, user_id)
        
        logger.info(f"📢 频道广播完成 - 频道: {channel}, 用户数: {len(target_users)}")
    
    async def subscribe_channel(self, user_id: int, channel: str):
        """订阅频道"""
        if user_id not in self.user_channels:
            self.user_channels[user_id] = set()
        
        self.user_channels[user_id].add(channel)
        logger.info(f"📺 用户订阅频道 - 用户: {user_id}, 频道: {channel}")
    
    async def unsubscribe_channel(self, user_id: int, channel: str):
        """取消订阅频道"""
        if user_id in self.user_channels:
            self.user_channels[user_id].discard(channel)
            logger.info(f"📺 用户取消订阅频道 - 用户: {user_id}, 频道: {channel}")
    
    def get_active_users(self) -> List[int]:
        """获取活跃用户列表"""
        return list(self.active_connections.keys())
    
    def get_connection_count(self) -> int:
        """获取总连接数"""
        total = 0
        for connections in self.active_connections.values():
            total += len(connections)
        return total


class WebSocketService:
    """WebSocket 实时通知服务"""
    
    def __init__(self):
        self.settings = get_settings()
        self.connection_manager = ConnectionManager()
        self.sio = socketio.AsyncServer(cors_allowed_origins="*")
        
    async def handle_websocket_connection(
        self, 
        websocket: WebSocket, 
        user_id: int
    ):
        """处理WebSocket连接"""
        connection_id = str(uuid.uuid4())
        
        try:
            await self.connection_manager.connect(websocket, user_id, connection_id)
            
            while True:
                # 接收客户端消息
                data = await websocket.receive_text()
                message = json.loads(data)
                
                await self._handle_client_message(message, user_id, connection_id)
                
        except WebSocketDisconnect:
            await self.connection_manager.disconnect(user_id, connection_id)
        except Exception as e:
            logger.error(f"💥 WebSocket处理错误: {e}")
            await self.connection_manager.disconnect(user_id, connection_id)
    
    async def _handle_client_message(
        self, 
        message: Dict[str, Any], 
        user_id: int, 
        connection_id: str
    ):
        """处理客户端消息"""
        message_type = message.get("type", "unknown")
        
        if message_type == "subscribe":
            # 订阅频道
            channel = message.get("channel")
            if channel:
                await self.connection_manager.subscribe_channel(user_id, channel)
                await self.connection_manager.send_personal_message({
                    "type": "subscription_success",
                    "channel": channel,
                    "message": f"已订阅频道: {channel}"
                }, user_id, connection_id)
        
        elif message_type == "unsubscribe":
            # 取消订阅频道
            channel = message.get("channel")
            if channel:
                await self.connection_manager.unsubscribe_channel(user_id, channel)
                await self.connection_manager.send_personal_message({
                    "type": "unsubscription_success",
                    "channel": channel,
                    "message": f"已取消订阅频道: {channel}"
                }, user_id, connection_id)
        
        elif message_type == "ping":
            # 心跳检测
            await self.connection_manager.send_personal_message({
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            }, user_id, connection_id)
        
        elif message_type == "get_status":
            # 获取连接状态
            await self.connection_manager.send_personal_message({
                "type": "status",
                "active_users": len(self.connection_manager.get_active_users()),
                "total_connections": self.connection_manager.get_connection_count(),
                "user_channels": list(self.connection_manager.user_channels.get(user_id, set()))
            }, user_id, connection_id)
        
        else:
            logger.warning(f"⚠️ 未知消息类型: {message_type}")
    
    async def send_activity_notification(
        self, 
        activity_data: Dict[str, Any], 
        target_users: Optional[List[int]] = None
    ):
        """发送活动通知"""
        notification = {
            "type": "activity_notification",
            "data": activity_data,
            "timestamp": datetime.now().isoformat(),
            "notification_id": str(uuid.uuid4())
        }
        
        if target_users:
            # 发送给指定用户
            for user_id in target_users:
                await self.connection_manager.send_personal_message(notification, user_id)
        else:
            # 广播到活动频道
            await self.connection_manager.broadcast_to_channel(
                notification, 
                f"repository_{activity_data.get('repository', 'unknown')}"
            )
        
        logger.info(f"📢 活动通知已发送: {activity_data.get('activity_type', 'unknown')}")
    
    async def send_ai_insight_notification(
        self, 
        insight_data: Dict[str, Any], 
        user_id: int
    ):
        """发送AI洞察通知"""
        notification = {
            "type": "ai_insight",
            "data": insight_data,
            "timestamp": datetime.now().isoformat(),
            "notification_id": str(uuid.uuid4())
        }
        
        await self.connection_manager.send_personal_message(notification, user_id)
        logger.info(f"🤖 AI洞察通知已发送 - 用户: {user_id}")
    
    async def send_report_notification(
        self, 
        report_data: Dict[str, Any], 
        user_id: int
    ):
        """发送报告通知"""
        notification = {
            "type": "report_notification",
            "data": report_data,
            "timestamp": datetime.now().isoformat(),
            "notification_id": str(uuid.uuid4())
        }
        
        await self.connection_manager.send_personal_message(notification, user_id)
        logger.info(f"📊 报告通知已发送 - 用户: {user_id}")
    
    async def send_system_announcement(
        self, 
        message: str, 
        announcement_type: str = "info"
    ):
        """发送系统公告"""
        notification = {
            "type": "system_announcement",
            "data": {
                "message": message,
                "announcement_type": announcement_type,
                "timestamp": datetime.now().isoformat()
            },
            "notification_id": str(uuid.uuid4())
        }
        
        # 广播给所有用户
        active_users = self.connection_manager.get_active_users()
        for user_id in active_users:
            await self.connection_manager.send_personal_message(notification, user_id)
        
        logger.info(f"📢 系统公告已发送: {message}")
    
    async def add_notification_rule(
        self, 
        user_id: int, 
        rule_type: str, 
        conditions: Dict[str, Any], 
        actions: Dict[str, Any]
    ) -> str:
        """添加通知规则"""
        rule_id = str(uuid.uuid4())
        rule = NotificationRule(
            rule_id=rule_id,
            user_id=user_id,
            rule_type=rule_type,
            conditions=conditions,
            actions=actions
        )
        
        if user_id not in self.connection_manager.notification_rules:
            self.connection_manager.notification_rules[user_id] = []
        
        self.connection_manager.notification_rules[user_id].append(rule)
        
        logger.info(f"📋 通知规则已添加 - 用户: {user_id}, 规则: {rule_id}")
        return rule_id
    
    async def remove_notification_rule(self, user_id: int, rule_id: str) -> bool:
        """删除通知规则"""
        if user_id in self.connection_manager.notification_rules:
            rules = self.connection_manager.notification_rules[user_id]
            for i, rule in enumerate(rules):
                if rule.rule_id == rule_id:
                    del rules[i]
                    logger.info(f"🗑️ 通知规则已删除 - 用户: {user_id}, 规则: {rule_id}")
                    return True
        return False
    
    async def check_notification_rules(
        self, 
        event_data: Dict[str, Any], 
        event_type: str
    ):
        """检查并触发通知规则"""
        for user_id, rules in self.connection_manager.notification_rules.items():
            for rule in rules:
                if not rule.enabled:
                    continue
                
                if await self._evaluate_rule_conditions(rule, event_data, event_type):
                    await self._execute_rule_actions(rule, event_data, user_id)
    
    async def _evaluate_rule_conditions(
        self, 
        rule: NotificationRule, 
        event_data: Dict[str, Any], 
        event_type: str
    ) -> bool:
        """评估规则条件"""
        conditions = rule.conditions
        
        # 检查事件类型
        if "event_types" in conditions:
            if event_type not in conditions["event_types"]:
                return False
        
        # 检查仓库过滤
        if "repositories" in conditions:
            repo_name = event_data.get("repository", "")
            if repo_name not in conditions["repositories"]:
                return False
        
        # 检查作者过滤
        if "authors" in conditions:
            author = event_data.get("author_login", "")
            if author not in conditions["authors"]:
                return False
        
        # 检查关键词过滤
        if "keywords" in conditions:
            title = event_data.get("title", "").lower()
            body = event_data.get("body", "").lower()
            for keyword in conditions["keywords"]:
                if keyword.lower() in title or keyword.lower() in body:
                    return True
            return False
        
        # 检查阈值条件
        if "thresholds" in conditions:
            thresholds = conditions["thresholds"]
            for metric, threshold in thresholds.items():
                if metric in event_data:
                    if event_data[metric] < threshold:
                        return False
        
        return True
    
    async def _execute_rule_actions(
        self, 
        rule: NotificationRule, 
        event_data: Dict[str, Any], 
        user_id: int
    ):
        """执行规则动作"""
        actions = rule.actions
        
        # 发送WebSocket通知
        if "websocket_notify" in actions and actions["websocket_notify"]:
            notification = {
                "type": "rule_triggered",
                "rule_id": rule.rule_id,
                "rule_type": rule.rule_type,
                "data": event_data,
                "timestamp": datetime.now().isoformat()
            }
            await self.connection_manager.send_personal_message(notification, user_id)
        
        # 发送邮件通知
        if "email_notify" in actions and actions["email_notify"]:
            # 这里可以集成邮件服务
            logger.info(f"📧 触发邮件通知 - 用户: {user_id}, 规则: {rule.rule_id}")
        
        # 发送第三方平台通知
        if "external_notify" in actions:
            platforms = actions["external_notify"]
            for platform in platforms:
                await self._send_external_notification(platform, event_data, user_id)
        
        logger.info(f"✅ 规则动作执行完成 - 用户: {user_id}, 规则: {rule.rule_id}")
    
    async def _send_external_notification(
        self, 
        platform: str, 
        event_data: Dict[str, Any], 
        user_id: int
    ):
        """发送第三方平台通知"""
        # 这里可以集成各种第三方平台的通知API
        # 如微信、钉钉、Telegram、Discord等
        
        logger.info(f"🔗 发送第三方通知 - 平台: {platform}, 用户: {user_id}")
        
        if platform == "wechat":
            # 微信通知集成
            pass
        elif platform == "dingtalk":
            # 钉钉通知集成
            pass
        elif platform == "telegram":
            # Telegram通知集成
            pass
        elif platform == "discord":
            # Discord通知集成
            pass
    
    def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        active_users = self.connection_manager.get_active_users()
        total_connections = self.connection_manager.get_connection_count()
        total_rules = sum(
            len(rules) for rules in self.connection_manager.notification_rules.values()
        )
        
        return {
            "active_users": len(active_users),
            "total_connections": total_connections,
            "total_notification_rules": total_rules,
            "channels": list(set().union(*self.connection_manager.user_channels.values())),
            "timestamp": datetime.now().isoformat()
        }


# 全局WebSocket服务实例
websocket_service = WebSocketService()