# 配置说明

## 快速开始

1. **复制配置文件**
   ```bash
   cp config/config.example.yaml config/config.yaml
   ```

2. **编辑配置文件**
   ```bash
   # 使用您喜欢的编辑器
   nano config/config.yaml
   # 或
   vim config/config.yaml
   ```

3. **必需配置项**
   - `github.token`: GitHub Personal Access Token
   - `secret_key`: 应用密钥（用于JWT签名）

## 配置项详解

### GitHub Token 获取

1. 访问 [GitHub Settings](https://github.com/settings/tokens)
2. 点击 "Developer settings" > "Personal access tokens" > "Tokens (classic)"
3. 点击 "Generate new token (classic)"
4. 设置过期时间和权限：
   - `repo`: 访问私有仓库
   - `read:user`: 读取用户信息
   - `read:org`: 读取组织信息
5. 复制生成的 token 到配置文件

### 邮件配置

#### Gmail 配置
```yaml
email_smtp_host: "smtp.gmail.com"
email_smtp_port: 587
email_username: "your_email@gmail.com"
email_password: "your_app_password"  # 使用应用专用密码
```

**获取 Gmail 应用密码：**
1. 启用两步验证
2. 访问 [应用密码设置](https://myaccount.google.com/apppasswords)
3. 生成应用密码并使用该密码

#### QQ 邮箱配置
```yaml
email_smtp_host: "smtp.qq.com"
email_smtp_port: 587
email_username: "your_email@qq.com"
email_password: "your_authorization_code"  # 使用授权码
```

#### 163 邮箱配置
```yaml
email_smtp_host: "smtp.163.com"
email_smtp_port: 587
email_username: "your_email@163.com"
email_password: "your_authorization_code"  # 使用授权码
```

### Slack 配置

1. 在 Slack 工作区创建应用
2. 启用 Incoming Webhooks
3. 创建 Webhook URL
4. 将 URL 复制到配置文件

### 数据库配置

#### SQLite（默认，推荐用于开发）
```yaml
database:
  url: "sqlite+aiosqlite:///./github_sentinel.db"
```

#### PostgreSQL（推荐用于生产）
```yaml
database:
  url: "postgresql+asyncpg://username:password@localhost:5432/github_sentinel"
```

### AI 服务配置

#### OpenAI
1. 访问 [OpenAI API Keys](https://platform.openai.com/api-keys)
2. 创建新的 API Key
3. 复制到配置文件

#### Ollama（本地部署）
1. 安装 Ollama
2. 下载模型：`ollama pull llama2`
3. 启动服务：`ollama serve`

## 安全最佳实践

### 1. 密钥管理
- 使用强随机密钥作为 `secret_key`
- 定期轮换 API 密钥
- 不要在代码中硬编码密钥

### 2. 文件权限
```bash
# 设置配置文件权限（仅所有者可读写）
chmod 600 config/config.yaml
```

### 3. 环境变量（可选）
您也可以使用环境变量覆盖配置：
```bash
export GITHUB_TOKEN="your_token_here"
export OPENAI_API_KEY="your_key_here"
export SECRET_KEY="your_secret_key"
```

### 4. 生产环境建议
- 设置 `debug: false`
- 使用 PostgreSQL 数据库
- 启用 Redis 缓存
- 设置适当的日志级别
- 使用 HTTPS

## 故障排除

### 常见问题

1. **GitHub API 限制**
   - 检查 token 权限
   - 确认 API 限制配置

2. **邮件发送失败**
   - 检查 SMTP 设置
   - 确认使用应用密码而非账户密码
   - 检查防火墙设置

3. **数据库连接失败**
   - 检查数据库 URL 格式
   - 确认数据库服务运行状态
   - 检查用户权限

4. **前端无法访问后端**
   - 检查端口配置
   - 确认防火墙设置
   - 检查 CORS 配置

### 日志查看
```bash
# 查看应用日志
tail -f logs/github_sentinel.log

# 查看详细调试信息（设置 debug: true）
```

## 配置验证

启动应用时会自动验证配置：
```bash
python main.py
```

如果配置有误，应用会显示具体的错误信息。 