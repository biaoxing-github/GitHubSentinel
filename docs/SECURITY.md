# 安全指南

## 🔒 敏感信息管理

### 配置文件安全

**✅ 正确做法：**
- 使用 `config/config.example.yaml` 作为模板
- 复制为 `config/config.yaml` 并填入真实配置
- 确保 `config/config.yaml` 在 `.gitignore` 中

**❌ 错误做法：**
- 直接在代码中硬编码 API 密钥
- 提交包含真实密钥的配置文件
- 在公开仓库中暴露敏感信息

### 必需的敏感信息

1. **GitHub Token**
   - 获取：GitHub Settings > Developer settings > Personal access tokens
   - 权限：`repo`, `read:user`, `read:org`
   - 配置：`github.token`

2. **应用密钥**
   - 生成：使用随机字符串生成器
   - 用途：JWT 签名和加密
   - 配置：`secret_key`

3. **邮件密码**（可选）
   - Gmail：使用应用专用密码
   - QQ/163：使用授权码
   - 配置：`notification.email_password`

4. **OpenAI API Key**（可选）
   - 获取：https://platform.openai.com/api-keys
   - 用途：AI 分析功能
   - 配置：`ai.openai_api_key`

## 🛡️ 安全最佳实践

### 1. 环境变量

推荐使用环境变量管理敏感信息：

```bash
# 设置环境变量
export GITHUB_TOKEN="your_token_here"
export SECRET_KEY="your_secret_key"
export OPENAI_API_KEY="your_openai_key"
export EMAIL_PASSWORD="your_email_password"
```

### 2. 文件权限

```bash
# 设置配置文件权限（仅所有者可读写）
chmod 600 config/config.yaml

# 设置脚本执行权限
chmod +x scripts/clean_sensitive_data.py
```

### 3. Git 安全

```bash
# 检查是否有敏感文件被跟踪
git status

# 如果意外添加了敏感文件，从暂存区移除
git reset HEAD config/config.yaml

# 从历史记录中完全删除敏感文件
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch config/config.yaml' \
  --prune-empty --tag-name-filter cat -- --all
```

## 🧹 清理敏感信息

### 自动清理脚本

运行清理脚本来移除所有敏感信息：

```bash
python scripts/clean_sensitive_data.py
```

该脚本会：
- 删除包含真实密钥的配置文件
- 清理日志文件中的敏感信息
- 移除临时文件和缓存
- 验证 `.gitignore` 配置

### 手动清理检查清单

**配置文件：**
- [ ] 删除 `config/config.yaml`
- [ ] 删除 `config/config.yml`
- [ ] 保留 `config/config.example.yaml`

**日志文件：**
- [ ] 删除 `logs/*.log`
- [ ] 删除根目录下的 `*.log` 文件

**数据库文件：**
- [ ] 删除 `github_sentinel.db`
- [ ] 删除 `*.sqlite` 文件

**临时文件：**
- [ ] 删除 `__pycache__/` 目录
- [ ] 删除 `node_modules/` 目录
- [ ] 删除 `frontend/dist/` 目录

## 🔍 安全检查

### 提交前检查

```bash
# 1. 检查暂存区文件
git diff --cached --name-only

# 2. 搜索敏感信息
grep -r "github_pat_" . --exclude-dir=.git
grep -r "sk-proj-" . --exclude-dir=.git
grep -r "@qq.com\|@gmail.com" . --exclude-dir=.git

# 3. 验证 .gitignore
cat .gitignore | grep -E "(config\.yaml|\.log|\.db)"
```

### 定期安全审计

1. **每月检查：**
   - 轮换 GitHub Token
   - 检查 API 使用情况
   - 更新依赖包

2. **每季度检查：**
   - 审查访问权限
   - 更新密码和密钥
   - 检查日志文件

## 🚨 安全事件响应

### 如果密钥泄露

1. **立即行动：**
   ```bash
   # 撤销 GitHub Token
   # 访问 GitHub Settings > Developer settings > Personal access tokens
   # 点击 "Delete" 删除泄露的 token
   
   # 生成新的 token
   # 更新本地配置文件
   ```

2. **清理历史记录：**
   ```bash
   # 从 Git 历史中移除敏感文件
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch path/to/sensitive/file' \
     --prune-empty --tag-name-filter cat -- --all
   
   # 强制推送（谨慎操作）
   git push origin --force --all
   ```

3. **通知相关人员：**
   - 通知团队成员
   - 更新文档
   - 记录事件日志

## 📋 部署安全

### 生产环境配置

```yaml
# 生产环境安全配置
debug: false
log_level: "WARNING"

# 使用强密钥
secret_key: "use-a-strong-random-key-here"

# 数据库安全
database:
  url: "postgresql+asyncpg://user:password@localhost:5432/github_sentinel"
  
# 启用 HTTPS
web:
  host: "0.0.0.0"
  port: 8000
  ssl_keyfile: "/path/to/ssl/key.pem"
  ssl_certfile: "/path/to/ssl/cert.pem"
```

### 网络安全

- 使用防火墙限制访问
- 启用 HTTPS/TLS
- 定期更新系统和依赖
- 监控异常访问

## 📞 报告安全问题

如果发现安全漏洞，请通过以下方式报告：

- 邮箱：security@your-domain.com
- 私有 Issue：在 GitHub 上创建私有安全报告
- 加密通信：使用 PGP 加密敏感信息

**请勿在公开 Issue 中报告安全问题。** 