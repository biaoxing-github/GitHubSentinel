#!/bin/bash

# GitHubSentinel v0.3.0 Release Script
# 自动提交代码并创建版本标签

echo "🚀 开始发布 GitHubSentinel v0.3.0..."

# 检查Git状态
echo "📋 检查Git状态..."
git status

# 添加所有修改的文件
echo "📦 添加修改的文件..."
git add .

# 提交代码
echo "💾 提交代码..."
git commit -m "feat: Release v0.3.0 - AI智能分析与实时通信平台

🎯 重大功能更新:
🤖 AI智能分析助手 - 基于LangChain的智能仓库分析系统
🔔 WebSocket实时通信 - 支持实时通知和多频道广播
📱 PWA渐进式Web应用 - 完整的离线支持和应用安装
🖥️ 系统监控面板 - 实时系统性能监控和运维工具

🔐 安全与认证:
- JWT令牌认证机制
- HTTP Bearer认证方案
- 开发环境友好的认证容错
- 完善的用户管理系统

🎨 前端界面升级:
- AI聊天页面 - 现代化聊天界面，支持Markdown渲染
- 系统监控页面 - 专业系统状态监控界面
- WebSocket监控 - 实时连接状态和日志监控
- 通知规则配置 - 可视化通知规则管理
- 用户配置页面 - 个人设置和偏好配置

🔧 技术架构升级:
- LLM服务 - 完整AI语言模型服务封装
- WebSocket服务 - 高性能实时通信服务
- PWA服务 - 渐进式Web应用支持服务
- 报告进度服务 - 实时进度追踪服务

📦 新增核心依赖:
- langchain>=0.1.0 - AI语言模型框架
- openai>=1.3.0 - OpenAI API客户端
- websockets>=11.0.3 - WebSocket支持
- psutil>=5.9.0 - 系统信息获取
- echarts^5.4.0 - 数据可视化图表

🚀 性能与体验优化:
- 异步处理全面升级
- 多层缓存策略
- 响应式设计完善
- PWA离线功能
- 实时进度反馈

🐛 Bug修复:
- WebSocket连接稳定性
- AI对话上下文保持
- 系统监控数据精度
- 移动端响应式布局

📊 新增API接口:
- POST /llm/chat - AI对话接口
- POST /llm/analyze - 仓库智能分析
- WebSocket /websocket/connect - WebSocket连接
- GET /pwa/manifest.json - PWA应用清单
- GET /system-monitor/metrics - 系统监控指标"

# 创建版本标签
echo "🏷️  创建版本标签 v0.3.0..."
git tag -a v0.3.0 -m "GitHubSentinel v0.3.0 - AI智能分析与实时通信平台

🎯 重大更新:
✅ AI智能分析助手 - LangChain驱动的智能仓库分析
✅ WebSocket实时通信 - 多频道实时通知系统
✅ PWA渐进式Web应用 - 离线支持和应用安装
✅ 系统监控面板 - 全面的性能监控和运维工具
✅ 增强认证系统 - JWT令牌和多层认证
✅ 前端界面全面升级 - 5个新页面和响应式设计

🔧 技术栈升级:
- Vue3 + Element Plus + ECharts
- FastAPI + LangChain + WebSocket
- PWA + Service Worker + 智能缓存
- PostgreSQL + Redis + JWT认证

🚀 核心特性:
- 🤖 智能对话和仓库分析
- 🔔 实时通知和进度推送
- 📱 跨平台PWA应用
- 🖥️ 专业系统监控
- 🔐 企业级安全认证"

# 推送到远程仓库
echo "🌐 推送到远程仓库..."
git push origin master
git push origin v0.3.0

echo "✅ GitHubSentinel v0.3.0 发布完成!"
echo "📝 请查看 RELEASE_NOTES.md 了解详细更新内容"
echo "📖 请查看 README.md 了解最新功能介绍"
echo "🔗 GitHub Release: https://github.com/your-username/GitHubSentinel/releases/tag/v0.3.0"

# 显示版本信息
echo ""
echo "🎉 版本发布信息:"
echo "   版本号: v0.3.0"
echo "   发布日期: $(date '+%Y-%m-%d %H:%M:%S')"
echo "   主要特性: AI智能分析、WebSocket实时通信、PWA应用、系统监控"
echo "   技术栈: Vue3 + FastAPI + LangChain + WebSocket + PWA"
echo ""
echo "📋 后续步骤:"
echo "   1. 更新生产环境配置"
echo "   2. 安装新增依赖: pip install -r requirements.txt"
echo "   3. 配置OpenAI API密钥（AI功能需要）"
echo "   4. 重启服务以启用新功能"
echo "   5. 测试PWA安装和WebSocket连接" 