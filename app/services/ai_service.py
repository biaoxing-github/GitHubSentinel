"""
AI 分析服务
使用 OpenAI API 或本地 Ollama 进行智能分析和报告生成
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

import httpx
from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class AIService:
    """AI 分析服务"""
    
    def __init__(self):
        self.settings = get_settings()
        self.ai_config = self.settings.ai
        
    async def generate_repository_summary(self, analysis_data: Dict[str, Any]) -> str:
        """
        生成仓库活动摘要（新版本，支持报告生成）
        
        Args:
            analysis_data: 包含仓库信息、提交、issues、PR等的分析数据
        
        Returns:
            str: 生成的摘要
        """
        try:
            if self.ai_config.provider == "openai" and self.ai_config.openai_api_key:
                return await self._generate_openai_repository_summary(analysis_data)
            elif self.ai_config.provider == "ollama":
                return await self._generate_ollama_repository_summary(analysis_data)
            else:
                return self._generate_simple_repository_summary(analysis_data)
        except Exception as e:
            logger.error(f"💥 生成仓库摘要失败: {e}")
            return self._generate_simple_repository_summary(analysis_data)

    async def analyze_repository_trends(self, analysis_data: Dict[str, Any]) -> str:
        """
        分析仓库趋势
        
        Args:
            analysis_data: 包含仓库信息、提交、issues、PR等的分析数据
        
        Returns:
            str: 生成的趋势分析
        """
        try:
            if self.ai_config.provider == "openai" and self.ai_config.openai_api_key:
                return await self._generate_openai_trend_analysis(analysis_data)
            elif self.ai_config.provider == "ollama":
                return await self._generate_ollama_trend_analysis(analysis_data)
            else:
                return self._generate_simple_trend_analysis(analysis_data)
        except Exception as e:
            logger.error(f"💥 生成趋势分析失败: {e}")
            return self._generate_simple_trend_analysis(analysis_data)

    async def _generate_openai_repository_summary(self, analysis_data: Dict[str, Any]) -> str:
        """使用 OpenAI 生成仓库摘要"""
        try:
            prompt = self._create_repository_summary_prompt(analysis_data)
            
            request_data = {
                "model": self.ai_config.openai_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的GitHub仓库分析师，擅长总结仓库活动并提供有价值的见解。请用中文回答，语言简洁明了。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": self.ai_config.max_tokens,
                "temperature": self.ai_config.temperature
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.ai_config.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    summary = result["choices"][0]["message"]["content"].strip()
                    logger.info(f"✅ OpenAI 仓库摘要生成成功")
                    return summary
                else:
                    logger.error(f"💥 OpenAI API 请求失败: {response.status_code}")
                    return self._generate_simple_repository_summary(analysis_data)
                    
        except Exception as e:
            logger.error(f"💥 OpenAI 仓库摘要生成失败: {e}")
            return self._generate_simple_repository_summary(analysis_data)

    async def _generate_openai_trend_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """使用 OpenAI 生成趋势分析"""
        try:
            prompt = self._create_trend_analysis_prompt(analysis_data)
            
            request_data = {
                "model": self.ai_config.openai_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的软件开发趋势分析师，擅长分析代码仓库的发展趋势和提供改进建议。请用中文回答，提供具体可行的建议。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": self.ai_config.max_tokens,
                "temperature": self.ai_config.temperature
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.ai_config.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    analysis = result["choices"][0]["message"]["content"].strip()
                    logger.info(f"✅ OpenAI 趋势分析生成成功")
                    return analysis
                else:
                    logger.error(f"💥 OpenAI API 请求失败: {response.status_code}")
                    return self._generate_simple_trend_analysis(analysis_data)
                    
        except Exception as e:
            logger.error(f"💥 OpenAI 趋势分析生成失败: {e}")
            return self._generate_simple_trend_analysis(analysis_data)

    def _create_repository_summary_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """创建仓库摘要的提示词"""
        repo = analysis_data.get('repository', {})
        commits = analysis_data.get('commits', [])
        issues = analysis_data.get('issues', [])
        prs = analysis_data.get('pull_requests', [])
        releases = analysis_data.get('releases', [])
        period = analysis_data.get('period', {})
        
        # 构建详细的活动信息
        commits_info = ""
        if commits:
            commits_info = "\n最近的提交:\n"
            for i, commit in enumerate(commits[:5]):  # 显示前5个提交
                commits_info += f"- {commit.get('message', '无消息')[:80]}... (作者: {commit.get('author', {}).get('name', '未知')})\n"
        
        issues_info = ""
        if issues:
            issues_info = "\n最近的Issues:\n"
            for i, issue in enumerate(issues[:5]):  # 显示前5个issues
                state = issue.get('state', 'unknown')
                issues_info += f"- [{state.upper()}] {issue.get('title', '无标题')[:60]}... (作者: {issue.get('user', {}).get('login', '未知')})\n"
        
        prs_info = ""
        if prs:
            prs_info = "\n最近的Pull Requests:\n"
            for i, pr in enumerate(prs[:5]):  # 显示前5个PR
                state = pr.get('state', 'unknown')
                merged = pr.get('merged', False)
                status = "MERGED" if merged else state.upper()
                prs_info += f"- [{status}] {pr.get('title', '无标题')[:60]}... (作者: {pr.get('user', {}).get('login', '未知')})\n"
        
        releases_info = ""
        if releases:
            releases_info = "\n最近的发布:\n"
            for release in releases[:3]:  # 显示前3个发布
                releases_info += f"- {release.get('tag_name', '未知版本')}: {release.get('name', '无名称')}\n"
        
        prompt = f"""
