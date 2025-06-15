# 常见问题解答 (FAQ)

本文档包含了 GitHub Sentinel 用户最常遇到的问题和解决方案。

## 📋 目录

- [安装和部署](#安装和部署)
- [配置相关](#配置相关)
- [GitHub API](#github-api)
- [AI 服务](#ai-服务)
- [通知系统](#通知系统)
- [性能和扩展](#性能和扩展)
- [故障排除](#故障排除)

## 🛠️ 安装和部署

### Q: 支持哪些操作系统？
**A:** GitHub Sentinel 支持所有主流操作系统：
- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu 18.04+, CentOS 7+, Debian 9+)
- Docker 容器环境

### Q: 最低系统要求是什么？
**A:** 
- **Python**: 3.8 或更高版本
- **内存**: 最少 512MB，推荐 2GB+
- **存储**: 最少 1GB 可用空间
- **网络**: 能访问 GitHub API 和 AI 服务

### Q: 可以在 Docker 中运行吗？
**A:** 是的，我们提供了 Docker 支持（即将发布）：
```bash
# 构建镜像
docker build -t github-sentinel .

# 运行容器
docker run -d -p 8000:8000 \
  -v ./config:/app/config \
  -v ./logs:/app/logs \
  github-sentinel
```

### Q: 支持 Python 虚拟环境吗？
**A:** 强烈推荐使用虚拟环境：
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## ⚙️ 配置相关

### Q: 必须配置哪些参数才能运行？
**A:** 最少需要配置：
```yaml
github:
  token: "your_github_token"

ai:
  provider: "openai"  # 或 "ollama"
  openai_api_key: "your_openai_key"  # 如果使用 OpenAI
```

### Q: 配置文件放在哪里？
**A:** 配置文件的查找顺序：
1. `config/config.yaml`
2. `./config.yaml`
3. 环境变量
4. 默认值

### Q: 如何安全地存储敏感信息？
**A:** 建议使用环境变量：
```bash
# 设置环境变量
export GITHUB__TOKEN="your_token"
export AI__OPENAI_API_KEY="your_key"
export NOTIFICATION__EMAIL_PASSWORD="your_password"
```

### Q: 可以使用多个配置文件吗？
**A:** 可以通过环境变量指定配置文件：
```bash
export CONFIG_FILE="config/production.yaml"
python main.py serve
```

## 🔧 GitHub API

### Q: 需要什么 GitHub 权限？
**A:** 根据需求选择权限：
- **public_repo**: 访问公共仓库（必需）
- **repo**: 访问私有仓库（可选）
- **read:org**: 读取组织信息（可选）
- **read:user**: 读取用户信息（推荐）

### Q: GitHub API 有使用限制吗？
**A:** 是的，GitHub API 有速率限制：
- **未认证**: 60 请求/小时
- **已认证**: 5,000 请求/小时
- **GitHub Enterprise**: 15,000 请求/小时

系统会自动处理限制并重试。

### Q: 如何监控 API 使用情况？
**A:** 
1. 查看日志文件中的 API 调用记录
2. 使用 GitHub API 检查剩余配额：
```bash
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/rate_limit
```

### Q: 支持 GitHub Enterprise 吗？
**A:** 支持，修改 API URL：
```yaml
github:
  api_url: "https://your-github-enterprise.com/api/v3"
  token: "your_token"
```

## 🤖 AI 服务

### Q: 必须使用 OpenAI 吗？
**A:** 不是，我们支持多种 AI 提供商：
- **OpenAI**: GPT-3.5/GPT-4（云服务）
- **Ollama**: 本地部署的开源模型
- **Azure OpenAI**: 企业级服务（即将支持）

### Q: Ollama 如何配置？
**A:** 
1. 安装 Ollama：
```bash
# 下载并安装 Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 拉取模型
ollama pull llama2
ollama pull mistral
```

2. 配置 GitHub Sentinel：
```yaml
ai:
  provider: "ollama"
  ollama_url: "http://localhost:11434"
  ollama_model: "llama2"
```

### Q: AI 分析消耗多少 tokens？
**A:** 大致估算：
- **每个 Issue/PR**: 50-200 tokens
- **每日报告**: 500-2000 tokens
- **每周报告**: 2000-8000 tokens

OpenAI GPT-3.5-turbo 约 $0.002/1K tokens。

### Q: 可以关闭 AI 功能吗？
**A:** 可以，但会影响报告质量：
```yaml
ai:
  provider: "none"  # 禁用 AI 分析
```

## 📧 通知系统

### Q: Gmail 应用专用密码怎么设置？
**A:** 
1. 启用 Google 账户的两步验证
2. 访问 [Google 账户安全设置](https://myaccount.google.com/security)
3. 选择"应用专用密码"
4. 生成密码并用于邮件配置

### Q: 支持哪些邮件服务商？
**A:** 支持所有标准 SMTP 服务：
- Gmail, Outlook, Yahoo
- 腾讯企业邮箱、阿里云邮箱
- 自建邮件服务器

### Q: Slack 通知显示格式错误？
**A:** 检查 Webhook URL 和消息格式：
```yaml
# 确保 URL 正确
slack_webhook_url: "https://hooks.slack.com/services/T.../B.../..."

# 检查频道名称格式
slack_channel: "#channel-name"  # 包含 #
```

### Q: 可以自定义通知内容吗？
**A:** 可以，通过模板系统：
```yaml
notification:
  email_template: "custom_email_template.html"
  slack_template: "custom_slack_template.json"
```

## 📊 性能和扩展

### Q: 可以同时监控多少个仓库？
**A:** 理论上没有限制，实际受以下因素影响：
- GitHub API 限制（5000 请求/小时）
- 系统资源（内存、CPU）
- 数据库性能

建议：
- **个人使用**: 10-50 个仓库
- **团队使用**: 50-200 个仓库
- **企业使用**: 配置 Redis 缓存和 PostgreSQL

### Q: 如何优化性能？
**A:** 
1. **使用 PostgreSQL**：
```yaml
database:
  url: "postgresql+asyncpg://user:pass@localhost/db"
```

2. **启用 Redis 缓存**：
```yaml
redis:
  enabled: true
  host: "localhost"
  port: 6379
```

3. **调整并发数**：
```yaml
github:
  max_concurrent_requests: 10
```

### Q: 支持集群部署吗？
**A:** 当前版本不支持，但可以：
- 使用负载均衡器分发 API 请求
- 使用共享数据库和 Redis
- 将任务调度器单独部署

### Q: 数据库会占用多少空间？
**A:** 取决于监控的仓库数量和活跃度：
- **10 个活跃仓库**: ~100MB/月
- **100 个活跃仓库**: ~1GB/月
- **1000 个活跃仓库**: ~10GB/月

## 🔍 故障排除

### Q: 服务启动失败怎么办？
**A:** 检查以下方面：
1. **端口占用**：
```bash
# 检查端口
netstat -an | grep 8000
# 使用其他端口
python main.py serve --port 8001
```

2. **权限问题**：
```bash
# 检查日志目录权限
mkdir -p logs
chmod 755 logs
```

3. **依赖缺失**：
```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

### Q: 数据库连接失败？
**A:** 
1. **SQLite 权限问题**：
```bash
# 检查文件权限
ls -la github_sentinel.db
chmod 664 github_sentinel.db
```

2. **PostgreSQL 连接**：
```bash
# 测试连接
psql "postgresql://user:pass@localhost/dbname"
```

### Q: GitHub API 请求失败？
**A:** 
1. **检查 token 有效性**：
```bash
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/user
```

2. **网络连接问题**：
```bash
# 测试网络
ping api.github.com
```

3. **代理设置**：
```yaml
github:
  proxy: "http://proxy.company.com:8080"
```

### Q: 日志文件在哪里？
**A:** 
- **应用日志**: `logs/github_sentinel.log`
- **访问日志**: `logs/access.log`
- **错误日志**: `logs/error.log`

查看日志：
```bash
# 实时日志
tail -f logs/github_sentinel.log

# 错误日志
grep -i error logs/github_sentinel.log

# 最近 100 行
tail -n 100 logs/github_sentinel.log
```

### Q: 如何重置所有数据？
**A:** 
```bash
# 停止服务
pkill -f "python main.py"

# 删除数据库
rm github_sentinel.db

# 清空日志
rm -rf logs/*

# 重新初始化
python main.py init
```

## 💡 最佳实践

### Q: 生产环境部署建议？
**A:** 
1. **使用 PostgreSQL**
2. **启用 Redis 缓存**
3. **配置反向代理** (Nginx)
4. **使用进程管理器** (systemd, supervisor)
5. **启用 HTTPS**
6. **定期备份数据库**

### Q: 如何备份数据？
**A:** 
```bash
# SQLite 备份
cp github_sentinel.db backup/github_sentinel_$(date +%Y%m%d).db

# PostgreSQL 备份
pg_dump github_sentinel > backup/github_sentinel_$(date +%Y%m%d).sql
```

### Q: 监控和告警建议？
**A:** 
- **健康检查**: 定期调用 `/api/v1/health`
- **日志监控**: 使用 ELK Stack 或 Grafana
- **资源监控**: CPU、内存、磁盘使用率
- **API 使用**: 监控 GitHub API 配额

## 📞 获取更多帮助

如果您的问题没有在此 FAQ 中找到答案：

1. **查看完整文档**：
   - [配置指南](configuration-guide.md)
   - [快速开始](quick-start.md)
   - [API 参考](api-reference.md)

2. **社区支持**：
   - [GitHub Issues](https://github.com/your-username/github-sentinel/issues)
   - [GitHub Discussions](https://github.com/your-username/github-sentinel/discussions)

3. **联系我们**：
   - 📧 support@github-sentinel.com
   - 💬 [Slack 社区](https://github-sentinel.slack.com)

---

**此文档会持续更新，如果您遇到新问题，欢迎提交 Issue 或 PR 来改进这个 FAQ！** 