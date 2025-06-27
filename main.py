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
        self.is_running = False
        
    async def initialize(self):
        """Initialize bot components"""
        logger.info("Initializing CNN Fear & Greed Index Bot...")
        
        try:
            # Initialize database
            logger.info("Initializing database...")
            await init_database()
            
            # Initialize data fetcher
            logger.info("Initializing data fetcher...")
            self.data_fetcher = DataFetcher()
            
            # Create application
            logger.info("Creating Telegram application...")
            self.app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
            
            # Add handlers
            self.setup_handlers()
            
            # # Setup scheduler (Temporarily disabled for debugging)
            # logger.info("Setting up scheduler...")
            # self.scheduler = await setup_scheduler(self.app)
            
            logger.info("Bot initialization completed successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise
    
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
    
    async def start(self):
        """Start the bot"""
        if not self.app:
            raise RuntimeError("Bot not initialized")
        
        logger.info("Starting bot...")
        self.is_running = True
        
        try:
            # # Start the scheduler (Temporarily disabled for debugging)
            # if self.scheduler:
            #     await self.scheduler.start()
            #     logger.info("Scheduler started")
            
            # Start the bot
            if config.USE_WEBHOOK:
                logger.info(f"Starting webhook on {config.WEBHOOK_URL}")
                await self.app.run_webhook(
                    listen=config.WEBHOOK_LISTEN,
                    port=config.WEBHOOK_PORT,
                    url_path=config.TELEGRAM_BOT_TOKEN,
                    webhook_url=f"{config.WEBHOOK_URL}/{config.TELEGRAM_BOT_TOKEN}",
                    cert=config.WEBHOOK_SSL_CERT if config.WEBHOOK_SSL_CERT else None,
                    key=config.WEBHOOK_SSL_PRIV if config.WEBHOOK_SSL_PRIV else None
                )
            else:
                logger.info("Starting polling mode")
                # run_polling() is a blocking call that runs the bot until
                # a signal is received. It also calls app.initialize() and app.start().
                await self.app.run_polling(
                    allowed_updates=Update.ALL_TYPES,
                    drop_pending_updates=True
                )
                
        except Exception as e:
            logger.error(f"Error running bot: {e}")
            # We don't raise the exception here to allow for a graceful shutdown
            # in the main function's finally block.
    
    async def stop(self):
        """Stop the bot gracefully"""
        logger.info("Stopping bot...")
        self.is_running = False
        
        try:
            # # Stop scheduler (Temporarily disabled for debugging)
            # if self.scheduler:
            #     self.scheduler.stop()
            #     logger.info("Scheduler stopped")
            
            # Stop application
            if self.app and self.app.running:
                await self.app.stop()
                await self.app.shutdown()
                logger.info("Application stopped")
                
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
        
        logger.info("Bot stopped successfully")

# Global bot instance
bot = GreedBot()

async def main():
    """Main application entry point"""
    logger.info("=" * 50)
    logger.info("CNN Fear & Greed Index Telegram Bot")
    logger.info("=" * 50)
    logger.info(f"Starting at {datetime.now()}")
    logger.info(f"Debug mode: {config.DEBUG}")
    logger.info(f"Test mode: {config.TEST_MODE}")
    logger.info(f"Language: {config.DEFAULT_LANGUAGE}")
    
    try:
        # Initialize bot
        await bot.initialize()
        
        # Start bot
        await bot.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        await bot.stop()

if __name__ == "__main__":
    # Signal handlers are removed to let the library handle them.
    
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown complete")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1) 