请为以下GitHub仓库生成一个简洁的活动摘要：

仓库信息：
- 名称：{repo.get('name', 'Unknown')}
- 描述：{repo.get('description', '无描述')}
- 主要语言：{repo.get('language', '未知')}
- Stars：{repo.get('stargazers_count', 0)}
- Forks：{repo.get('forks_count', 0)}

报告期间：{period.get('start', '')} 到 {period.get('end', '')} ({period.get('type', 'daily')} 报告)

活动统计：
- 提交数：{len(commits)}
- Issues数：{len(issues)}
- Pull Requests数：{len(prs)}
- 发布数：{len(releases)}

{commits_info}
{issues_info}
{prs_info}
{releases_info}

请基于以上详细信息生成一个2-3句话的简洁摘要，突出本期间的主要活动、开发重点和项目进展。
"""
        return prompt

    def _create_trend_analysis_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """创建趋势分析的提示词"""
        repo = analysis_data.get('repository', {})
        commits = analysis_data.get('commits', [])
        issues = analysis_data.get('issues', [])
        prs = analysis_data.get('pull_requests', [])
        period = analysis_data.get('period', {})
        
        # 分析提交者
        committers = set()
        for commit in commits:
            author = commit.get('author')
            if author:
                # 如果 author 是字典，提取 login 或 name
                if isinstance(author, dict):
                    author_name = author.get('login') or author.get('name') or 'Unknown'
                else:
                    author_name = str(author)
                committers.add(author_name)
        
        # 分析Issue状态
        open_issues = sum(1 for issue in issues if issue.get('state') == 'open')
        closed_issues = len(issues) - open_issues
        
        # 分析PR状态
        open_prs = sum(1 for pr in prs if pr.get('state') == 'open')
        merged_prs = sum(1 for pr in prs if pr.get('merged'))
        
        # 构建详细的活动信息
        commits_detail = ""
        if commits:
            commits_detail = "\n提交详情:\n"
            for commit in commits[:3]:  # 显示前3个提交
                commits_detail += f"- {commit.get('message', '无消息')[:60]}... (作者: {commit.get('author', {}).get('name', '未知')})\n"
        
        issues_detail = ""
        if issues:
            issues_detail = "\nIssues详情:\n"
            for issue in issues[:3]:  # 显示前3个issues
                state = issue.get('state', 'unknown')
                issues_detail += f"- [{state.upper()}] {issue.get('title', '无标题')[:50]}... (作者: {issue.get('user', {}).get('login', '未知')})\n"
        
        prs_detail = ""
        if prs:
            prs_detail = "\nPull Requests详情:\n"
            for pr in prs[:3]:  # 显示前3个PR
                state = pr.get('state', 'unknown')
                merged = pr.get('merged', False)
                status = "MERGED" if merged else state.upper()
                prs_detail += f"- [{status}] {pr.get('title', '无标题')[:50]}... (作者: {pr.get('user', {}).get('login', '未知')})\n"
        
        prompt = f"""
请分析以下GitHub仓库的发展趋势并提供建议：

仓库：{repo.get('name', 'Unknown')}
分析期间：{period.get('type', 'daily')} 报告

开发活动统计：
- 活跃提交者：{len(committers)} 人
- 代码提交：{len(commits)} 次
- 新增Issues：{len(issues)} 个（开放：{open_issues}，已关闭：{closed_issues}）
- Pull Requests：{len(prs)} 个（开放：{open_prs}，已合并：{merged_prs}）

{commits_detail}
{issues_detail}
{prs_detail}

