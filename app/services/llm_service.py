"""
LLM 智能分析服务 (v0.3.0)
基于 LangChain 框架，提供高级 AI 分析和对话查询功能
与原有 ai_service 并存，提供更强大的智能分析能力
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional

from langchain.chains import LLMChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.callbacks import AsyncCallbackHandler
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class StreamingCallbackHandler(AsyncCallbackHandler):
    """流式输出回调处理器"""
    
    def __init__(self, callback_func=None):
        self.callback_func = callback_func
        self.tokens = []
    
    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        """处理新的token"""
        if self.callback_func:
            await self.callback_func(token)
        self.tokens.append(token)


class LLMService:
    """基于 LangChain 的高级 LLM 服务"""
    
    def __init__(self):
        self.settings = get_settings()
        self.ai_config = self.settings.ai
        
        # 初始化 LangChain 组件
        self.llm = None
        self.conversation_chains = {}  # 用户会话链
        self.search_tool = DuckDuckGoSearchRun()
        
        self._initialize_llm()
        
    def _initialize_llm(self):
        """初始化 LLM 模型"""
        try:
            if self.ai_config.provider == "openai" and self.ai_config.openai_api_key:
                self.llm = ChatOpenAI(
                    model=self.ai_config.openai_model,
                    api_key=self.ai_config.openai_api_key,
                    temperature=self.ai_config.temperature,
                    max_tokens=self.ai_config.max_tokens,
                    streaming=True
                )
                logger.info(f"✅ LangChain LLM 初始化成功 - 模型: {self.ai_config.openai_model}")
            else:
                logger.warning("⚠️ 未配置 OpenAI API Key，LLM 服务将不可用")
        except Exception as e:
            logger.error(f"💥 LLM 初始化失败: {e}")
    
    def get_conversation_chain(self, user_id: str):
        """获取或创建用户的对话链"""
        if user_id not in self.conversation_chains:
            from langchain.chains import LLMChain
            from langchain.memory import ConversationBufferWindowMemory
            from langchain.prompts import PromptTemplate
            
            # 使用简化的提示模板
            template = """你是 GitHubSentinel 的 AI 助手，专门帮助用户分析 GitHub 仓库活动和代码开发趋势。

你的职责包括：
1. 分析仓库活动数据，提供深度洞察
2. 回答用户关于代码、提交、Issue、PR 等的问题
3. 提供开发建议和最佳实践
4. 解释技术概念和代码模式

请用中文回答，保持专业、友好的语调。如果需要更多上下文信息，请主动询问。

当前对话历史:
{history}

用户问题: {input}
AI回答:"""

            prompt = PromptTemplate(
                input_variables=["history", "input"],
                template=template
            )
            
            memory = ConversationBufferWindowMemory(
                k=10,  # 保留最近10轮对话
                memory_key="history",
                input_key="input"
            )
            
            self.conversation_chains[user_id] = LLMChain(
                llm=self.llm,
                prompt=prompt,
                memory=memory,
                verbose=True
            )
            
        return self.conversation_chains[user_id]
    
    async def chat_with_context(
        self, 
        user_id: str, 
        message: str, 
        context_data: Optional[Dict[str, Any]] = None,
        stream_callback: Optional[callable] = None
    ) -> str:
        """与用户进行对话，可以包含上下文数据"""
        try:
            if not self.llm:
                return "抱歉，AI 服务当前不可用。请检查配置。"
            
            # 构建包含上下文的消息
            enhanced_message = message
            if context_data:
                context_str = self._format_context_data(context_data)
                enhanced_message = f"""
上下文数据：
{context_str}

