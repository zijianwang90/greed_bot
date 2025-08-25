"""
CNN Fear & Greed Index Telegram Bot - 主配置文件
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ==================== 导入本地配置 ====================
try:
    from config_local import (
        TELEGRAM_BOT_TOKEN, 
        ADMIN_USER_ID, 
        BOT_USERNAME,
        DATABASE_URL, 
        DB_POOL_SIZE, 
        DB_MAX_OVERFLOW,
        DEFAULT_NOTIFICATION_TIME, 
        DEFAULT_TIMEZONE,
        USE_WEBHOOK, 
        WEBHOOK_URL, 
        WEBHOOK_PORT, 
        WEBHOOK_LISTEN,
        WEBHOOK_SSL_CERT, 
        WEBHOOK_SSL_PRIV,
        LOG_LEVEL, 
        LOG_FILE, 
        LOG_TO_CONSOLE,
        DEBUG, 
        TEST_MODE
    )
except ImportError:
    print("⚠️  警告: 未找到 config_local.py 文件")
    print("📋 请复制 config_local.example.py 为 config_local.py 并配置您的设置")
    
    # 提供默认值以防导入失败
    TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    ADMIN_USER_ID = None
    BOT_USERNAME = "your_bot_username"
    DATABASE_URL = "sqlite:///bot.db"
    DB_POOL_SIZE = 10
    DB_MAX_OVERFLOW = 20
    DEFAULT_NOTIFICATION_TIME = "09:00"
    DEFAULT_TIMEZONE = "UTC"
    USE_WEBHOOK = False
    WEBHOOK_URL = ""
    WEBHOOK_PORT = 8443
    WEBHOOK_LISTEN = "0.0.0.0"
    WEBHOOK_SSL_CERT = ""
    WEBHOOK_SSL_PRIV = ""
    LOG_LEVEL = "INFO"
    LOG_FILE = "bot.log"
    LOG_TO_CONSOLE = True
    DEBUG = False
    TEST_MODE = False

# ==================== 定时任务设置 ====================

# 数据更新间隔（分钟）
DATA_UPDATE_INTERVAL = int(os.getenv("DATA_UPDATE_INTERVAL", "60"))

# 通知检查间隔（分钟）
NOTIFICATION_CHECK_INTERVAL = int(os.getenv("NOTIFICATION_CHECK_INTERVAL", "1"))

# ==================== 缓存设置 ====================

# 缓存超时时间（分钟）
CACHE_TIMEOUT_MINUTES = int(os.getenv("CACHE_TIMEOUT_MINUTES", "30"))

# 备用缓存超时时间（分钟，当API失败时使用）
FALLBACK_CACHE_TIMEOUT_MINUTES = int(os.getenv("FALLBACK_CACHE_TIMEOUT_MINUTES", "180"))

# 缓存清理周期（天）
CACHE_CLEANUP_DAYS = int(os.getenv("CACHE_CLEANUP_DAYS", "30"))

# ==================== 市场数据配置 ====================

# CNN Fear & Greed Index API
CNN_FEAR_GREED_API = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"

# 备用数据源 - Alternative.me API
BACKUP_DATA_SOURCE = os.getenv("BACKUP_DATA_SOURCE", "https://api.alternative.me/fng/")

# 请求超时（秒）
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# 最大重试次数
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# 历史数据天数
HISTORICAL_DAYS = int(os.getenv("HISTORICAL_DAYS", "30"))

# ==================== 语言设置 ====================

# 默认语言
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")  # en, zh
SUPPORTED_LANGUAGES = ["en", "zh"]

# ==================== 功能开关 ====================

# 启用功能
ENABLE_HISTORICAL_DATA = os.getenv("ENABLE_HISTORICAL_DATA", "true").lower() == "true"
ENABLE_VIX_DATA = os.getenv("ENABLE_VIX_DATA", "true").lower() == "true"
ENABLE_MARKET_INDICATORS = os.getenv("ENABLE_MARKET_INDICATORS", "true").lower() == "true"
ENABLE_CHARTS = os.getenv("ENABLE_CHARTS", "false").lower() == "true"

# 最大用户数限制（0 = 无限制）
MAX_USERS = int(os.getenv("MAX_USERS", "0"))

# ==================== 通知内容设置 ====================

# 消息格式化
USE_RICH_FORMATTING = os.getenv("USE_RICH_FORMATTING", "true").lower() == "true"
INCLUDE_EMOJIS = os.getenv("INCLUDE_EMOJIS", "true").lower() == "true"

# 通知内容
INCLUDE_ANALYSIS = os.getenv("INCLUDE_ANALYSIS", "true").lower() == "true"
INCLUDE_HISTORICAL_COMPARISON = os.getenv("INCLUDE_HISTORICAL_COMPARISON", "true").lower() == "true"
INCLUDE_TREND_ANALYSIS = os.getenv("INCLUDE_TREND_ANALYSIS", "true").lower() == "true"

# 静默时段（不发送通知的时间）
QUIET_HOURS_START = os.getenv("QUIET_HOURS_START", "22:00")
QUIET_HOURS_END = os.getenv("QUIET_HOURS_END", "07:00")

# ==================== 日志配置 ====================

# 日志轮转设置
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "3"))

# ==================== 安全设置 ====================

# 速率限制
ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # 秒
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "20"))

# ==================== 开发设置 ====================

# 使用模拟数据进行测试
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

# 开发模式
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

# ==================== 监控设置 ====================

# 健康检查
ENABLE_HEALTH_CHECK = os.getenv("ENABLE_HEALTH_CHECK", "true").lower() == "true"
HEALTH_CHECK_PORT = int(os.getenv("HEALTH_CHECK_PORT", "8080"))

# 指标收集
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "false").lower() == "true"

# 错误报告
ENABLE_ERROR_REPORTING = os.getenv("ENABLE_ERROR_REPORTING", "false").lower() == "true"
ERROR_WEBHOOK_URL = os.getenv("ERROR_WEBHOOK_URL", "")

# ==================== 性能设置 ====================

# HTTP连接池设置
HTTP_POOL_CONNECTIONS = int(os.getenv("HTTP_POOL_CONNECTIONS", "10"))
HTTP_POOL_MAXSIZE = int(os.getenv("HTTP_POOL_MAXSIZE", "10"))

# 缓存设置
ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5分钟

# 并发处理
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))

# ==================== 配置验证 ====================

def validate_config():
    """验证配置设置"""
    errors = []
    
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        errors.append("TELEGRAM_BOT_TOKEN 是必需的")
    
    if USE_WEBHOOK and not WEBHOOK_URL:
        errors.append("启用 USE_WEBHOOK 时需要 WEBHOOK_URL")
    
    if ADMIN_USER_ID and not str(ADMIN_USER_ID).isdigit():
        errors.append("ADMIN_USER_ID 必须是有效的 Telegram 用户 ID")
    
    if LOG_LEVEL not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        errors.append("LOG_LEVEL 必须是: DEBUG, INFO, WARNING, ERROR, CRITICAL 之一")
    
    if DEFAULT_LANGUAGE not in SUPPORTED_LANGUAGES:
        errors.append(f"DEFAULT_LANGUAGE 必须是: {', '.join(SUPPORTED_LANGUAGES)} 之一")
    
    if errors:
        raise ValueError(f"配置错误:\n" + "\n".join(f"- {error}" for error in errors))

# 导入时验证配置
if __name__ != "__main__":
    try:
        validate_config()
    except ValueError as e:
        print(f"配置验证失败: {e}")
        print("请检查您的配置文件并修复上述错误。")

# ==================== 运行时设置 ====================

# 可在运行时修改的设置
RUNTIME_SETTINGS = {
    "maintenance_mode": False,
    "max_message_length": 4096,
    "default_timeout": 30,
    "retry_attempts": 3,
    "backoff_factor": 2,
} 