请基于以上详细信息从以下角度分析：
1. 开发活跃度趋势
2. 代码质量和维护情况
3. 社区参与度
4. 改进建议

请用2-3段话总结，每段不超过50字。
"""
        return prompt

    def _generate_simple_repository_summary(self, analysis_data: Dict[str, Any]) -> str:
        """生成简单的仓库摘要"""
        repo = analysis_data.get('repository', {})
        commits = analysis_data.get('commits', [])
        issues = analysis_data.get('issues', [])
        prs = analysis_data.get('pull_requests', [])
        releases = analysis_data.get('releases', [])
        
        summary_parts = []
        
        if commits:
            summary_parts.append(f"新增 {len(commits)} 个提交")
        if issues:
            summary_parts.append(f"{len(issues)} 个Issues活动")
        if prs:
            summary_parts.append(f"{len(prs)} 个Pull Request")
        if releases:
            summary_parts.append(f"{len(releases)} 个新发布")
        
        if summary_parts:
            summary = f"本期间 {repo.get('name', '该仓库')} 有" + "、".join(summary_parts) + "。"
        else:
            summary = f"本期间 {repo.get('name', '该仓库')} 没有新的活动。"
        
        return summary

    def _generate_simple_trend_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """生成简单的趋势分析"""
        commits = analysis_data.get('commits', [])
        issues = analysis_data.get('issues', [])
        prs = analysis_data.get('pull_requests', [])
        
        analysis_parts = []
        
        if len(commits) > 10:
            analysis_parts.append("代码提交频繁，开发活跃度较高")
        elif len(commits) > 0:
            analysis_parts.append("有适量的代码提交，开发稳定进行")
        else:
            analysis_parts.append("本期间代码提交较少")
        
        if len(issues) > 5:
            analysis_parts.append("Issues活动活跃，社区参与度良好")
        elif len(issues) > 0:
            analysis_parts.append("有一定的Issues活动")
        
        if len(prs) > 3:
            analysis_parts.append("Pull Request数量较多，代码协作良好")
        elif len(prs) > 0:
            analysis_parts.append("有代码贡献和协作")
        
        if analysis_parts:
            analysis = "。".join(analysis_parts) + "。建议继续保持当前的开发节奏，关注代码质量和文档完善。"
        else:
            analysis = "本期间活动较少，建议增加开发活跃度，鼓励社区参与。"
        
        return analysis
    
    def _prepare_analysis_data(
        self, 
        repository_data: Dict[str, Any], 
        activities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """准备用于AI分析的数据"""
        
        # 统计活动类型
        activity_stats = {}
        for activity in activities:
            activity_type = activity.get("activity_type", "unknown")
            activity_stats[activity_type] = activity_stats.get(activity_type, 0) + 1
        
        # 提取关键活动
        key_activities = []
        for activity in activities[:10]:  # 取前10个活动
            key_activities.append({
                "type": activity.get("activity_type"),
                "title": activity.get("title", "")[:100],
                "author": activity.get("author_login"),
                "created_at": activity.get("github_created_at")
            })
        
        return {
            "repository": {
                "name": repository_data.get("repository", "Unknown"),
                "description": repository_data.get("description", ""),
                "language": repository_data.get("language", ""),
                "stars": repository_data.get("stargazers_count", 0),
                "forks": repository_data.get("forks_count", 0)
            },
            "period_summary": {
                "total_activities": len(activities),
                "activity_types": activity_stats,
                "key_activities": key_activities
            }
        }
    
    async def _generate_openai_summary(self, analysis_data: Dict[str, Any]) -> str:
        """使用 OpenAI API 生成摘要"""
        if not self.ai_config.openai_api_key:
            logger.warning("OpenAI API Key 未配置，使用简单摘要")
            return self._generate_simple_summary(analysis_data)
        
        try:
            prompt = self._create_summary_prompt(analysis_data)
            logger.info("🤖 开始调用 OpenAI API 生成摘要")
            logger.info(f"📝 使用模型: {self.ai_config.openai_model}")
            logger.info(f"🎯 最大Token数: {self.ai_config.max_tokens}")
            logger.info(f"🌡️ 温度参数: {self.ai_config.temperature}")
            logger.debug(f"📋 输入提示词:\n{prompt}")
            
            request_data = {
                "model": self.ai_config.openai_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的GitHub仓库活动分析师，擅长总结开发活动并提供有价值的见解。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": self.ai_config.max_tokens,
                "temperature": self.ai_config.temperature
            }
            
            logger.debug(f"📤 发送请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.ai_config.openai_api_key[:10]}...{self.ai_config.openai_api_key[-4:]}",
                        "Content-Type": "application/json"
                    },
                    json=request_data,
                    timeout=30.0
                )
                
                logger.info(f"📡 OpenAI API 响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    logger.debug(f"📥 完整响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    
                    summary = result["choices"][0]["message"]["content"].strip()
                    usage = result.get("usage", {})
                    
                    logger.info(f"✅ OpenAI 摘要生成成功")
                    logger.info(f"📊 Token使用情况: 输入={usage.get('prompt_tokens', 0)}, 输出={usage.get('completion_tokens', 0)}, 总计={usage.get('total_tokens', 0)}")
                    logger.info(f"📝 生成的摘要长度: {len(summary)} 字符")
                    logger.debug(f"📄 生成的摘要内容:\n{summary}")
                    
                    return summary
                else:
                    error_text = response.text
                    logger.error(f"💥 OpenAI API 请求失败: {response.status_code}")
                    logger.error(f"📋 错误详情: {error_text}")
                    return self._generate_simple_summary(analysis_data)
                    
        except Exception as e:
            logger.error(f"💥 OpenAI 摘要生成失败: {str(e)}", exc_info=True)
            return self._generate_simple_summary(analysis_data)
    
    async def _generate_ollama_summary(self, analysis_data: Dict[str, Any]) -> str:
        """使用 Ollama 生成摘要"""
        try:
            prompt = self._create_summary_prompt(analysis_data)
            logger.info("🤖 开始调用 Ollama API 生成摘要")
            logger.info(f"🌐 Ollama URL: {self.ai_config.ollama_url}")
            logger.info(f"📝 使用模型: {self.ai_config.ollama_model}")
            logger.info(f"🎯 最大Token数: {self.ai_config.max_tokens}")
            logger.info(f"🌡️ 温度参数: {self.ai_config.temperature}")
            logger.debug(f"📋 输入提示词:\n{prompt}")
            
            request_data = {
                "model": self.ai_config.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.ai_config.temperature,
                    "num_predict": self.ai_config.max_tokens
                }
            }
            
            logger.debug(f"📤 发送请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ai_config.ollama_url}/api/generate",
                    json=request_data,
                    timeout=60.0
                )
                
                logger.info(f"📡 Ollama API 响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    logger.debug(f"📥 完整响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    
                    summary = result["response"].strip()
                    
                    logger.info(f"✅ Ollama 摘要生成成功")
                    logger.info(f"📝 生成的摘要长度: {len(summary)} 字符")
                    logger.debug(f"📄 生成的摘要内容:\n{summary}")
                    
                    return summary
                else:
                    error_text = response.text
                    logger.error(f"💥 Ollama API 请求失败: {response.status_code}")
                    logger.error(f"📋 错误详情: {error_text}")
                    return self._generate_simple_summary(analysis_data)
                    
        except Exception as e:
            logger.error(f"💥 Ollama 摘要生成失败: {str(e)}", exc_info=True)
            return self._generate_simple_summary(analysis_data)
    
    def _create_summary_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """创建摘要生成的提示词"""
        repo_info = analysis_data["repository"]
        period_summary = analysis_data["period_summary"]
        
        prompt = f"""
