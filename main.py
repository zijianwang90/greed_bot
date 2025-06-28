#!/usr/bin/env python3
"""
CNN Fear & Greed Index Telegram Bot
Main entry point for the bot application
"""

import logging
import sys
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Import configuration and modules
import config
from data.database import init_database
from bot.handlers import (
    start_handler, help_handler, current_handler, 
    subscribe_handler, unsubscribe_handler, settings_handler, 
    history_handler, message_handler, button_handler, error_handler
)

# Setup logging
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper()),
    format=log_format
)
logger = logging.getLogger(__name__)

# Suppress verbose logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

async def startup_callback(application: Application) -> None:
    """Callback function that runs when the bot starts up"""
    logger.info("=" * 50)
    logger.info("CNN Fear & Greed Index Telegram Bot")
    logger.info("=" * 50)
    logger.info(f"Starting at {datetime.now()}")
    logger.info(f"Debug mode: {config.DEBUG}")
    logger.info(f"Language: {config.DEFAULT_LANGUAGE}")
    
    # Initialize database
    logger.info("Initializing database...")
    await init_database()
    logger.info("Database initialized successfully!")
    
    # Note: Scheduler is temporarily disabled to isolate the issue
    logger.info("Bot startup complete!")

def main():
    """Main function to start the bot"""
    try:
        # Create application
        logger.info("Creating Telegram application...")
        app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).post_init(startup_callback).build()
        
        # Add handlers
        logger.info("Registering handlers...")
        
        # Command handlers
        app.add_handler(CommandHandler("start", start_handler))
        app.add_handler(CommandHandler("help", help_handler))
        app.add_handler(CommandHandler("current", current_handler))
        app.add_handler(CommandHandler("subscribe", subscribe_handler))
        app.add_handler(CommandHandler("unsubscribe", unsubscribe_handler))
        app.add_handler(CommandHandler("settings", settings_handler))
        app.add_handler(CommandHandler("history", history_handler))
        
        # Callback query handler
        app.add_handler(CallbackQueryHandler(button_handler))
        
        # Message handler
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
        
        # Error handler
        app.add_error_handler(error_handler)
        
        logger.info("All handlers registered successfully!")
        
        # Start polling
        logger.info("Starting bot in polling mode...")
        app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 