用户问题：{message}
"""
            
            # 获取对话链
            chain = self.get_conversation_chain(user_id)
            
            # 设置流式回调
            callbacks = []
            if stream_callback:
                callbacks.append(StreamingCallbackHandler(stream_callback))
            
            # 执行对话
            response = await chain.arun(
                input=enhanced_message,
                callbacks=callbacks
            )
            
            logger.info(f"✅ LLM 对话完成 - 用户: {user_id}")
            return response
            
        except Exception as e:
            logger.error(f"💥 LLM 对话失败: {e}")
            return f"抱歉，处理您的问题时出现错误：{str(e)}"
    
    async def analyze_repository_intelligence(
        self, 
        repo_data: Dict[str, Any],
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """智能分析仓库数据"""
        try:
            if not self.llm:
                return {"error": "AI 服务不可用"}
            
            # 根据分析类型选择不同的提示词
            if analysis_type == "comprehensive":
                analysis_result = await self._comprehensive_analysis(repo_data)
            elif analysis_type == "security":
                analysis_result = await self._security_analysis(repo_data)
            elif analysis_type == "performance":
                analysis_result = await self._performance_analysis(repo_data)
            elif analysis_type == "quality":
                analysis_result = await self._quality_analysis(repo_data)
            else:
                analysis_result = await self._comprehensive_analysis(repo_data)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"💥 智能分析失败: {e}")
            return {"error": f"分析失败: {str(e)}"}
    
    async def _comprehensive_analysis(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """综合分析"""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""你是一个资深的代码架构师和项目分析专家。请对提供的 GitHub 仓库数据进行深度分析。

分析维度包括：
1. 代码质量和架构设计
2. 开发活跃度和团队协作
3. 技术栈选择和依赖管理
4. 安全性和最佳实践
5. 项目发展趋势和建议

请提供结构化的分析结果，包含具体的数据支撑和可行的改进建议。"""),
            HumanMessage(content="请分析以下仓库数据：\n{repo_data}")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"repo_data": json.dumps(repo_data, ensure_ascii=False, indent=2)})
        
        return {
            "type": "comprehensive",
            "analysis": response.content,
            "timestamp": datetime.now().isoformat(),
            "confidence": "high"
        }
    
    async def _security_analysis(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """安全性分析"""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""你是一个网络安全专家，专注于代码安全审计和风险评估。

请从以下角度分析仓库的安全性：
1. 依赖包安全风险
2. 代码中的潜在安全漏洞
3. 敏感信息泄露风险
4. 访问控制和权限管理
5. 安全最佳实践遵循情况

提供具体的安全建议和修复方案。"""),
            HumanMessage(content="请进行安全分析：\n{repo_data}")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"repo_data": json.dumps(repo_data, ensure_ascii=False, indent=2)})
        
        return {
            "type": "security",
            "analysis": response.content,
            "timestamp": datetime.now().isoformat(),
            "confidence": "high"
        }
    
    async def _performance_analysis(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """性能分析"""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""你是一个性能优化专家，专注于代码性能分析和系统优化。

请分析仓库的性能相关方面：
1. 代码执行效率
2. 资源使用优化
3. 数据库查询性能
4. 缓存策略
5. 并发和异步处理

提供具体的性能优化建议。"""),
            HumanMessage(content="请进行性能分析：\n{repo_data}")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"repo_data": json.dumps(repo_data, ensure_ascii=False, indent=2)})
        
        return {
            "type": "performance",
            "analysis": response.content,
            "timestamp": datetime.now().isoformat(),
            "confidence": "medium"
        }
    
    async def _quality_analysis(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """代码质量分析"""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""你是一个代码质量专家，专注于代码规范和最佳实践。

请分析代码质量相关指标：
1. 代码规范和一致性
2. 测试覆盖率和质量
3. 文档完整性
4. 代码可维护性
5. 重构和技术债务

提供具体的质量改进建议。"""),
            HumanMessage(content="请进行质量分析：\n{repo_data}")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"repo_data": json.dumps(repo_data, ensure_ascii=False, indent=2)})
        
        return {
            "type": "quality",
            "analysis": response.content,
            "timestamp": datetime.now().isoformat(),
            "confidence": "high"
        }
    
    async def generate_smart_summary(
        self, 
        activities: List[Dict[str, Any]], 
        timeframe: str = "weekly"
    ) -> Dict[str, Any]:
        """生成智能摘要"""
        try:
            if not self.llm:
                return {"error": "AI 服务不可用"}
            
            # 数据预处理
            processed_data = self._preprocess_activities(activities, timeframe)
            
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=f"""你是一个专业的数据分析师，擅长从开发活动数据中提取关键洞察。

请为 {timeframe} 的开发活动生成智能摘要，包括：
1. 关键统计数据
2. 重要趋势和模式
3. 异常活动识别
4. 团队表现亮点
5. 需要关注的问题

用简洁专业的语言总结，突出最重要的信息。"""),
                HumanMessage(content="活动数据：\n{activities}")
            ])
            
            chain = prompt | self.llm
            response = await chain.ainvoke({
                "activities": json.dumps(processed_data, ensure_ascii=False, indent=2)
            })
            
            return {
                "summary": response.content,
                "timeframe": timeframe,
                "activity_count": len(activities),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"💥 智能摘要生成失败: {e}")
            return {"error": f"摘要生成失败: {str(e)}"}
    
    async def search_and_analyze(
        self, 
        query: str, 
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """搜索并分析相关信息"""
        try:
            # 使用搜索工具获取外部信息
            search_results = self.search_tool.run(query)
            
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""你是一个专业的技术研究员，能够结合搜索结果和上下文数据提供深入分析。

请基于搜索结果和提供的上下文数据，回答用户问题并提供相关分析。"""),
                HumanMessage(content="""
搜索结果：
{search_results}

上下文数据：
{context_data}

用户问题：{query}
""")
            ])
            
            chain = prompt | self.llm
            response = await chain.ainvoke({
                "search_results": search_results,
                "context_data": json.dumps(context_data or {}, ensure_ascii=False, indent=2),
                "query": query
            })
            
            return {
                "analysis": response.content,
                "search_results": search_results,
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"💥 搜索分析失败: {e}")
            return {"error": f"搜索分析失败: {str(e)}"}
    
    def _format_context_data(self, context_data: Dict[str, Any]) -> str:
        """格式化上下文数据"""
        formatted = []
        
        if "repository" in context_data:
            repo = context_data["repository"]
            formatted.append(f"仓库: {repo.get('name', 'Unknown')}")
            formatted.append(f"描述: {repo.get('description', 'N/A')}")
            formatted.append(f"主要语言: {repo.get('language', 'N/A')}")
            formatted.append(f"Stars: {repo.get('stargazers_count', 0)}")
        
        if "recent_activities" in context_data:
            activities = context_data["recent_activities"]
            formatted.append(f"\n最近活动 ({len(activities)} 项):")
            for i, activity in enumerate(activities[:5]):
                formatted.append(f"  {i+1}. {activity.get('type', 'unknown')}: {activity.get('title', 'N/A')[:50]}...")
        
        if "statistics" in context_data:
            stats = context_data["statistics"]
            formatted.append(f"\n统计数据:")
            for key, value in stats.items():
                formatted.append(f"  {key}: {value}")
        
        return "\n".join(formatted)
    
    def _preprocess_activities(
        self, 
        activities: List[Dict[str, Any]], 
        timeframe: str
    ) -> Dict[str, Any]:
        """预处理活动数据"""
        # 按类型分组
        by_type = {}
        by_author = {}
        by_date = {}
        
        for activity in activities:
            # 按类型分组
            activity_type = activity.get("activity_type", "unknown")
            if activity_type not in by_type:
                by_type[activity_type] = []
            by_type[activity_type].append(activity)
            
            # 按作者分组
            author = activity.get("author_login", "unknown")
            if author not in by_author:
                by_author[author] = []
            by_author[author].append(activity)
            
            # 按日期分组
            created_at = activity.get("github_created_at", "")
            if created_at:
                date_key = created_at[:10]  # YYYY-MM-DD
                if date_key not in by_date:
                    by_date[date_key] = []
                by_date[date_key].append(activity)
        
        return {
            "total_activities": len(activities),
            "timeframe": timeframe,
            "by_type": {k: len(v) for k, v in by_type.items()},
            "by_author": {k: len(v) for k, v in by_author.items()},
            "by_date": {k: len(v) for k, v in by_date.items()},
            "top_contributors": sorted(by_author.items(), key=lambda x: len(x[1]), reverse=True)[:5],
            "most_active_dates": sorted(by_date.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        }
    
    async def clear_conversation(self, user_id: str) -> bool:
        """清除用户对话历史"""
        try:
            if user_id in self.conversation_chains:
                del self.conversation_chains[user_id]
                logger.info(f"✅ 清除用户对话历史 - 用户: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"💥 清除对话历史失败: {e}")
            return False
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "llm_available": self.llm is not None,
            "model": self.ai_config.openai_model if self.llm else None,
            "active_conversations": len(self.conversation_chains),
            "last_updated": datetime.now().isoformat()
        }