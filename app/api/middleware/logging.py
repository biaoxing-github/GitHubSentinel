"""
API 日志记录中间件
"""

import time
import json
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """API请求日志记录中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取请求信息
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # 记录请求体（仅对POST/PUT请求）
        request_body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    request_body = body.decode("utf-8")
                    # 重新构建request以便后续处理
                    async def receive():
                        return {"type": "http.request", "body": body}
                    request._receive = receive
            except Exception as e:
                logger.warning(f"读取请求体失败: {e}")
        
        # 记录请求日志
        logger.info(
            f"🌐 API请求开始 - {method} {url} | "
            f"客户端: {client_ip} | "
            f"User-Agent: {user_agent[:100]}..."
        )
        
        if request_body:
            # 隐藏敏感信息
            safe_body = mask_sensitive_data(request_body)
            logger.debug(f"📤 请求体: {safe_body}")
        
        try:
            # 执行请求
            response = await call_next(request)
            
            # 计算响应时间
            process_time = time.time() - start_time
            
            # 记录响应日志
            status_emoji = get_status_emoji(response.status_code)
            logger.info(
                f"{status_emoji} API请求完成 - {method} {url} | "
                f"状态码: {response.status_code} | "
                f"耗时: {process_time:.3f}s"
            )
            
            # 记录响应体（仅在debug模式下）
            if logger.level("DEBUG").no <= logger._core.min_level:
                response_body = None
                if hasattr(response, 'body'):
                    try:
                        response_body = response.body.decode('utf-8')
                        if len(response_body) > 1000:
                            response_body = response_body[:1000] + "..."
                        logger.debug(f"📥 响应体: {response_body}")
                    except Exception:
                        pass
            
            # 添加响应头
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 计算错误响应时间
            process_time = time.time() - start_time
            
            # 记录错误日志
            logger.error(
                f"❌ API请求失败 - {method} {url} | "
                f"错误: {str(e)} | "
                f"耗时: {process_time:.3f}s",
                exc_info=True
            )
            
            # 返回标准错误响应
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "内部服务器错误",
                    "error": str(e),
                    "path": url,
                    "method": method,
                    "timestamp": time.time()
                },
                headers={"X-Process-Time": str(process_time)}
            )


def mask_sensitive_data(data: str) -> str:
    """隐藏敏感数据"""
    try:
        json_data = json.loads(data)
        sensitive_keys = ['password', 'token', 'api_key', 'secret', 'key']
        
        def mask_dict(obj):
            if isinstance(obj, dict):
                return {
                    k: "***" if any(key in k.lower() for key in sensitive_keys) else mask_dict(v)
                    for k, v in obj.items()
                }
            elif isinstance(obj, list):
                return [mask_dict(item) for item in obj]
            else:
                return obj
        
        masked_data = mask_dict(json_data)
        return json.dumps(masked_data, ensure_ascii=False, indent=2)
    except:
        return data[:200] + "..." if len(data) > 200 else data


def get_status_emoji(status_code: int) -> str:
    """根据状态码返回对应的emoji"""
    if 200 <= status_code < 300:
        return "✅"
    elif 300 <= status_code < 400:
        return "🔄"
    elif 400 <= status_code < 500:
        return "❌"
    elif 500 <= status_code < 600:
        return "💥"
    else:
        return "❓" 