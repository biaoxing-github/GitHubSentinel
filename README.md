# GitHubSentinel 🚀

> 智能GitHub仓库监控与分析平台

[![Version](https://img.shields.io/badge/version-v0.3.0-blue.svg)](https://github.com/your-username/GitHubSentinel/releases/tag/v0.3.0)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Vue](https://img.shields.io/badge/vue-3.0+-brightgreen.svg)](https://vuejs.org)
[![FastAPI](https://img.shields.io/badge/fastapi-0.100+-red.svg)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/langchain-0.1+-purple.svg)](https://langchain.com)
[![PWA](https://img.shields.io/badge/PWA-enabled-orange.svg)](https://web.dev/progressive-web-apps/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

GitHubSentinel 是一个现代化的GitHub仓库监控与AI智能分析平台，提供实时活动追踪、AI驱动的智能分析、WebSocket实时通信、PWA离线支持等功能。

## ✨ 核心特性

### 🎯 v0.3.0 最新功能
- **🤖 AI智能分析助手**: 基于LangChain的智能仓库分析和对话系统
- **🔔 WebSocket实时通信**: 支持实时通知、多频道广播和进度推送
- **📱 PWA渐进式Web应用**: 完整的离线支持、应用安装和推送通知
- **🖥️ 系统监控面板**: 实时性能监控、服务状态管理和运维工具
- **🔐 增强认证系统**: JWT令牌认证和多层安全保护
- **🎨 现代化界面**: 5个全新页面，Element Plus设计语言

### 🎯 v0.2.0 历史功能
- **🕒 北京时间显示**: 前端统一使用北京时间，提供本地化体验
- **📊 智能时间筛选**: Dashboard支持1天/3天/7天/30天时间周期筛选
- **📈 性能指标监控**: 完整的Performance Metrics接口，实时监控系统性能
- **📧 现代化邮件通知**: 邮件模板样式与HTML报告完全一致
- **🔍 高级活动筛选**: 支持按仓库、活动类型、时间周期多维度筛选

### 🎯 v0.1.0 基础功能
- **🏠 仓库监控**: GitHub仓库实时活动追踪和数据收集
- **📊 数据面板**: 基础的Dashboard和数据展示
- **📝 报告系统**: HTML/Markdown格式报告生成
- **📧 邮件通知**: 基础邮件通知功能
- **🔗 API接口**: RESTful API和Swagger文档

### 🏠 仓库监控
- **实时活动追踪**: 监控commits、issues、pull requests、releases等活动
- **多仓库管理**: 支持同时监控多个GitHub仓库
- **智能数据收集**: 自动收集和分析仓库数据
- **活动统计分析**: 提供详细的活动趋势和统计信息

### 📊 数据分析与可视化
- **交互式Dashboard**: 现代化的数据展示面板
- **实时统计图表**: 活动趋势、贡献者分析、代码提交统计
- **多维度筛选**: 按时间、仓库、活动类型灵活筛选数据
- **性能指标监控**: 系统响应时间、成功率、健康评分等指标

### 📝 智能报告系统
- **AI驱动分析**: 集成AI进行智能数据分析和趋势预测
- **多格式报告**: 支持HTML、Markdown、PDF等多种格式
- **自动化生成**: 定时生成和发送报告
- **个性化模板**: 可自定义报告模板和样式

### 📧 通知与提醒
- **邮件通知**: 现代化设计的HTML邮件模板
- **实时提醒**: 重要活动和异常情况及时通知
- **多渠道支持**: 邮件、Webhook等多种通知方式
- **智能筛选**: 根据重要性和用户偏好发送通知

## 🏗️ 技术架构

### 后端技术栈
- **FastAPI**: 现代化的Python Web框架
- **LangChain**: AI语言模型集成框架 🆕
- **WebSocket**: 实时双向通信协议 🆕
- **SQLAlchemy**: 强大的ORM框架
- **PostgreSQL**: 可靠的关系型数据库
- **JWT**: JSON Web Token认证 🆕
- **Redis**: 缓存和消息代理

### 前端技术栈
- **Vue 3**: 渐进式JavaScript框架
- **Element Plus**: 企业级UI组件库 🆕
- **PWA**: 渐进式Web应用支持 🆕
- **ECharts**: 数据可视化图表库 🆕
- **Vue Router**: 官方路由管理器
- **Axios**: HTTP客户端库

### AI与智能化
- **OpenAI GPT-4**: 强大的语言模型 🆕
- **智能分析**: 仓库智能分析和摘要 🆕
- **对话系统**: 自然语言交互 🆕
- **上下文感知**: 基于数据的智能回答 🆕

### 开发工具
- **Docker**: 容器化部署
- **GitHub Actions**: CI/CD自动化
- **ESLint**: 代码质量检查
- **Prettier**: 代码格式化

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/GitHubSentinel.git
cd GitHubSentinel
```

2. **后端设置**
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库和GitHub API密钥

# 初始化数据库
python -m app.core.database init

# 启动后端服务
python main.py
```

3. **前端设置**
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

4. **访问应用**
- 前端界面: http://localhost:3000
- API文档: http://localhost:8000/docs

## 📖 使用指南

### 1. 添加仓库监控
1. 访问Dashboard页面
2. 点击"Add Repository"按钮
3. 输入GitHub仓库URL
4. 配置监控选项
5. 保存并开始监控

### 2. 查看活动数据
1. 在Dashboard查看实时活动统计
2. 使用时间筛选器选择查看周期
3. 点击"View All"查看详细活动列表
4. 支持按仓库和活动类型筛选

### 3. 生成分析报告
1. 进入Reports页面
2. 选择要分析的仓库
3. 配置报告参数（时间范围、格式等）
4. 点击"Generate Report"
5. 查看或下载生成的报告

### 4. 配置通知设置
1. 进入Settings页面
2. 配置邮件服务器设置
3. 设置通知规则和频率
4. 测试通知功能

## 🎨 界面预览

### Dashboard 主面板
- 📊 实时统计卡片
- 📈 活动趋势图表
- 🔍 智能筛选器
- ⚡ 快速操作按钮

### Activities 活动页面
- 📋 详细活动列表
- 🔍 多维度筛选
- 📄 分页浏览
- 🔗 外部链接跳转

### Reports 报告中心
- 📝 报告列表管理
- 🎨 多样式模板
- 📊 数据可视化
- 📧 自动发送功能

## 🔧 配置说明

### 环境变量配置
```env
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost/githubsentinel

# GitHub API配置
GITHUB_TOKEN=your_github_token

# 邮件服务配置
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Redis配置
REDIS_URL=redis://localhost:6379

# 应用配置
SECRET_KEY=your_secret_key
DEBUG=false
```

### 功能开关
```env
# 启用AI分析功能
ENABLE_AI_ANALYSIS=true

# 启用邮件通知
ENABLE_EMAIL_NOTIFICATIONS=true

# 启用性能监控
ENABLE_PERFORMANCE_MONITORING=true
```

## 📊 API文档

### 主要接口

#### Dashboard API
- `GET /api/dashboard/stats` - 获取统计数据
- `GET /api/dashboard/recent-activity` - 获取最近活动
- `GET /api/dashboard/performance-metrics` - 获取性能指标

#### Reports API
- `GET /api/reports` - 获取报告列表
- `POST /api/reports/generate` - 生成新报告
- `GET /api/reports/{id}/download` - 下载报告

#### Subscriptions API
- `GET /api/subscriptions` - 获取订阅列表
- `POST /api/subscriptions` - 添加新订阅
- `PUT /api/subscriptions/{id}` - 更新订阅

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 开发流程
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范
- 后端遵循 PEP 8 规范
- 前端使用 ESLint + Prettier
- 提交信息遵循 Conventional Commits

## 📝 更新日志

### v0.2.0 (2024-12-XX)
🎯 **主要功能更新**
- ✅ 前端时间显示统一使用北京时间
- ✅ Dashboard Recent Activity 增加时间筛选功能
- ✅ 完善 Performance Metrics 接口实现
- ✅ 邮件通知模板样式与HTML报告保持一致
- ✅ 修复 Activities.vue 图标导入错误
- ✅ 优化数据库查询逻辑，使用GitHub实际活动时间

🔧 **技术改进**
- 创建时间工具函数统一时间处理
- 数据库模型时间字段使用北京时间默认值
- API接口支持时间周期参数筛选
- 前端组件支持响应式时间筛选

### v0.1.0 (2024-11-XX)
- 🎉 初始版本发布
- 📊 基础Dashboard功能
- 🏠 仓库监控功能
- 📝 报告生成系统
- 📧 邮件通知功能

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Element Plus](https://element-plus.org/) - Vue 3 UI组件库
- [GitHub API](https://docs.github.com/en/rest) - 强大的GitHub数据接口

## 📞 联系我们

- 📧 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/GitHubSentinel/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-username/GitHubSentinel/discussions)

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！

## 🔮 v0.3.0 开发计划

### 🤖 AI智能分析与摘要生成
- **智能代码分析**: 
  - 集成GPT-4/Claude等大模型分析代码变更
  - 自动识别重要功能更新和Breaking Changes
  - 生成技术债务和代码质量分析报告
- **智能摘要生成**:
  - AI驱动的仓库活动摘要
  - 自动生成周报/月报的文字描述
  - 智能识别项目发展趋势和关键里程碑
- **对话式查询**:
  - 自然语言查询仓库数据
  - "这个仓库最近有什么重要更新？"
  - "分析一下项目的发展趋势"

### 🔔 实时通知与WebSocket支持
- **WebSocket实时推送**:
  - 仓库活动实时推送到Dashboard
  - 实时显示新的Issues、PRs、Commits
  - 在线用户状态同步
- **智能通知规则**:
  - 基于重要性的通知分级
  - 用户自定义通知规则
  - 静默时段和频率控制
- **多平台通知集成**:
  - 微信企业号集成
  - 钉钉机器人支持
  - Telegram Bot集成
  - Discord Webhook支持

### 📱 移动端优化与PWA
- **PWA支持**:
  - 离线数据缓存
  - 桌面安装支持
  - 后台同步功能
- **移动端优化**:
  - 响应式设计完善
  - 触摸手势支持
  - 移动端专属界面
- **推送通知**:
  - 系统级通知支持
  - 离线消息缓存
  - 通知历史管理

## 📅 开发时间线

### Phase 1: AI智能分析 (预计2个月)
- 🤖 AI分析引擎基础框架
- 📝 智能摘要生成算法
- 💬 对话式查询接口

### Phase 2: 实时通知系统 (预计1.5个月)
- 🔔 WebSocket实时通信
- 📢 多平台通知集成
- ⚙️ 智能通知规则引擎

### Phase 3: 移动端与PWA (预计2个月)
- 📱 移动端界面优化
- 💾 PWA离线功能
- 🔔 系统级推送通知

### Phase 4: 集成测试与优化 (预计1个月)
- 🧪 功能集成测试
- 🔧 性能优化调整
- 🐛 Bug修复和稳定性提升

## 🎯 技术选型

### AI智能分析技术栈
- **AI服务**: OpenAI GPT-4, Anthropic Claude
- **自然语言处理**: LangChain, Transformers
- **数据分析**: Pandas, NumPy, scikit-learn

### 实时通信技术栈
- **实时通信**: Socket.IO, WebSocket
- **消息队列**: RabbitMQ, Redis Streams
- **通知服务**: Firebase Cloud Messaging

### 移动端PWA技术栈
- **PWA框架**: Workbox, Service Worker
- **移动端优化**: Vant UI, Touch Events
- **离线存储**: IndexedDB, LocalStorage

### 基础设施
- **容器化**: Docker, Docker Compose
- **监控**: Prometheus, Grafana
- **CI/CD**: GitHub Actions

## 🤝 参与v0.3.0开发

我们欢迎社区贡献者参与v0.3.0的开发！

### 贡献方式
- **AI功能开发**: 智能分析算法和对话式查询
- **实时通信**: WebSocket和多平台通知集成
- **移动端开发**: PWA功能和移动端界面优化
- **测试**: 自动化测试用例编写
- **文档**: 用户指南和开发文档

### 开发环境搭建
```bash
# 克隆开发分支
git clone -b v0.3-dev https://github.com/your-username/GitHubSentinel.git

# 安装开发依赖
pip install -r requirements-dev.txt
npm install --include=dev

# 启动开发环境
docker-compose -f docker-compose.dev.yml up
```

### 讨论和反馈
- 💬 加入我们的Discord开发者社区
- 📧 订阅开发者邮件列表
- 🐛 提交Issue报告Bug或建议
- 🎯 参与Feature Request投票

---

⭐ 如果您对v0.3.0的功能感兴趣，请关注我们的开发进度！