请为以下GitHub仓库活动生成一份简洁而有价值的中文摘要：

仓库信息：
- 名称：{repo_info["name"]}
- 描述：{repo_info["description"]}
- 主要语言：{repo_info["language"]}
- Stars：{repo_info["stars"]}
- Forks：{repo_info["forks"]}

活动统计：
- 总活动数：{period_summary["total_activities"]}
- 活动类型分布：{json.dumps(period_summary["activity_types"], ensure_ascii=False)}

主要活动：
"""
        
        for activity in period_summary["key_activities"]:
            prompt += f"- {activity['type']}: {activity['title']} (by {activity['author']})\n"
        
        prompt += """
请生成一份200-300字的摘要，包括：
1. 本期间的主要开发活动概述
2. 值得关注的重要变化或趋势
3. 对项目发展的简要评价

要求：
- 使用中文
- 语言简洁专业
- 突出重点信息
- 避免过于技术性的细节
"""
        
        return prompt
    
    def _generate_simple_summary(self, analysis_data: Dict[str, Any]) -> str:
        """生成简单的统计摘要（不使用AI）"""
        repo_info = analysis_data["repository"]
        period_summary = analysis_data["period_summary"]
        
        summary_parts = []
        
        # 基本统计
        total_activities = period_summary["total_activities"]
        summary_parts.append(f"本期间 {repo_info['name']} 仓库共有 {total_activities} 项活动。")
        
        # 活动类型统计
        activity_types = period_summary["activity_types"]
        if activity_types:
            type_descriptions = {
                "commit": "代码提交",
                "issue": "问题讨论",
                "pull_request": "代码合并请求",
                "release": "版本发布"
            }
            
            type_summary = []
            for activity_type, count in activity_types.items():
                desc = type_descriptions.get(activity_type, activity_type)
                type_summary.append(f"{desc} {count} 项")
            
            summary_parts.append(f"其中包括：{', '.join(type_summary)}。")
        
        # 主要活动
        key_activities = period_summary["key_activities"]
        if key_activities:
            summary_parts.append("主要活动包括：")
            for activity in key_activities[:3]:  # 只显示前3个
                summary_parts.append(f"• {activity['title']} (by {activity['author']})")
        
        # 项目信息
        if repo_info.get("language"):
            summary_parts.append(f"该项目主要使用 {repo_info['language']} 语言开发。")
        
        return "\n".join(summary_parts)
    
    async def generate_trend_analysis(
        self, 
        historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        生成趋势分析
        
        Args:
            historical_data: 历史数据列表
        
        Returns:
            Dict[str, Any]: 趋势分析结果
        """
        if len(historical_data) < 2:
            return {
                "trend": "insufficient_data",
                "description": "数据不足，无法进行趋势分析",
                "recommendations": []
            }
        
        # 计算活动趋势
        activity_counts = [data.get("total_activities", 0) for data in historical_data]
        
        # 简单的趋势计算
        recent_avg = sum(activity_counts[-3:]) / min(3, len(activity_counts))
        earlier_avg = sum(activity_counts[:-3]) / max(1, len(activity_counts) - 3)
        
        if recent_avg > earlier_avg * 1.2:
            trend = "increasing"
            description = "项目活动呈上升趋势，开发较为活跃"
        elif recent_avg < earlier_avg * 0.8:
            trend = "decreasing"
            description = "项目活动有所下降，可能需要关注"
        else:
            trend = "stable"
            description = "项目活动保持稳定"
        
        # 生成建议
        recommendations = self._generate_recommendations(trend, historical_data)
        
        return {
            "trend": trend,
            "description": description,
            "recent_average": recent_avg,
            "earlier_average": earlier_avg,
            "recommendations": recommendations
        }
    
    def _generate_recommendations(
        self, 
        trend: str, 
        historical_data: List[Dict[str, Any]]
    ) -> List[str]:
        """根据趋势生成建议"""
        recommendations = []
        
        if trend == "increasing":
            recommendations.extend([
                "项目发展势头良好，建议继续保持",
                "可以考虑增加代码审查和质量控制",
                "关注新贡献者的参与情况"
            ])
        elif trend == "decreasing":
            recommendations.extend([
                "建议分析活动下降的原因",
                "可以考虑增加社区互动和宣传",
                "检查是否有技术债务或阻碍因素"
            ])
        else:
            recommendations.extend([
                "项目保持稳定发展",
                "可以考虑设定新的发展目标",
                "持续关注代码质量和文档完善"
            ])
        
        return recommendations
    
    async def generate_activity_insights(
        self, 
        activities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        生成活动洞察
        
        Args:
            activities: 活动列表
        
        Returns:
            Dict[str, Any]: 活动洞察结果
        """
        if not activities:
            return {
                "insights": [],
                "top_contributors": [],
                "activity_patterns": {}
            }
        
        # 分析贡献者
        contributors = {}
        for activity in activities:
            author = activity.get("author_login", "unknown")
            contributors[author] = contributors.get(author, 0) + 1
        
        top_contributors = sorted(
            contributors.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        # 分析活动模式
        activity_patterns = {}
        for activity in activities:
            activity_type = activity.get("activity_type", "unknown")
            activity_patterns[activity_type] = activity_patterns.get(activity_type, 0) + 1
        
        # 生成洞察
        insights = []
        
        if top_contributors:
            top_contributor = top_contributors[0]
            insights.append(f"最活跃的贡献者是 {top_contributor[0]}，共有 {top_contributor[1]} 项活动")
        
        if len(contributors) > 1:
            insights.append(f"本期间共有 {len(contributors)} 位贡献者参与")
        
        most_common_activity = max(activity_patterns.items(), key=lambda x: x[1])
        insights.append(f"最常见的活动类型是 {most_common_activity[0]}，占 {most_common_activity[1]} 项")
        
        return {
            "insights": insights,
            "top_contributors": top_contributors,
            "activity_patterns": activity_patterns,
            "total_contributors": len(contributors)
        } 