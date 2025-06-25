"""
本地配置文件模板
复制此文件为 config_local.py 并填入您的实际配置值
此文件包含不经常变动的配置，如 Telegram Bot Token 等
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ==================== TELEGRAM BOT SETTINGS ====================

# 必填：从 @BotFather 获取的 Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# 可选：管理员用户ID，用于管理命令
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", None)

# Bot 用户名（不含@符号）
BOT_USERNAME = os.getenv("BOT_USERNAME", "your_bot_username")

# ==================== 数据库配置 ====================

# 数据库连接URL - 生产环境建议使用PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")

# PostgreSQL 示例（如果使用）
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

# 是否启用 Webhook 模式（False 为轮询模式）
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() == "true"

# Webhook 设置（如果启用）
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8443"))
WEBHOOK_LISTEN = os.getenv("WEBHOOK_LISTEN", "0.0.0.0")

# SSL 证书路径（用于 webhook）
WEBHOOK_SSL_CERT = os.getenv("WEBHOOK_SSL_CERT", "")
WEBHOOK_SSL_PRIV = os.getenv("WEBHOOK_SSL_PRIV", "")

# ==================== 日志设置 ====================

# 日志级别
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 日志文件路径
LOG_FILE = os.getenv("LOG_FILE", "bot.log")

# 是否输出到控制台
LOG_TO_CONSOLE = os.getenv("LOG_TO_CONSOLE", "true").lower() == "true"

# ==================== 错误报告设置 ====================

# 是否启用错误报告
ENABLE_ERROR_REPORTING = os.getenv("ENABLE_ERROR_REPORTING", "false").lower() == "true"

# 错误报告 Webhook URL（如监控服务）
ERROR_WEBHOOK_URL = os.getenv("ERROR_WEBHOOK_URL", "")

# ==================== 开发模式设置 ====================

# 调试模式
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# 开发模式（启用开发功能）
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

# 测试模式（不发送实际通知）
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true" 