"""
WebSocket 实时通知 API 路由 (v0.3.0)
提供WebSocket连接管理和通知规则配置接口
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth_simple import get_current_user, get_user_from_token
from app.core.logger import get_logger
from app.models.subscription import User
from app.services.websocket_service import websocket_service
from app.services.report_progress_service import progress_service, simulate_report_generation, simulate_ai_analysis

logger = get_logger(__name__)
router = APIRouter(prefix="/websocket", tags=["实时通知"])


class NotificationRuleRequest(BaseModel):
    """通知规则请求模型"""
    rule_type: str = Field(..., description="规则类型: activity, threshold, schedule, ai_insight")
    conditions: Dict[str, Any] = Field(..., description="触发条件")
    actions: Dict[str, Any] = Field(..., description="执行动作")


class NotificationRuleResponse(BaseModel):
    """通知规则响应模型"""
    rule_id: str = Field(..., description="规则ID")
    message: str = Field(..., description="响应消息")


class BroadcastRequest(BaseModel):
    """广播请求模型"""
    message: str = Field(..., description="广播消息")
    channel: Optional[str] = Field(None, description="频道名称")
    target_users: Optional[List[int]] = Field(None, description="目标用户ID列表")


@router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    """WebSocket连接端点"""
    try:
        # 验证用户token
        user = await get_user_from_token(token, db)
        if not user:
            logger.warning(f"WebSocket连接被拒绝: 无效token")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        logger.info(f"用户 {user.username} 建立WebSocket连接")
        
        # 处理WebSocket连接
        await websocket_service.handle_websocket_connection(websocket, user.id)
        
    except Exception as e:
        logger.error(f"💥 WebSocket连接错误: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)


@router.get("/notification-rules")
async def get_notification_rules(
    current_user: User = Depends(get_current_user)
):
    """获取用户的通知规则列表"""
    try:
        rules = await websocket_service.get_user_notification_rules(current_user.id)
        return {"rules": rules, "count": len(rules)}
        
    except Exception as e:
        logger.error(f"💥 获取通知规则失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取通知规则失败: {str(e)}"
        )


@router.post("/notification-rules", response_model=NotificationRuleResponse)
async def create_notification_rule(
    request: NotificationRuleRequest,
    current_user: User = Depends(get_current_user)
):
    """创建通知规则"""
    try:
        rule_id = await websocket_service.add_notification_rule(
            user_id=current_user.id,
            rule_type=request.rule_type,
            conditions=request.conditions,
            actions=request.actions
        )
        
        return NotificationRuleResponse(
            rule_id=rule_id,
            message="通知规则创建成功"
        )
        
    except Exception as e:
        logger.error(f"💥 创建通知规则失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建通知规则失败: {str(e)}"
        )


@router.delete("/notification-rules/{rule_id}")
async def delete_notification_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user)
):
    """删除通知规则"""
    try:
        success = await websocket_service.remove_notification_rule(
            user_id=current_user.id,
            rule_id=rule_id
        )
        
        if success:
            return {"message": "通知规则删除成功", "rule_id": rule_id}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="通知规则不存在"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 删除通知规则失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除通知规则失败: {str(e)}"
        )


@router.post("/broadcast")
async def broadcast_message(
    request: BroadcastRequest,
    current_user: User = Depends(get_current_user)
):
    """广播消息（管理员功能）"""
    try:
        # 这里可以添加管理员权限检查
        # if not current_user.is_admin:
        #     raise HTTPException(status_code=403, detail="需要管理员权限")
        
        if request.target_users:
            # 发送给指定用户
            for user_id in request.target_users:
                await websocket_service.connection_manager.send_personal_message(
                    {
                        "type": "broadcast",
                        "message": request.message,
                        "from_user": current_user.username,
                        "timestamp": datetime.now().isoformat()
                    },
                    user_id
                )
            return {"message": f"消息已发送给 {len(request.target_users)} 个用户"}
        
        elif request.channel:
            # 频道广播
            await websocket_service.connection_manager.broadcast_to_channel(
                {
                    "type": "channel_broadcast",
                    "message": request.message,
                    "channel": request.channel,
                    "from_user": current_user.username,
                    "timestamp": datetime.now().isoformat()
                },
                request.channel
            )
            return {"message": f"消息已广播到频道: {request.channel}"}
        
        else:
            # 系统公告
            await websocket_service.send_system_announcement(
                message=request.message,
                announcement_type="admin"
            )
            return {"message": "系统公告已发送"}
            
    except Exception as e:
        logger.error(f"💥 广播消息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"广播消息失败: {str(e)}"
        )


@router.get("/stats")
async def get_websocket_stats(
    current_user: User = Depends(get_current_user)
):
    """获取WebSocket服务统计信息"""
    try:
        stats = websocket_service.get_service_stats()
        return stats
        
    except Exception as e:
        logger.error(f"💥 获取WebSocket统计失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )


@router.post("/test-notification")
async def send_test_notification(
    current_user: User = Depends(get_current_user)
):
    """发送测试通知"""
    try:
        await websocket_service.send_ai_insight_notification(
            {
                "type": "test",
                "message": "这是一条测试通知",
                "timestamp": datetime.now().isoformat()
            },
            current_user.id
        )
        
        return {"message": "测试通知已发送"}
        
    except Exception as e:
        logger.error(f"💥 发送测试通知失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送测试通知失败: {str(e)}"
        )


@router.get("/channels")
async def get_user_channels(
    current_user: User = Depends(get_current_user)
):
    """获取用户订阅的频道"""
    try:
        user_channels = websocket_service.connection_manager.user_channels.get(
            current_user.id, set()
        )
        
        return {
            "user_id": current_user.id,
            "channels": list(user_channels),
            "channel_count": len(user_channels)
        }
        
    except Exception as e:
        logger.error(f"💥 获取用户频道失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户频道失败: {str(e)}"
        )


@router.post("/subscribe/{channel}")
async def subscribe_channel(
    channel: str,
    current_user: User = Depends(get_current_user)
):
    """订阅频道"""
    try:
        await websocket_service.connection_manager.subscribe_channel(
            current_user.id, channel
        )
        
        return {"message": f"已订阅频道: {channel}", "channel": channel}
        
    except Exception as e:
        logger.error(f"💥 订阅频道失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"订阅频道失败: {str(e)}"
        )


@router.delete("/subscribe/{channel}")
async def unsubscribe_channel(
    channel: str,
    current_user: User = Depends(get_current_user)
):
    """取消订阅频道"""
    try:
        await websocket_service.connection_manager.unsubscribe_channel(
            current_user.id, channel
        )
        
        return {"message": f"已取消订阅频道: {channel}", "channel": channel}
        
    except Exception as e:
        logger.error(f"💥 取消订阅频道失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消订阅频道失败: {str(e)}"
        )


# =================== 进度推送相关API ===================

class ReportGenerationRequest(BaseModel):
    """报告生成请求模型"""
    repo_name: str = Field(..., description="仓库名称")
    report_type: str = Field(default="monthly", description="报告类型: daily/weekly/monthly/yearly")


class AnalysisRequest(BaseModel):
    """AI分析请求模型"""
    repo_name: str = Field(..., description="仓库名称")
    analysis_type: str = Field(default="comprehensive", description="分析类型: comprehensive/security/performance/quality")


@router.post("/generate-report")
async def start_report_generation(
    request: ReportGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """启动报告生成任务（带进度推送）"""
    try:
        import uuid
        import asyncio
        
        # 生成任务ID
        task_id = f"report_{uuid.uuid4().hex[:8]}"
        
        # 注册进度回调
        async def progress_callback(progress_data: Dict[str, Any]):
            await websocket_service.connection_manager.send_personal_message(
                progress_data, current_user.id
            )
        
        progress_service.register_progress_callback(task_id, progress_callback)
        
        # 异步启动报告生成任务
        asyncio.create_task(
            simulate_report_generation(task_id, request.report_type, request.repo_name)
        )
        
        return {
            "task_id": task_id,
            "message": "报告生成任务已启动",
            "repo_name": request.repo_name,
            "report_type": request.report_type
        }
        
    except Exception as e:
        logger.error(f"💥 启动报告生成失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动报告生成失败: {str(e)}"
        )


@router.post("/start-analysis")
async def start_ai_analysis(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """启动AI分析任务（带进度推送）"""
    try:
        import uuid
        import asyncio
        
        # 生成任务ID
        task_id = f"analysis_{uuid.uuid4().hex[:8]}"
        
        # 注册进度回调
        async def progress_callback(progress_data: Dict[str, Any]):
            await websocket_service.connection_manager.send_personal_message(
                progress_data, current_user.id
            )
        
        progress_service.register_progress_callback(task_id, progress_callback)
        
        # 异步启动AI分析任务
        asyncio.create_task(
            simulate_ai_analysis(task_id, request.analysis_type, request.repo_name)
        )
        
        return {
            "task_id": task_id,
            "message": "AI分析任务已启动",
            "repo_name": request.repo_name,
            "analysis_type": request.analysis_type
        }
        
    except Exception as e:
        logger.error(f"💥 启动AI分析失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动AI分析失败: {str(e)}"
        )


@router.get("/task-status/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """获取任务状态"""
    try:
        task_status = progress_service.get_task_status(task_id)
        if task_status:
            return task_status
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 获取任务状态失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务状态失败: {str(e)}"
        )


@router.delete("/cancel-task/{task_id}")
async def cancel_task(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """取消正在运行的任务"""
    try:
        success = progress_service.cancel_task(task_id)
        if success:
            # 发送取消通知给前端
            await websocket_service.connection_manager.send_personal_message(
                {
                    "type": "task_cancelled",
                    "task_id": task_id,
                    "message": "任务已被取消",
                    "timestamp": datetime.now().isoformat()
                },
                current_user.id
            )
            
            return {"message": "任务已取消", "task_id": task_id}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在或无法取消"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 取消任务失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消任务失败: {str(e)}"
        ) 