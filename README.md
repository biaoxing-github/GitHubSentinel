# GitHub Sentinel

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.0+-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-blue.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.1.0-orange.svg)](RELEASE_NOTES.md)

## 项目简介

GitHub Sentinel 是一款开源的 GitHub 仓库监控和报告系统，专为开发者和项目管理人员设计。通过现代化的 Web 界面，用户可以轻松订阅和监控 GitHub 仓库的最新动态，并接收智能化的报告和通知。

### ✨ 已实现功能

- **🎯 订阅管理** - 完整的 CRUD 操作，支持多种监控选项配置
- **📧 多渠道通知** - 支持邮件、Slack、自定义 Webhook 通知
- **📊 智能报告** - 自动生成日报、周报、月报，支持多种格式
- **📈 数据可视化** - 实时仪表板，展示订阅统计和活动趋势
- **🔧 灵活配置** - 每个订阅可独立配置通知邮箱和推送设置
- **🌐 现代化界面** - 基于 Vue 3 + Element Plus 的响应式 Web UI

### 🚀 核心特性

- **订阅管理** - 灵活管理订阅的 GitHub 仓库列表，支持细粒度监控配置
- **多渠道通知** - 邮件/Slack/Webhook 多渠道推送，每个订阅可配置不同接收者
- **智能报告** - 生成结构化的项目动态报告，支持 HTML/Markdown/JSON 格式
- **实时仪表板** - 可视化展示订阅状态、活动趋势和系统健康状况
- **RESTful API** - 完整的 API 接口，支持第三方集成

## 架构设计

### 核心模块

```
github_sentinel/
├── app/
│   ├── core/              # 核心模块
│   │   ├── config.py      # 配置管理
│   │   ├── scheduler.py   # 任务调度器
│   │   └── database.py    # 数据库连接
│   ├── models/            # 数据模型
│   │   ├── user.py        # 用户模型
│   │   ├── subscription.py # 订阅模型
│   │   └── report.py      # 报告模型
│   ├── services/          # 业务服务
│   │   ├── subscription_service.py   # 订阅管理服务
│   │   ├── github_service.py         # GitHub API 服务
│   │   └── ai_service.py             # AI 分析服务
│   ├── collectors/        # 数据采集器
│   │   ├── github_collector.py       # GitHub 数据采集
│   │   └── base_collector.py         # 采集器基类
│   ├── analyzers/         # 数据分析器
│   │   ├── content_analyzer.py       # 内容分析器
│   │   └── trend_analyzer.py         # 趋势分析器
│   ├── notifiers/         # 通知器
│   │   ├── email_notifier.py         # 邮件通知
│   │   ├── slack_notifier.py         # Slack 通知
│   │   └── webhook_notifier.py       # Webhook 通知
│   ├── reporters/         # 报告生成器
│   │   ├── html_reporter.py          # HTML 报告
│   │   ├── markdown_reporter.py      # Markdown 报告
│   │   └── json_reporter.py          # JSON 报告
│   ├── api/              # API 接口
│   │   ├── routes/        # 路由定义
│   │   └── middleware/    # 中间件
│   └── utils/            # 工具函数
├── config/               # 配置文件
├── tests/                # 测试文件
├── docs/                 # 文档
├── scripts/              # 脚本文件
├── requirements.txt      # 项目依赖
└── main.py              # 应用入口
```

### 技术栈

**后端技术**
- **框架**: FastAPI (高性能异步 Web 框架)
- **数据库**: SQLAlchemy 2.0 + SQLite (支持 PostgreSQL)
- **API 文档**: Swagger/OpenAPI 自动生成
- **数据验证**: Pydantic v2
- **异步支持**: asyncio + httpx

**前端技术**
- **框架**: Vue 3 (Composition API)
- **UI 组件**: Element Plus
- **图表库**: ECharts
- **构建工具**: Vite
- **状态管理**: Vue 3 Reactivity

**通知系统**
- **邮件**: SMTP 支持 (HTML 模板)
- **Slack**: Webhook 集成
- **自定义**: HTTP Webhook 支持

### 数据流

1. **订阅管理**: 用户通过 API 或配置文件管理订阅的仓库
2. **定时调度**: 调度器按配置的频率触发数据收集任务
3. **数据采集**: GitHub Collector 通过 GitHub API 获取仓库动态
4. **智能分析**: AI Analyzer 对收集的数据进行分析和摘要
5. **报告生成**: Reporter 生成格式化的更新报告
6. **通知推送**: Notifier 通过多种渠道推送给用户

## 安装和使用

### 环境要求

- Python 3.8+
- Redis (可选，用于缓存)
- PostgreSQL (可选，默认使用 SQLite)

### 快速开始

1. **克隆项目**
```bash
git clone https://github.com/your-username/github-sentinel.git
cd github-sentinel
```

2. **安装后端依赖**
```bash
pip install -r requirements.txt
```

3. **配置应用**
```bash
# 复制配置文件模板
cp config/config.example.yaml config/config.yaml

# 编辑配置文件，设置必要的参数
nano config/config.yaml
```

4. **初始化数据库**
```bash
python scripts/init_test_data.py
```

5. **启动后端服务**
```bash
python main.py
# 后端服务运行在 http://localhost:8000
```

6. **启动前端服务**
```bash
cd frontend
npm install
npm run dev
# 前端服务运行在 http://localhost:5173
```

7. **访问应用**
- 前端界面: http://localhost:5173
- API 文档: http://localhost:8000/docs
- 管理后台: http://localhost:8000/admin

### 配置说明

**必需配置项：**
- `github.token`: GitHub Personal Access Token（必需）
- `secret_key`: 应用密钥（用于JWT签名）

**可选配置项：**
- `ai.openai_api_key`: OpenAI API Key（用于AI分析）
- `notification.email_*`: 邮件通知配置
- `notification.slack_*`: Slack通知配置

详细配置说明请参考：[config/README.md](config/README.md)

### API 文档

启动应用后，访问 `http://localhost:8000/docs` 查看 Swagger API 文档。

## 📋 开发进度

### ✅ v0.1.0 (已完成)
- [x] 项目架构设计和基础框架
- [x] 用户和订阅管理系统
- [x] 完整的 CRUD API 接口
- [x] Vue 3 前端界面 (订阅管理、报告系统、仪表板)
- [x] 多渠道通知系统 (邮件/Slack/Webhook)
- [x] 报告生成和管理
- [x] 实时数据可视化仪表板
- [x] 每个订阅独立通知配置

### 🚧 v0.2.0 (开发中)
- [ ] GitHub API 集成和数据采集
- [ ] 定时任务调度系统
- [ ] 活动数据存储和分析
- [ ] 报告内容自动生成
- [ ] 通知系统实际发送功能

### 🔮 v1.0.0 (计划中)
- [ ] AI 智能分析和摘要
- [ ] 高级过滤和搜索功能
- [ ] 用户认证和权限管理
- [ ] 系统配置和管理界面
- [ ] 性能优化和缓存

### 🌟 v2.0.0 (未来版本)
- [ ] 多平台支持 (GitLab, Bitbucket)
- [ ] 团队协作和共享功能
- [ ] 高级分析和趋势预测
- [ ] 插件系统和扩展机制
- [ ] 移动端支持

## 贡献指南

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 支持

如有问题或建议，请提交 [Issue](https://github.com/your-username/github-sentinel/issues)。 