# GitHub Sentinel 快速启动指南

## 🚨 配置文件问题解决方案

如果遇到"配置文件不存在"的错误，请按以下步骤操作：

### 1. 运行配置测试脚本
```bash
cd D:\GitHubSentinel
python scripts/fix_and_test.py
```

### 2. 手动检查配置文件
```bash
# 检查配置文件是否存在
dir config
# 应该看到 config.yaml 和/或 config.yml
```

### 3. 如果仍有问题，手动切换到正确目录
```bash
# 确保在项目根目录
cd D:\GitHubSentinel
# 然后运行脚本
python scripts/generate_langchain_report.py
```

## 问题修复说明

已修复的问题：
1. ✅ 配置文件路径问题 - 现在同时支持 `config.yml` 和 `config.yaml`
2. ✅ SQLite数据库连接池参数问题 - 修复了不兼容的参数
3. ✅ 前端结构完善 - 创建了完整的Vue3前端
4. ✅ 配置加载逻辑优化 - 支持多种配置文件格式

## 快速启动

### 1. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
cd ..
```

### 2. 验证配置

```bash
# 运行配置测试（推荐）
python scripts/fix_and_test.py

# 或者手动检查
python scripts/test_config.py
```

### 3. 启动项目

#### 方法1：使用启动脚本
```bash
python scripts/start_dev.py
```

#### 方法2：手动启动

**启动后端：**
```bash
# 初始化数据库
python main.py init

# 启动后端服务
python main.py server
```

**启动前端：**
```bash
cd frontend
npm run dev
```

### 4. 访问应用

- 前端界面: http://localhost:4000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 功能测试

### 测试GitHub数据收集
```bash
# 先运行配置测试
python scripts/fix_and_test.py

# 然后生成报告
python scripts/generate_langchain_report.py
```

### 主要功能页面
- **首页**: 项目介绍和功能展示
- **仪表板**: 系统概览和统计数据
- **订阅管理**: 管理GitHub仓库订阅
- **报告管理**: 查看和管理生成的报告
- **系统设置**: 配置GitHub Token、AI服务等

## 配置说明

主要配置项：
- `github.token`: GitHub Personal Access Token（必需）
- `ai.openai_api_key`: OpenAI API密钥（AI功能必需）
- `notification.email_*`: 邮件通知配置（可选）

配置文件位置：
- 优先使用：`config/config.yml`
- 备选使用：`config/config.yaml`

## 故障排除

### 1. 配置文件路径错误
```bash
# 运行修复脚本
python scripts/fix_and_test.py
```

### 2. SQLite错误
确保已修复database.py中的连接池参数问题，SQLite不支持pool_size参数。

### 3. 前端访问错误
确保已安装前端依赖并正确配置了Vue Router。

### 4. PyYAML依赖错误
```bash
pip install PyYAML
```

### 5. 工作目录错误
确保在项目根目录 `D:\GitHubSentinel` 中运行脚本。

## 开发模式

- 后端端口: 8000
- 前端端口: 4000
- 前端代理: /api 请求会转发到后端

## 快速验证

运行这个命令来验证一切是否正常：
```bash
python scripts/fix_and_test.py
```

如果看到"🎉 所有测试通过!"，说明配置正确，可以开始使用了！

## 下一步

1. 配置你的GitHub Token
2. 配置OpenAI API Key（如果使用AI功能）
3. 添加仓库订阅
4. 生成第一个报告

项目现在应该可以正常运行了！ 