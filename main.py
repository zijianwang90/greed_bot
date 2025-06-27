#!/usr/bin/env python3
"""
CNN Fear & Greed Index Telegram Bot
Main entry point for the bot application
"""

import sys
import logging
import asyncio
import signal
from datetime import datetime
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application, 
    ApplicationBuilder, 
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

# Import local modules
from bot.handlers import (
    start_handler,
    help_handler,
    current_handler,
    subscribe_handler,
    unsubscribe_handler,
    settings_handler,
    history_handler,
    message_handler,
    button_handler,
    error_handler
)
from bot.scheduler import setup_scheduler
from data.database import init_database
from data.fetcher import DataFetcher

# Try to import config
try:
    import config
except ImportError:
    print("ERROR: config.py not found!")
    print("Please copy config.example.py to config.py and fill in your settings.")
    sys.exit(1)

# Validate configuration
try:
    config.validate_config()
except ValueError as e:
    print(f"Configuration error: {e}")
    sys.exit(1)

# Setup logging
def setup_logging():
    """Configure logging for the application"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper()),
        format=log_format,
        handlers=[]
    )
    
    logger = logging.getLogger(__name__)
    
    # Console handler
    if config.LOG_TO_CONSOLE:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if config.LOG_FILE:
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            config.LOG_FILE,
            maxBytes=config.LOG_MAX_BYTES,
            backupCount=config.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)
    
    # Suppress some verbose logs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    
    return logger

# Initialize logger
logger = setup_logging()

class GreedBot:
    """Main bot application class"""
    
    def __init__(self):
        self.app: Optional[Application] = None
        self.data_fetcher: Optional[DataFetcher] = None
        self.scheduler = None

    def setup_handlers(self):
        """Setup all bot handlers"""
        if not self.app:
            raise RuntimeError("Application not initialized")
        
        # Command handlers
        self.app.add_handler(CommandHandler("start", start_handler))
        self.app.add_handler(CommandHandler("help", help_handler))
        self.app.add_handler(CommandHandler("current", current_handler))
        self.app.add_handler(CommandHandler("subscribe", subscribe_handler))
        self.app.add_handler(CommandHandler("unsubscribe", unsubscribe_handler))
        self.app.add_handler(CommandHandler("settings", settings_handler))
        self.app.add_handler(CommandHandler("history", history_handler))
        
        # Callback query handler for inline keyboards
        self.app.add_handler(CallbackQueryHandler(button_handler))
        
        # Message handler for text messages
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
        
        # Error handler
        self.app.add_error_handler(error_handler)
        
        logger.info("Bot handlers registered successfully")

    async def run(self):
        """Initializes, runs, and cleans up the bot."""
        
        # 1. Initialization
        logger.info("Initializing CNN Fear & Greed Index Bot...")
        try:
            await init_database()
            self.data_fetcher = DataFetcher()
            self.app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
            self.setup_handlers()
            
            # Setup scheduler
            logger.info("Setting up scheduler...")
            self.scheduler = await setup_scheduler(self.app)
            logger.info("Bot initialization completed successfully!")

        except Exception as e:
            logger.critical(f"Bot failed to initialize: {e}")
            raise

        # 2. Running Phase
        if self.scheduler:
            await self.scheduler.start()
            logger.info("Scheduler started.")

        logger.info("Starting polling mode...")
        await self.app.run_polling(
            allowed_updates=Update.ALL_TYPES, 
            drop_pending_updates=True
        )

        # 3. Cleanup Phase (after run_polling exits)
        if self.scheduler:
            self.scheduler.stop()
            logger.info("Scheduler stopped.")
        
        logger.info("Bot shutdown complete.")


async def main():
    """Main application entry point"""
    logger.info("=" * 50)
    logger.info("CNN Fear & Greed Index Telegram Bot")
    logger.info("=" * 50)
    logger.info(f"Starting at {datetime.now()}")
    logger.info(f"Debug mode: {config.DEBUG}")
    logger.info(f"Test mode: {config.TEST_MODE}")
    logger.info(f"Language: {config.DEFAULT_LANGUAGE}")
    
    bot = GreedBot()
    try:
        await bot.run()
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # The library's run_polling() handles signals gracefully.
    # No custom signal handlers needed.
    try:
        # Use get_event_loop() instead of asyncio.run() to avoid conflicts
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user.")
    except Exception as e:
        logger.critical(f"Fatal error in top-level execution: {e}")
        sys.exit(1) 