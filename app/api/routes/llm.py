"""
LLM 智能分析 API 路由 (v0.3.0)
基于 LangChain 的高级 AI 分析和对话查询接口
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth_simple import get_current_user
from app.core.logger import get_logger
from app.models.subscription import User
from app.services.llm_service import LLMService
from app.services.websocket_service import websocket_service
from app.collectors.github_collector import GitHubCollector

logger = get_logger(__name__)
router = APIRouter(prefix="/llm", tags=["AI智能分析"])

# 全局LLM服务实例
llm_service = LLMService()


class ChatRequest(BaseModel):
    """对话请求模型"""
    message: str = Field(..., description="用户消息")
    context_data: Optional[Dict[str, Any]] = Field(None, description="上下文数据")
    stream: bool = Field(False, description="是否流式输出")


class ChatResponse(BaseModel):
    """对话响应模型"""
    response: str = Field(..., description="AI回复")
    conversation_id: str = Field(..., description="对话ID")
    timestamp: str = Field(..., description="时间戳")


class AnalysisRequest(BaseModel):
    """分析请求模型"""
    repository: str = Field(..., description="仓库名称，格式：owner/repo")
    analysis_type: str = Field(default="comprehensive", description="分析类型")
    timeframe: str = Field(default="30d", description="时间范围")


class AnalysisResponse(BaseModel):
    """分析响应模型"""
    analysis: Dict[str, Any] = Field(..., description="分析结果")
    repository: str = Field(..., description="仓库名称")
    analysis_type: str = Field(..., description="分析类型")
    generated_at: str = Field(..., description="生成时间")


class SmartSummaryRequest(BaseModel):
    """智能摘要请求模型"""
    repository: str = Field(..., description="仓库名称")
    timeframe: str = Field(default="weekly", description="时间范围")
    days: int = Field(default=7, description="天数")


class SearchRequest(BaseModel):
    """搜索分析请求模型"""
    query: str = Field(..., description="搜索查询")
    context_data: Optional[Dict[str, Any]] = Field(None, description="上下文数据")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """与AI进行对话"""
    try:
        user_id = str(current_user.id)
        
        # 普通对话模式
        if not request.stream:
            response = await llm_service.chat_with_context(
                user_id=user_id,
                message=request.message,
                context_data=request.context_data
            )
            
            # 发送对话通知
            background_tasks.add_task(
                websocket_service.send_ai_insight_notification,
                {
                    "type": "chat_response",
                    "message": request.message,
                    "response": response,
                    "conversation_id": user_id
                },
                current_user.id
            )
            
            return ChatResponse(
                response=response,
                conversation_id=user_id,
                timestamp=datetime.now().isoformat()
            )
        
        else:
            # 流式对话模式
            return StreamingResponse(
                stream_chat_response(user_id, request.message, request.context_data),
                media_type="text/plain"
            )
            
    except Exception as e:
        import traceback
        logger.error(f"💥 AI对话失败: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI对话失败: {str(e)}"
        )


async def stream_chat_response(user_id: str, message: str, context_data: Optional[Dict[str, Any]]):
    """流式对话响应生成器"""
    try:
        response_tokens = []
        
        async def token_callback(token: str):
            response_tokens.append(token)
            yield f"data: {token}\n\n"
        
        # 执行流式对话
        await llm_service.chat_with_context(
            user_id=user_id,
            message=message,
            context_data=context_data,
            stream_callback=token_callback
        )
        
        # 发送结束标记
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        logger.error(f"💥 流式对话失败: {e}")
        yield f"data: 错误: {str(e)}\n\n"


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_repository(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """智能分析仓库"""
    try:
        # 解析仓库名称
        if "/" not in request.repository:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="仓库名称格式错误，应为 owner/repo"
            )
        
        owner, repo = request.repository.split("/", 1)
        
        # 收集仓库数据
        github_collector = GitHubCollector()
        repo_data = await github_collector.collect_repository_data(owner, repo)
        
        # 执行智能分析
        analysis_result = await llm_service.analyze_repository_intelligence(
            repo_data=repo_data,
            analysis_type=request.analysis_type
        )
        
        if "error" in analysis_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=analysis_result["error"]
            )
        
        # 发送分析结果通知
        background_tasks.add_task(
            websocket_service.send_ai_insight_notification,
            {
                "type": "repository_analysis",
                "repository": request.repository,
                "analysis_type": request.analysis_type,
                "analysis": analysis_result
            },
            current_user.id
        )
        
        return AnalysisResponse(
            analysis=analysis_result,
            repository=request.repository,
            analysis_type=request.analysis_type,
            generated_at=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 仓库分析失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"仓库分析失败: {str(e)}"
        )


@router.post("/smart-summary")
async def generate_smart_summary(
    request: SmartSummaryRequest,
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """生成智能摘要"""
    try:
        # 解析仓库名称
        if "/" not in request.repository:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="仓库名称格式错误，应为 owner/repo"
            )
        
        owner, repo = request.repository.split("/", 1)
        
        # 收集活动数据
        github_collector = GitHubCollector()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.days)
        
        activities = await github_collector.collect_activities(
            owner, repo, start_date, end_date
        )
        
        # 生成智能摘要
        summary_result = await llm_service.generate_smart_summary(
            activities=activities,
            timeframe=request.timeframe
        )
        
        if "error" in summary_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=summary_result["error"]
            )
        
        # 发送摘要通知
        background_tasks.add_task(
            websocket_service.send_ai_insight_notification,
            {
                "type": "smart_summary",
                "repository": request.repository,
                "timeframe": request.timeframe,
                "summary": summary_result
            },
            current_user.id
        )
        
        return summary_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 智能摘要生成失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"智能摘要生成失败: {str(e)}"
        )


@router.post("/search")
async def search_and_analyze(
    request: SearchRequest,
    current_user: User = Depends(get_current_user)
):
    """搜索并分析"""
    try:
        result = await llm_service.search_and_analyze(
            query=request.query,
            context_data=request.context_data
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 搜索分析失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索分析失败: {str(e)}"
        )


@router.delete("/conversation")
async def clear_conversation(
    current_user: User = Depends(get_current_user)
):
    """清除对话历史"""
    try:
        user_id = str(current_user.id)
        success = await llm_service.clear_conversation(user_id)
        
        if success:
            return {"message": "对话历史已清除", "user_id": user_id}
        else:
            return {"message": "未找到对话历史", "user_id": user_id}
            
    except Exception as e:
        logger.error(f"💥 清除对话历史失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清除对话历史失败: {str(e)}"
        )


@router.get("/status")
async def get_llm_status(
    current_user: User = Depends(get_current_user)
):
    """获取LLM服务状态"""
    try:
        status_info = llm_service.get_service_status()
        return status_info
        
    except Exception as e:
        logger.error(f"💥 获取LLM状态失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取LLM状态失败: {str(e)}"
        )


@router.post("/batch-analyze")
async def batch_analyze_repositories(
    repositories: List[str],
    analysis_type: str = "comprehensive",
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """批量分析多个仓库"""
    try:
        if len(repositories) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="批量分析最多支持10个仓库"
            )
        
        results = []
        github_collector = GitHubCollector()
        
        for repo in repositories:
            try:
                if "/" not in repo:
                    results.append({
                        "repository": repo,
                        "error": "仓库名称格式错误"
                    })
                    continue
                
                owner, repo_name = repo.split("/", 1)
                
                # 收集仓库数据
                repo_data = await github_collector.collect_repository_data(owner, repo_name)
                
                # 执行分析
                analysis_result = await llm_service.analyze_repository_intelligence(
                    repo_data=repo_data,
                    analysis_type=analysis_type
                )
                
                results.append({
                    "repository": repo,
                    "analysis": analysis_result,
                    "status": "success"
                })
                
            except Exception as e:
                results.append({
                    "repository": repo,
                    "error": str(e),
                    "status": "failed"
                })
        
        # 发送批量分析完成通知
        background_tasks.add_task(
            websocket_service.send_ai_insight_notification,
            {
                "type": "batch_analysis_complete",
                "repositories": repositories,
                "analysis_type": analysis_type,
                "results_count": len(results),
                "success_count": len([r for r in results if r.get("status") == "success"])
            },
            current_user.id
        )
        
        return {
            "results": results,
            "total": len(repositories),
            "success": len([r for r in results if r.get("status") == "success"]),
            "failed": len([r for r in results if r.get("status") == "failed"]),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 批量分析失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量分析失败: {str(e)}"
        ) 