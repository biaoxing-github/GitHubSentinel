# 通知系统配置指南

GitHub Sentinel 支持多种通知渠道，包括邮件、Slack 和自定义 Webhook。本指南将详细介绍每种通知方式的配置步骤。

## 📋 目录

1. [邮件通知配置](#邮件通知配置)
2. [Slack 通知配置](#slack-通知配置)
3. [Webhook 通知配置](#webhook-通知配置)
4. [通知模板自定义](#通知模板自定义)
5. [故障排除](#故障排除)

## 📧 邮件通知配置

### Gmail 配置（推荐）

Gmail 是最常用的邮件服务，配置相对简单：

```yaml
notification:
  email_enabled: true
  email_smtp_host: "smtp.gmail.com"
  email_smtp_port: 587
  email_username: "your_email@gmail.com"
  email_password: "your_app_password"  # 注意：这不是您的Gmail密码
  email_from: "your_email@gmail.com"
  email_to:
    - "recipient1@example.com"
    - "recipient2@example.com"
```

#### 获取 Gmail 应用专用密码

1. **启用两步验证**：
   - 访问 [Google Account Security](https://myaccount.google.com/security)
   - 启用"两步验证"

2. **生成应用专用密码**：
   - 在安全设置中找到"应用专用密码"
   - 选择"邮件"和"其他（自定义名称）"
   - 输入"GitHub Sentinel"
   - 复制生成的16位密码

3. **配置文件中使用**：
   ```yaml
   email_password: "abcd efgh ijkl mnop"  # 使用生成的应用专用密码
   ```

### Outlook/Hotmail 配置

```yaml
notification:
  email_enabled: true
  email_smtp_host: "smtp-mail.outlook.com"
  email_smtp_port: 587
  email_username: "your_email@outlook.com"
  email_password: "your_password"
  email_from: "your_email@outlook.com"
  email_to:
    - "recipient@example.com"
```

### 企业邮箱配置

不同企业邮箱的 SMTP 设置：

#### 腾讯企业邮箱
```yaml
email_smtp_host: "smtp.exmail.qq.com"
email_smtp_port: 465  # 或 587
```

#### 阿里云企业邮箱
```yaml
email_smtp_host: "smtp.mxhichina.com"
email_smtp_port: 465
```

#### 网易企业邮箱
```yaml
email_smtp_host: "smtp.ym.163.com"
email_smtp_port: 994
```

### 邮件安全配置

对于生产环境，建议使用环境变量存储敏感信息：

```bash
# 设置环境变量
export NOTIFICATION__EMAIL_PASSWORD="your_app_password"
export NOTIFICATION__EMAIL_USERNAME="your_email@gmail.com"
```

配置文件可以留空，系统会自动读取环境变量：

```yaml
notification:
  email_enabled: true
  email_smtp_host: "smtp.qq.com"
  email_smtp_port: 587
  email_username: "your_email@qq.com"  # 从环境变量读取
  email_password: "your_authorization_code"  # 从环境变量读取
```

## 💬 Slack 通知配置

### 创建 Slack Webhook

1. **访问 Slack App 目录**：
   - 打开 [Slack API](https://api.slack.com/apps)
   - 点击"Create New App"

2. **选择创建方式**：
   - 选择"From scratch"
   - 输入应用名称："GitHub Sentinel"
   - 选择您的工作区

3. **配置 Incoming Webhooks**：
   - 在左侧菜单选择"Incoming Webhooks"
   - 开启"Activate Incoming Webhooks"
   - 点击"Add New Webhook to Workspace"
   - 选择要发送消息的频道
   - 复制生成的 Webhook URL

4. **配置 GitHub Sentinel**：
```yaml
notification:
  slack_enabled: true
  slack_webhook_url: "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
  slack_channel: "#github-updates"  # 可选，覆盖默认频道
```

### Slack 消息格式定制

您可以自定义 Slack 消息的格式，系统支持 Slack 的富文本格式：

```yaml
notification:
  slack_enabled: true
  slack_webhook_url: "your_webhook_url"
  slack_channel: "#github-updates"
  slack_username: "GitHub Sentinel"  # 可选：自定义发送者名称
  slack_icon_emoji: ":robot_face:"   # 可选：自定义头像
```

### 多个 Slack 工作区

如果需要同时发送到多个 Slack 工作区，可以配置多个 Webhook：

```yaml
notification:
  slack_enabled: true
  slack_webhooks:  # 使用数组形式
    - url: "https://hooks.slack.com/services/TEAM1/..."
      channel: "#team1-updates"
    - url: "https://hooks.slack.com/services/TEAM2/..."
      channel: "#team2-updates"
```

## 🔗 Webhook 通知配置

### 基础配置

```yaml
notification:
  webhook_enabled: true
  webhook_urls:
    - "https://your-api.example.com/github-webhook"
    - "https://another-service.com/notifications"
```

### Webhook 请求格式

GitHub Sentinel 会向您的 Webhook URL 发送 POST 请求，包含以下信息：

```json
{
  "timestamp": "2024-01-15T08:00:00Z",
  "event_type": "daily_report",
  "source": "github_sentinel",
  "version": "1.0.0",
  "data": {
    "report_id": 123,
    "user_id": 1,
    "repositories": [
      {
        "name": "owner/repo",
        "activities_count": 15,
        "summary": "AI generated summary"
      }
    ],
    "summary": "Overall summary of activities",
    "period": {
      "start": "2024-01-14T08:00:00Z",
      "end": "2024-01-15T08:00:00Z"
    }
  }
}
```

### 自定义 Webhook 头部

```yaml
notification:
  webhook_enabled: true
  webhook_urls:
    - url: "https://your-api.example.com/webhook"
      headers:
        Authorization: "Bearer your_token"
        Content-Type: "application/json"
        X-Source: "GitHub-Sentinel"
```

### Webhook 安全性

#### 1. 使用签名验证

```yaml
notification:
  webhook_enabled: true
  webhook_secret: "your_webhook_secret"  # 用于生成签名
```

GitHub Sentinel 会在请求头中添加签名：
```
X-GitHub-Sentinel-Signature: sha256=hash_value
```

#### 2. IP 白名单

确保您的 Webhook 端点只接受来自 GitHub Sentinel 服务器的请求。

#### 3. HTTPS 强制

生产环境中务必使用 HTTPS URL。

### 常见 Webhook 集成

#### Discord Webhook
```yaml
notification:
  webhook_enabled: true
  webhook_urls:
    - "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
```

#### Microsoft Teams
```yaml
notification:
  webhook_enabled: true
  webhook_urls:
    - "https://your-tenant.webhook.office.com/webhookb2/YOUR_WEBHOOK_URL"
```

#### 钉钉机器人
```yaml
notification:
  webhook_enabled: true
  webhook_urls:
    - "https://oapi.dingtalk.com/robot/send?access_token=YOUR_ACCESS_TOKEN"
```

## 🎨 通知模板自定义

### 邮件模板

创建自定义邮件模板：

```html
<!-- templates/email/daily_report.html -->
<!DOCTYPE html>
<html>
<head>
    <title>GitHub 每日报告</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background-color: #24292e; color: white; padding: 20px; }
        .content { padding: 20px; }
        .repo-section { margin-bottom: 30px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 GitHub 每日报告</h1>
        <p>{{ date }}</p>
    </div>
    <div class="content">
        {% for repo in repositories %}
        <div class="repo-section">
            <h2>{{ repo.name }}</h2>
            <p>{{ repo.summary }}</p>
            <ul>
                {% for activity in repo.activities %}
                <li>{{ activity.title }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endfor %}
    </div>
</body>
</html>
```

### Slack 消息模板

```yaml
# 配置文件中指定模板
notification:
  slack_enabled: true
  slack_template: |
    :rocket: *GitHub 每日报告* - {{ date }}
    
    {% for repo in repositories %}
    *{{ repo.name }}*
    • 活动数量: {{ repo.activities_count }}
    • 摘要: {{ repo.summary[:100] }}...
    
    {% endfor %}
    
    详细报告: {{ report_url }}
```

## 🔧 故障排除

### 邮件发送失败

1. **SMTP 认证错误**：
   ```
   Error: (535, 'Authentication failed')
   ```
   - 检查用户名和密码
   - 确认使用应用专用密码（Gmail）
   - 验证 SMTP 服务器地址和端口

2. **连接超时**：
   ```
   Error: Connection timed out
   ```
   - 检查网络连接
   - 验证防火墙设置
   - 尝试不同的端口（587, 465, 25）

3. **SSL/TLS 错误**：
   ```
   Error: SSL handshake failed
   ```
   - 确认端口配置正确
   - 尝试不同的加密方式

### Slack 通知失败

1. **Webhook URL 无效**：
   - 重新生成 Webhook URL
   - 检查工作区权限

2. **消息格式错误**：
   - 验证 JSON 格式
   - 检查特殊字符转义

### Webhook 调试

1. **启用详细日志**：
```yaml
debug: true
log_level: "DEBUG"
```

2. **使用测试端点**：
   - 使用 [webhook.site](https://webhook.site) 测试
   - 检查请求头和数据格式

3. **网络连通性测试**：
```bash
curl -X POST https://your-webhook-url.com/test \
  -H "Content-Type: application/json" \
  -d '{"test": "message"}'
```

### 常见错误码

| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| 401 | 认证失败 | 检查凭据和权限 |
| 403 | 权限不足 | 更新 API 权限 |
| 429 | 请求过于频繁 | 实施速率限制 |
| 500 | 服务器错误 | 检查目标服务状态 |

## 📊 通知监控

### 查看通知状态

```bash
# 查看通知相关日志
grep -i "notification" logs/github_sentinel.log

# 查看失败的通知
grep -i "notification.*failed" logs/github_sentinel.log
```

### 通知统计

访问 API 端点查看通知统计：
```bash
curl http://localhost:8000/api/v1/notifications/stats
```

### 重试机制

系统会自动重试失败的通知：

```yaml
notification:
  retry_attempts: 3
  retry_delay: 60  # 秒
  max_retry_delay: 300  # 最大延迟
```

---

[返回配置指南首页](configuration-guide.md) | [API 参考文档](api-reference.md) 