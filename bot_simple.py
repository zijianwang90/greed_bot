#!/usr/bin/env python3
"""
Simplified bot runner for CNN Fear & Greed Index Bot
"""

import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Import configuration
import config
from data.database import init_database
from bot.handlers import start_handler, help_handler, current_handler, subscribe_handler, unsubscribe_handler

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(application: Application) -> None:
    """Initialize the database when the bot starts"""
    logger.info("Initializing database...")
    await init_database()
    logger.info("Database initialized successfully!")

def main() -> None:
    """Start the bot using the simplified approach"""
    logger.info("Starting CNN Fear & Greed Index Bot (Simplified Version)...")
    
    # Create the Application
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("current", current_handler))
    application.add_handler(CommandHandler("subscribe", subscribe_handler))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe_handler))
    
    logger.info("Handlers registered successfully!")
    
    # Run the bot until the user presses Ctrl-C
    logger.info("Starting polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 