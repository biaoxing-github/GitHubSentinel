#!/bin/bash

# GitHubSentinel v0.2 Release Script
# 自动提交代码并创建版本标签

echo "🚀 开始发布 GitHubSentinel v0.2..."

# 检查Git状态
echo "📋 检查Git状态..."
git status

# 添加所有修改的文件
echo "📦 添加修改的文件..."
git add .

# 提交代码
echo "💾 提交代码..."
git commit -m "feat: Release v0.2 - Enhanced Dashboard and Email Notifications

🎯 主要功能更新:
- 前端时间显示统一使用北京时间
- Dashboard Recent Activity 增加时间筛选功能
- 完善 Performance Metrics 接口实现
- 邮件通知模板样式与HTML报告保持一致
- 修复 Activities.vue 图标导入错误
- 优化数据库查询逻辑，使用GitHub实际活动时间

🔧 技术改进:
- 创建时间工具函数统一时间处理
- 数据库模型时间字段使用北京时间默认值
- API接口支持时间周期参数筛选
- 前端组件支持响应式时间筛选

🐛 Bug修复:
- 修复ExternalLink图标导入错误
- 修复repository_activities数据查询问题
- 优化时间筛选逻辑，基于GitHub实际活动时间

📊 数据展示优化:
- Dashboard统计面板数据更准确
- Recent Activity支持多维度筛选
- Activities页面支持分页和搜索
- 邮件通知样式现代化升级"

# 创建版本标签
echo "🏷️  创建版本标签 v0.2..."
git tag -a v0.2.0 -m "GitHubSentinel v0.2 - Enhanced Dashboard and Email Notifications

主要更新:
✅ 前端时间显示北京时间
✅ Dashboard时间筛选功能
✅ Performance Metrics接口
✅ 邮件模板样式优化
✅ 数据查询逻辑修复
✅ 前端组件功能增强

技术栈: Vue3 + FastAPI + PostgreSQL + Element Plus"

# 推送到远程仓库
echo "🌐 推送到远程仓库..."
git push origin master
git push origin v0.2.0

echo "✅ GitHubSentinel v0.2 发布完成!"
echo "📝 请查看 RELEASE_NOTES.md 了解详细更新内容"
echo "📖 请查看 README.md 了解最新功能介绍" 