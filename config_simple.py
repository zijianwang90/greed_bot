"""
Simplified Configuration for CNN Fear & Greed Index Telegram Bot
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==================== ESSENTIAL SETTINGS ====================

# Required: Get this from @BotFather on Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Optional: Your Telegram user ID for admin commands
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", None)

# Database URL - SQLite for simplicity
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")

# ==================== BASIC SETTINGS ====================

# Default notification time (24-hour format)
DEFAULT_NOTIFICATION_TIME = os.getenv("DEFAULT_NOTIFICATION_TIME", "09:00")

# Default timezone
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "UTC")

# Language settings
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")  # en, zh
SUPPORTED_LANGUAGES = ["en", "zh"]

# ==================== DATA SOURCES ====================

# CNN Fear & Greed Index API
CNN_FEAR_GREED_API = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"

# Backup data source
BACKUP_DATA_SOURCE = "https://alternative.me/crypto/fear-and-greed-index/"

# Request timeout (seconds)
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# Max retries for API calls
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# ==================== LOGGING SETTINGS ====================

# Logging level
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Log to console
LOG_TO_CONSOLE = os.getenv("LOG_TO_CONSOLE", "true").lower() == "true"

# Log file (optional)
LOG_FILE = os.getenv("LOG_FILE", "")

# Log rotation settings
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "3"))

# ==================== FEATURE FLAGS ====================

# Use webhook instead of polling (False for VPS polling)
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() == "true"

# Webhook settings (only if USE_WEBHOOK is True)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8443"))
WEBHOOK_LISTEN = os.getenv("WEBHOOK_LISTEN", "0.0.0.0")
WEBHOOK_SSL_CERT = os.getenv("WEBHOOK_SSL_CERT", "")
WEBHOOK_SSL_PRIV = os.getenv("WEBHOOK_SSL_PRIV", "")

# Development settings
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

# ==================== VALIDATION ====================

def validate_config():
    """Validate essential configuration settings"""
    errors = []
    
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        errors.append("TELEGRAM_BOT_TOKEN is required")
    
    if USE_WEBHOOK and not WEBHOOK_URL:
        errors.append("WEBHOOK_URL is required when USE_WEBHOOK is enabled")
    
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