"""
Configuration template for CNN Fear & Greed Index Telegram Bot
Copy this file to config.py and fill in your values
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==================== TELEGRAM BOT SETTINGS ====================

# Required: Get this from @BotFather on Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Optional: Your Telegram user ID for admin commands
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", None)

# Bot username (without @)
BOT_USERNAME = os.getenv("BOT_USERNAME", "your_bot_username")

# ==================== DATABASE SETTINGS ====================

# Database URL - SQLite for development, PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")

# Database pool settings (for PostgreSQL)
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))

# ==================== SCHEDULING SETTINGS ====================

# Default notification time (24-hour format)
DEFAULT_NOTIFICATION_TIME = os.getenv("DEFAULT_NOTIFICATION_TIME", "09:00")

# Default timezone
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "UTC")

# How often to update market data (minutes)
DATA_UPDATE_INTERVAL = int(os.getenv("DATA_UPDATE_INTERVAL", "60"))

# How often to check for notifications to send (minutes)
NOTIFICATION_CHECK_INTERVAL = int(os.getenv("NOTIFICATION_CHECK_INTERVAL", "1"))

# ==================== MARKET DATA SETTINGS ====================

# CNN Fear & Greed Index API
CNN_FEAR_GREED_API = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"

# Alternative data sources (comma-separated)
ALTERNATIVE_DATA_SOURCES = os.getenv("ALTERNATIVE_DATA_SOURCES", "").split(",")

# How many days of historical data to fetch
HISTORICAL_DAYS = int(os.getenv("HISTORICAL_DAYS", "30"))

# Data source timeout (seconds)
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))

# Rate limiting settings
MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))

# ==================== FEATURE SETTINGS ====================

# Language settings
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")  # en, zh
SUPPORTED_LANGUAGES = ["en", "zh"]

# Enable/disable features
ENABLE_HISTORICAL_DATA = os.getenv("ENABLE_HISTORICAL_DATA", "true").lower() == "true"
ENABLE_VIX_DATA = os.getenv("ENABLE_VIX_DATA", "true").lower() == "true"
ENABLE_MARKET_INDICATORS = os.getenv("ENABLE_MARKET_INDICATORS", "true").lower() == "true"
ENABLE_CHARTS = os.getenv("ENABLE_CHARTS", "false").lower() == "true"

# Maximum users per bot (0 = unlimited)
MAX_USERS = int(os.getenv("MAX_USERS", "0"))

# ==================== NOTIFICATION SETTINGS ====================

# Message formatting
USE_RICH_FORMATTING = os.getenv("USE_RICH_FORMATTING", "true").lower() == "true"
INCLUDE_EMOJIS = os.getenv("INCLUDE_EMOJIS", "true").lower() == "true"

# Notification content
INCLUDE_ANALYSIS = os.getenv("INCLUDE_ANALYSIS", "true").lower() == "true"
INCLUDE_HISTORICAL_COMPARISON = os.getenv("INCLUDE_HISTORICAL_COMPARISON", "true").lower() == "true"
INCLUDE_TREND_ANALYSIS = os.getenv("INCLUDE_TREND_ANALYSIS", "true").lower() == "true"

# Quiet hours (when not to send notifications)
QUIET_HOURS_START = os.getenv("QUIET_HOURS_START", "22:00")
QUIET_HOURS_END = os.getenv("QUIET_HOURS_END", "07:00")

# ==================== LOGGING SETTINGS ====================

# Logging level
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Log file path
LOG_FILE = os.getenv("LOG_FILE", "bot.log")

# Enable console logging
LOG_TO_CONSOLE = os.getenv("LOG_TO_CONSOLE", "true").lower() == "true"

# Log rotation settings
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "3"))

# ==================== SECURITY SETTINGS ====================

# Enable webhook mode (False for polling)
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() == "true"

# Webhook settings (if enabled)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8443"))
WEBHOOK_LISTEN = os.getenv("WEBHOOK_LISTEN", "0.0.0.0")

# SSL certificate paths (for webhook)
WEBHOOK_SSL_CERT = os.getenv("WEBHOOK_SSL_CERT", "")
WEBHOOK_SSL_PRIV = os.getenv("WEBHOOK_SSL_PRIV", "")

# Rate limiting
ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "20"))

# ==================== DEVELOPMENT SETTINGS ====================

# Debug mode
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Enable development features
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

# Test mode (don't send actual notifications)
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

# Mock data for testing
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

# ==================== MONITORING SETTINGS ====================

# Health check endpoint
ENABLE_HEALTH_CHECK = os.getenv("ENABLE_HEALTH_CHECK", "true").lower() == "true"
HEALTH_CHECK_PORT = int(os.getenv("HEALTH_CHECK_PORT", "8080"))

# Metrics collection
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "false").lower() == "true"

# Error reporting
ENABLE_ERROR_REPORTING = os.getenv("ENABLE_ERROR_REPORTING", "false").lower() == "true"
ERROR_WEBHOOK_URL = os.getenv("ERROR_WEBHOOK_URL", "")

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