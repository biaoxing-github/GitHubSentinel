# GitHub Sentinel 配置指南

本指南将帮助您完成 GitHub Sentinel 的所有配置步骤，确保系统正常运行。

## 📋 目录

1. [快速开始](#快速开始)
2. [基础配置](#基础配置)
3. [数据库配置](#数据库配置)
4. [GitHub API 配置](#github-api-配置)
5. [AI 服务配置](#ai-服务配置)
6. [任务调度配置](#任务调度配置)
7. [通知系统配置](#通知系统配置)
8. [安全配置](#安全配置)
9. [高级配置](#高级配置)
10. [故障排除](#故障排除)

## 🚀 快速开始

### 1. 环境准备

确保您的系统满足以下要求：

```bash
# 检查 Python 版本
python --version
# 需要 Python 3.8 或更高版本

# 安装依赖
pip install -r requirements.txt
```

### 2. 创建配置文件

```bash
# 从示例文件创建配置文件
cp config/config.example.yaml config/config.yaml
```

### 3. 最小化配置

编辑 `config/config.yaml`，至少需要配置以下项：

```yaml
github:
  token: "your_github_personal_access_token"

ai:
  provider: "openai"  # 或 "ollama"
  openai_api_key: "your_openai_api_key"  # 如果使用 OpenAI
```

### 4. 初始化和启动

```bash
# 初始化数据库
python main.py init

# 启动服务
python main.py serve
```

## ⚙️ 基础配置

### 应用设置

```yaml
# 应用基础信息
app_name: "GitHub Sentinel"
app_version: "1.0.0"
debug: false  # 生产环境设为 false

# 日志配置
log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR
log_file: "logs/github_sentinel.log"
```

**参数说明：**
- `debug`: 开启调试模式，会显示详细的错误信息
- `log_level`: 日志级别，建议生产环境使用 INFO
- `log_file`: 日志文件路径，确保目录存在

## 🗄️ 数据库配置

### SQLite（默认，推荐开发环境）

```yaml
database:
  url: "sqlite+aiosqlite:///./github_sentinel.db"
  echo: false
  pool_size: 5
  max_overflow: 10
```

### PostgreSQL（推荐生产环境）

```yaml
database:
  url: "postgresql+asyncpg://username:password@localhost:5432/github_sentinel"
  echo: false
  pool_size: 20
  max_overflow: 50
```

**PostgreSQL 设置步骤：**

1. 安装 PostgreSQL 数据库
2. 创建数据库和用户：
```sql
CREATE DATABASE github_sentinel;
CREATE USER github_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE github_sentinel TO github_user;
```
3. 安装异步驱动：
```bash
pip install asyncpg
```

**参数说明：**
- `echo`: 是否打印 SQL 语句（调试用）
- `pool_size`: 连接池大小
- `max_overflow`: 连接池最大溢出连接数

## 🔧 GitHub API 配置

### 获取 GitHub Token

1. 访问 [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token (classic)"
3. 选择所需权限：
   - `repo` - 访问私有仓库（可选）
   - `public_repo` - 访问公共仓库
   - `read:org` - 读取组织信息（可选）
   - `read:user` - 读取用户信息

### 配置参数

```yaml
github:
  token: "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  api_url: "https://api.github.com"
  max_requests_per_hour: 5000
  retry_attempts: 3
  retry_delay: 60
```

**参数说明：**
- `token`: GitHub Personal Access Token
- `max_requests_per_hour`: API 限制（认证用户为 5000/小时）
- `retry_attempts`: 请求失败重试次数
- `retry_delay`: 重试间隔（秒）

**注意事项：**
- 妥善保管您的 token，不要提交到版本控制系统
- 定期更新 token 以确保安全
- 监控 API 使用配额避免超限

## 🤖 AI 服务配置

### OpenAI 配置

```yaml
ai:
  provider: "openai"
  openai_api_key: "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  openai_model: "gpt-3.5-turbo"  # 或 "gpt-4"
  max_tokens: 1000
  temperature: 0.7
```

**获取 OpenAI API Key：**
1. 访问 [OpenAI API Keys](https://platform.openai.com/api-keys)
2. 创建新的 API Key
3. 设置使用限制和预算

### Ollama 本地部署配置

```yaml
ai:
  provider: "ollama"
  ollama_url: "http://localhost:11434"
  ollama_model: "llama2"  # 或其他支持的模型
  max_tokens: 1000
  temperature: 0.7
```

**Ollama 安装步骤：**
1. 从 [Ollama 官网](https://ollama.ai/) 下载安装
2. 拉取模型：
```bash
ollama pull llama2
# 或其他模型：mistral, codellama, etc.
```
3. 启动服务：
```bash
ollama serve
```

**参数说明：**
- `provider`: AI 服务提供商（openai 或 ollama）
- `max_tokens`: 生成的最大 token 数
- `temperature`: 生成随机性（0-1，越高越随机）

## ⏰ 任务调度配置

```yaml
schedule:
  enabled: true
  daily_time: "08:00"    # 每日执行时间
  weekly_day: 1          # 每周执行日（1=周一，7=周日）
  weekly_time: "08:00"   # 每周执行时间
  timezone: "Asia/Shanghai"  # 时区
```

**时区设置：**
- 使用 IANA 时区数据库格式
- 常用时区：
  - `Asia/Shanghai` - 中国标准时间
  - `America/New_York` - 美国东部时间
  - `Europe/London` - 英国时间
  - `UTC` - 协调世界时

**调度说明：**
- 每日任务：在指定时间执行数据收集
- 每周任务：在指定的周几和时间执行周报生成
- 系统会自动处理夏令时变化

## 📧 通知系统配置

详细的通知配置请参考：[通知配置指南](notification-setup.md)

### 邮件通知

```yaml
notification:
  email_enabled: true
  email_smtp_host: "smtp.gmail.com"
  email_smtp_port: 587
  email_username: "your_email@gmail.com"
  email_password: "your_app_password"
  email_from: "your_email@gmail.com"
  email_to:
    - "recipient1@example.com"
    - "recipient2@example.com"
```

### Slack 通知

```yaml
notification:
  slack_enabled: true
  slack_webhook_url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
  slack_channel: "#github-updates"
```

### Webhook 通知

```yaml
notification:
  webhook_enabled: true
  webhook_urls:
    - "https://your-webhook-endpoint.com/github-sentinel"
```

## 🔒 安全配置

```yaml
# 安全相关配置
secret_key: "your-super-secret-key-change-this-in-production"
access_token_expire_minutes: 30
```

**安全建议：**
1. 生成强密钥：
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
2. 定期更换密钥
3. 使用环境变量存储敏感信息
4. 启用 HTTPS（生产环境）

## 🔍 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库 URL 格式
   - 确认数据库服务正在运行
   - 验证用户名和密码

2. **GitHub API 限制**
   - 检查 token 是否有效
   - 监控 API 使用情况
   - 调整请求频率

3. **AI 服务不可用**
   - 验证 API Key 是否正确
   - 检查网络连接
   - 确认服务提供商状态

4. **任务调度不工作**
   - 检查时区设置
   - 验证调度配置格式
   - 查看日志文件

### 调试模式

启用调试模式获取更详细的错误信息：

```yaml
debug: true
log_level: "DEBUG"
```

### 日志分析

```bash
# 查看实时日志
tail -f logs/github_sentinel.log

# 搜索错误
grep -i error logs/github_sentinel.log

# 分析 API 调用
grep -i "GitHub API" logs/github_sentinel.log
```

## 📞 获取帮助

如果您遇到问题：

1. 查看 [FAQ](faq.md)
2. 搜索 [GitHub Issues](https://github.com/your-username/github-sentinel/issues)
3. 提交新的 Issue
4. 参考 [API 文档](api-reference.md)

---

下一步：[通知配置详细指南](notification-setup.md) 