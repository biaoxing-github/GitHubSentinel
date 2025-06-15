# GitHub Sentinel 快速开始指南

本指南将帮助您在 5 分钟内快速部署并开始使用 GitHub Sentinel。

## 🎯 目标

完成本指南后，您将能够：
- ✅ 成功部署 GitHub Sentinel
- ✅ 订阅您的第一个 GitHub 仓库
- ✅ 配置基础通知
- ✅ 生成第一份报告

## ⚡ 快速部署

### 第一步：环境准备

```bash
# 检查 Python 版本（需要 3.8+）
python --version

# 克隆项目
git clone https://github.com/your-username/github-sentinel.git
cd github-sentinel

# 安装依赖
pip install -r requirements.txt
```

### 第二步：基础配置

```bash
# 复制配置文件
cp config/config.example.yaml config/config.yaml
```

编辑 `config/config.yaml`，只需配置以下必需项：

```yaml
# 最小化配置 - 只需修改这两项
github:
  token: "your_github_token_here"  # 👈 在这里填入您的 GitHub Token

ai:
  provider: "openai"
  openai_api_key: "your_openai_key_here"  # 👈 在这里填入您的 OpenAI Key
```

### 第三步：获取必需的 API Keys

#### 获取 GitHub Token（必需）

1. 访问 [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token (classic)"
3. 勾选权限：
   - ✅ `public_repo` - 访问公共仓库
   - ✅ `repo` - 访问私有仓库（可选）
4. 复制生成的 token 到配置文件

#### 获取 OpenAI API Key（推荐）

1. 访问 [OpenAI API Keys](https://platform.openai.com/api-keys)
2. 创建新的 API Key
3. 复制到配置文件

> 💡 **提示**：如果不想使用 OpenAI，可以配置本地 Ollama，参考 [AI 配置指南](configuration-guide.md#ai-服务配置)

### 第四步：初始化和启动

```bash
# 初始化数据库
python main.py init

# 启动服务（开发模式）
python main.py serve --reload
```

看到以下输出表示启动成功：
```
INFO     GitHub Sentinel 正在启动...
INFO     数据库初始化完成
INFO     任务调度器启动完成
INFO     GitHub Sentinel 启动完成！
INFO     Application startup complete.
INFO     Uvicorn running on http://0.0.0.0:8000
```

## 📊 快速体验

### 1. 访问 API 文档

打开浏览器访问：http://localhost:8000/docs

您将看到 Swagger API 文档界面。

### 2. 健康检查

测试服务是否正常运行：

```bash
curl http://localhost:8000/api/v1/health
```

应该返回：
```json
{
  "status": "healthy",
  "service": "GitHub Sentinel",
  "version": "1.0.0"
}
```

### 3. 添加第一个订阅

使用 CLI 命令添加您的第一个 GitHub 仓库订阅：

```bash
# 示例：订阅 FastAPI 仓库
python main.py add-subscription --repo tiangolo/fastapi
```

或者使用您自己的仓库：
```bash
python main.py add-subscription --repo your-username/your-repo
```

### 4. 手动触发数据收集

```bash
# 手动收集数据（测试用）
python main.py collect
```

### 5. 查看日志

```bash
# 实时查看日志
tail -f logs/github_sentinel.log
```

## 🔔 配置基础通知

### 邮件通知（推荐）

如果您使用 Gmail，编辑 `config/config.yaml`：

```yaml
notification:
  email_enabled: true
  email_smtp_host: "smtp.gmail.com"
  email_smtp_port: 587
  email_username: "your_email@gmail.com"
  email_password: "your_app_password"  # Gmail 应用专用密码
  email_from: "your_email@gmail.com"
  email_to:
    - "your_email@gmail.com"  # 发送给自己
```

> 📧 **Gmail 配置提示**：需要生成应用专用密码，详见 [通知配置指南](notification-setup.md#gmail-配置推荐)

### Slack 通知（可选）

如果您使用 Slack：

```yaml
notification:
  slack_enabled: true
  slack_webhook_url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
  slack_channel: "#github-updates"
```

> 💬 **Slack 配置提示**：需要创建 Slack App 和 Webhook，详见 [通知配置指南](notification-setup.md#创建-slack-webhook)

## ⚙️ 配置定时任务

默认配置每天早上 8 点执行数据收集：

```yaml
schedule:
  enabled: true
  daily_time: "08:00"    # 每日 8:00 收集数据
  weekly_day: 1          # 周一
  weekly_time: "08:00"   # 每周一 8:00 生成周报
  timezone: "Asia/Shanghai"
```

## 📈 生成第一份报告

```bash
# 手动生成今日报告
python main.py generate-report --type daily

# 查看生成的报告
ls -la reports/
```

## 🎉 完成！

恭喜！您已经成功部署了 GitHub Sentinel。现在系统将：

- 🔄 每天自动收集您订阅仓库的动态
- 🤖 使用 AI 分析和总结内容
- 📧 通过邮件/Slack 发送通知
- 📊 生成详细的活动报告

## 📚 下一步

现在您可以：

1. **添加更多订阅**：
   ```bash
   python main.py add-subscription --repo microsoft/vscode
   python main.py add-subscription --repo facebook/react
   ```

2. **自定义监控配置**：
   - 编辑订阅设置
   - 配置过滤规则
   - 调整通知频率

3. **探索高级功能**：
   - [API 文档](api-reference.md)
   - [配置指南](configuration-guide.md)
   - [通知设置](notification-setup.md)

## 🆘 遇到问题？

### 常见问题快速解决

1. **端口被占用**：
   ```bash
   python main.py serve --port 8001
   ```

2. **GitHub API 限制**：
   - 检查 token 是否有效
   - 验证权限设置

3. **数据库错误**：
   ```bash
   # 重新初始化数据库
   rm github_sentinel.db
   python main.py init
   ```

4. **依赖安装失败**：
   ```bash
   # 使用国内镜像
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
   ```

### 获取帮助

- 📖 查看 [FAQ](faq.md)
- 🐛 提交 [GitHub Issue](https://github.com/your-username/github-sentinel/issues)
- 📧 发送邮件到 support@github-sentinel.com

## 🎯 性能提示

- **生产环境**：使用 PostgreSQL 替代 SQLite
- **大量订阅**：启用 Redis 缓存
- **高并发**：使用 Gunicorn 部署
- **监控**：集成 Prometheus 指标

详细的生产部署指南请参考 [部署指南](deployment.md)。

---

🎊 **欢迎使用 GitHub Sentinel！** 

如果您觉得这个项目有用，请在 GitHub 上给我们一个 ⭐ Star！ 