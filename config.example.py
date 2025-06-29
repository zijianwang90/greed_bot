"""
主配置文件模板
此文件包含经常需要调整的业务配置
不经常变动的配置（如Telegram Token）请在 config_local.py 中设置
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ==================== 导入本地配置 ====================
try:
    from config_local import (
        TELEGRAM_BOT_TOKEN, ADMIN_USER_ID, BOT_USERNAME,
        DATABASE_URL, DB_POOL_SIZE, DB_MAX_OVERFLOW,
        DEFAULT_NOTIFICATION_TIME, DEFAULT_TIMEZONE,
        USE_WEBHOOK, WEBHOOK_URL, WEBHOOK_PORT, WEBHOOK_LISTEN,
        WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV,
        LOG_LEVEL, LOG_FILE, LOG_TO_CONSOLE,
        ENABLE_ERROR_REPORTING, ERROR_WEBHOOK_URL,
        DEBUG, DEV_MODE, TEST_MODE
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
    ENABLE_ERROR_REPORTING = False
    ERROR_WEBHOOK_URL = ""
    DEBUG = False
    DEV_MODE = False
    TEST_MODE = False

# ==================== 定时任务设置 ====================

# How often to update market data (minutes)
DATA_UPDATE_INTERVAL = int(os.getenv("DATA_UPDATE_INTERVAL", "60"))

# How often to check for notifications to send (minutes)
NOTIFICATION_CHECK_INTERVAL = int(os.getenv("NOTIFICATION_CHECK_INTERVAL", "1"))

# ==================== MARKET DATA SETTINGS ====================

# CNN Fear & Greed Index API
CNN_FEAR_GREED_API = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"

# Backup data source (fallback API)
BACKUP_DATA_SOURCE = os.getenv("BACKUP_DATA_SOURCE", "")

# Request timeout (seconds)
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# Maximum retries for failed requests
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Alternative data sources (comma-separated)
ALTERNATIVE_DATA_SOURCES = os.getenv("ALTERNATIVE_DATA_SOURCES", "").split(",")

# How many days of historical data to fetch
HISTORICAL_DAYS = int(os.getenv("HISTORICAL_DAYS", "30"))

# Data source timeout (seconds) - keeping for backward compatibility
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))

# Rate limiting settings
MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))

# ==================== FEATURE SETTINGS ====================

# ==================== 语言设置 ====================

# 默认语言
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")  # en, zh
SUPPORTED_LANGUAGES = ["en", "zh"]

# ==================== 功能开关 ====================

# 启用/禁用功能
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

# ==================== 监控设置 ====================

# 健康检查端点
ENABLE_HEALTH_CHECK = os.getenv("ENABLE_HEALTH_CHECK", "true").lower() == "true"
HEALTH_CHECK_PORT = int(os.getenv("HEALTH_CHECK_PORT", "8080"))

# 指标收集
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "false").lower() == "true"

# ==================== PERFORMANCE SETTINGS ====================

# Connection pool settings
HTTP_POOL_CONNECTIONS = int(os.getenv("HTTP_POOL_CONNECTIONS", "10"))
HTTP_POOL_MAXSIZE = int(os.getenv("HTTP_POOL_MAXSIZE", "10"))

# Cache settings
ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes

# Concurrent processing
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))

# ==================== VALIDATION ====================

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        errors.append("TELEGRAM_BOT_TOKEN is required")
    
    if USE_WEBHOOK and not WEBHOOK_URL:
        errors.append("WEBHOOK_URL is required when USE_WEBHOOK is enabled")
    
    if ADMIN_USER_ID and not str(ADMIN_USER_ID).isdigit():
        errors.append("ADMIN_USER_ID must be a valid Telegram user ID")
    
    if LOG_LEVEL not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        errors.append("LOG_LEVEL must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    
    if DEFAULT_LANGUAGE not in SUPPORTED_LANGUAGES:
        errors.append(f"DEFAULT_LANGUAGE must be one of: {', '.join(SUPPORTED_LANGUAGES)}")
    
    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"- {error}" for error in errors))

# Validate configuration on import
if __name__ != "__main__":
    try:
        validate_config()
    except ValueError as e:
        print(f"Configuration validation failed: {e}")
        print("Please check your config.py file and fix the errors above.")

# ==================== RUNTIME SETTINGS ====================

# Settings that can be modified at runtime
RUNTIME_SETTINGS = {
    "maintenance_mode": False,
    "max_message_length": 4096,
    "default_timeout": 30,
    "retry_attempts": 3,
    "backoff_factor": 2,
} 