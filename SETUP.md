# 快速设置指南

## 1. 配置文件设置

### 创建本地配置文件
```bash
# 复制配置模板
cp config_local.example.py config_local.py
```

### 编辑配置文件
```bash
# 编辑本地配置
nano config_local.py
```

必须配置的项目：
- `TELEGRAM_BOT_TOKEN`: 从 @BotFather 获取
- `ADMIN_USER_ID`: 您的 Telegram 用户 ID（可选，但推荐）

## 2. 获取 Telegram Bot Token

1. 在 Telegram 中找到 @BotFather
2. 发送 `/newbot` 命令
3. 按提示设置机器人名称和用户名
4. 复制获得的 Token 到 `config_local.py`

## 3. 获取用户 ID（可选）

1. 在 Telegram 中找到 @userinfobot
2. 发送任意消息
3. 复制您的用户 ID 到 `config_local.py` 的 `ADMIN_USER_ID`

## 4. 数据库配置

### 开发环境（默认）
```python
DATABASE_URL = "sqlite:///bot.db"
```

### 生产环境（PostgreSQL）
```python
DATABASE_URL = "postgresql://username:password@localhost:5432/greed_bot"
```

## 5. 部署模式

### VPS 部署（推荐）
```python
USE_WEBHOOK = False  # 使用轮询模式
```

### 服务器部署（有公网 IP）
```python
USE_WEBHOOK = True
WEBHOOK_URL = "https://yourdomain.com/webhook"
```

## 6. 启动机器人

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python migrate_db.py

# 启动机器人
python main.py
```

## 配置文件说明

- `config_local.py`: 敏感配置（Token、数据库等）**不要提交到 Git**
- `config.py`: 业务配置（功能开关、通知设置等）
- `.env`: 环境变量文件（可选）

## 环境变量

也可以通过环境变量设置：

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export ADMIN_USER_ID="your_user_id"
export LOG_LEVEL="INFO"
```

或创建 `.env` 文件：
```
TELEGRAM_BOT_TOKEN=your_bot_token
ADMIN_USER_ID=your_user_id
LOG_LEVEL=INFO
``` 