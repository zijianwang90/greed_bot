"""
本地配置文件模板 - 敏感数据配置
复制此文件为 config_local.py 并填入您的实际配置值

此文件包含敏感信息，不应提交到版本控制系统
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ==================== TELEGRAM BOT 设置 ====================

# 必填：从 @BotFather 获取的 Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# 可选：管理员用户ID，用于管理命令
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", None)

# Bot 用户名（不含@符号）
BOT_USERNAME = os.getenv("BOT_USERNAME", "your_bot_username")

# ==================== 数据库配置 ====================

# 数据库连接URL
# 开发环境使用 SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")

# 生产环境使用 PostgreSQL 示例
# DATABASE_URL = "postgresql://username:password@localhost:5432/greed_bot"

# 数据库连接池设置（PostgreSQL）
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))

# ==================== 通知设置 ====================

# 默认通知时间（24小时制）
DEFAULT_NOTIFICATION_TIME = os.getenv("DEFAULT_NOTIFICATION_TIME", "09:00")

# 默认时区
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "UTC")

# ==================== WEBHOOK 设置（可选）====================

# 是否启用 Webhook 模式（False 为轮询模式，推荐用于VPS）
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() == "true"

# Webhook 设置（仅在启用 Webhook 时需要）
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8443"))
WEBHOOK_LISTEN = os.getenv("WEBHOOK_LISTEN", "0.0.0.0")

# SSL 证书路径（用于 webhook，可选）
WEBHOOK_SSL_CERT = os.getenv("WEBHOOK_SSL_CERT", "")
WEBHOOK_SSL_PRIV = os.getenv("WEBHOOK_SSL_PRIV", "")

# ==================== 日志设置 ====================

# 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 日志文件路径
LOG_FILE = os.getenv("LOG_FILE", "bot.log")

# 是否输出到控制台
LOG_TO_CONSOLE = os.getenv("LOG_TO_CONSOLE", "true").lower() == "true"

# ==================== 开发设置 ====================

# 调试模式（开发时启用）
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# 测试模式（不发送实际通知）
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

# ==================== 配置说明 ====================
"""
配置说明：

1. TELEGRAM_BOT_TOKEN: 
   - 从 @BotFather 获取
   - 格式: 123456789:ABCdefGHIjklMNOpqrSTUvwxyz

2. ADMIN_USER_ID:
   - 您的 Telegram 用户 ID
   - 可通过 @userinfobot 获取

3. DATABASE_URL:
   - SQLite: sqlite:///bot.db
   - PostgreSQL: postgresql://user:pass@host:port/dbname

4. WEBHOOK vs POLLING:
   - VPS 部署推荐使用 POLLING (USE_WEBHOOK = False)
   - 有公网 IP 和域名时可使用 WEBHOOK

5. 环境变量:
   - 可以在 .env 文件中设置
   - 或直接在系统环境变量中设置
""" 