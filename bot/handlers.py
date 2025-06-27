"""
临时简化的handlers模块
包含基本功能以让bot能够启动运行
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from data.database import get_user_or_create, UserRepository, is_user_subscribed
from data.fetcher import DataFetcher

import config

logger = logging.getLogger(__name__)

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user = update.effective_user
    chat_id = update.effective_chat.id if update.effective_chat else None
    
    if not user or not chat_id:
        return
    
    logger.info(f"User {user.id} ({user.username}) started the bot")
    
    try:
        # Get or create user
        db_user = await get_user_or_create(user)
        logger.info(f"User {user.id} accessed start command")
        
        # Get current market data
        fetcher = DataFetcher()
        try:
            current_data = await fetcher.get_current_fear_greed_index()
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            current_data = None
        
        # Welcome message
        welcome_msg = (
            "🎯 **Welcome to CNN Fear & Greed Index Bot!**\n\n"
            "📊 Get daily market sentiment updates delivered to your Telegram\n"
            "📈 Track market fear and greed indicators\n" 
            "🔔 Set custom notification times\n\n"
            "**Available Commands:**\n"
            "• /current - Current market sentiment\n"
            "• /subscribe - Subscribe to daily updates\n"
            "• /unsubscribe - Unsubscribe from updates\n"
            "• /help - Show all commands\n\n"
        )
        
        # Add current market data if available
        if current_data:
            index_value = current_data.get('score', 'N/A')
            sentiment = get_sentiment_text(index_value)
            welcome_msg += f"📊 **Current Index**: {index_value} ({sentiment})\n\n"
        
        # Create inline keyboard
        keyboard = [
            [
                InlineKeyboardButton("📊 Current Index", callback_data="current"),
                InlineKeyboardButton("🔔 Subscribe", callback_data="subscribe")
            ],
            [
                InlineKeyboardButton("❓ Help", callback_data="help")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in start_handler: {e}")
        await update.message.reply_text(
            "❌ Sorry, there was an error. Please try again later.",
            parse_mode=ParseMode.MARKDOWN
        )

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = (
        "🤖 **CNN Fear & Greed Index Bot Help**\n\n"
        "**📊 Commands:**\n"
        "• `/start` - Start the bot and see welcome message\n"
        "• `/current` - Get current Fear & Greed Index\n"
        "• `/subscribe` - Subscribe to daily updates\n"
        "• `/unsubscribe` - Unsubscribe from updates\n"
        "• `/help` - Show this help message\n\n"
        "**📈 About the Index:**\n"
        "The CNN Fear & Greed Index measures market sentiment:\n"
        "• 0-24: Extreme Fear 😨\n"
        "• 25-49: Fear 😟\n"
        "• 50: Neutral 😐\n"
        "• 51-74: Greed 😃\n"
        "• 75-100: Extreme Greed 🤑\n\n"
        "⚠️ **Disclaimer:** This information is for educational purposes only."
    )
    
    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.MARKDOWN
    )

async def current_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /current command"""
    loading_msg = await update.message.reply_text("📊 Fetching current market sentiment...")
    
    try:
        fetcher = DataFetcher()
        current_data = await fetcher.get_current_fear_greed_index()
        
        if current_data:
            index_value = current_data.get('score', 'N/A')
            sentiment = get_sentiment_text(index_value)
            emoji = get_sentiment_emoji(index_value)
            
            message = (
                f"📊 **Current Fear & Greed Index**\n\n"
                f"🎯 **Index**: {index_value}\n"
                f"{emoji} **Sentiment**: {sentiment}\n\n"
                f"📅 **Last Updated**: {current_data.get('timestamp', 'Unknown')}\n\n"
                "📈 Use /subscribe to get daily updates!"
            )
        else:
            message = "❌ Unable to fetch current data. Please try again later."
        
        await loading_msg.edit_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error in current_handler: {e}")
        await loading_msg.edit_text(
            "❌ Error fetching data. Please try again later."
        )

async def subscribe_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /subscribe command"""
    user_id = update.effective_user.id if update.effective_user else None
    if not user_id:
        return
    
    try:
        # Get or create user
        user = await UserRepository.get_user_by_telegram_id(user_id)
        if not user:
            user = await get_user_or_create(update.effective_user)
        
        # Subscribe user
        success = await UserRepository.update_user_subscription(user_id, True)
        
        if success:
            message = (
                "🔔 **Successfully subscribed to daily updates!**\n\n"
                f"📅 You'll receive daily Fear & Greed Index updates at {config.DEFAULT_NOTIFICATION_TIME} UTC\n\n"
                "❌ Use /unsubscribe to stop receiving updates"
            )
        else:
            message = "❌ Error subscribing. Please try again later."
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error in subscribe_handler: {e}")
        await update.message.reply_text(
            "❌ Error processing subscription. Please try again later."
        )

async def unsubscribe_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /unsubscribe command"""
    user_id = update.effective_user.id if update.effective_user else None
    if not user_id:
        return
    
    try:
        success = await UserRepository.update_user_subscription(user_id, False)
        
        if success:
            message = (
                "❌ **Successfully unsubscribed from daily updates**\n\n"
                "You'll no longer receive daily Fear & Greed Index notifications.\n\n"
                "🔔 Use /subscribe to re-enable daily updates anytime"
            )
        else:
            message = "❌ Error unsubscribing. Please try again later."
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error in unsubscribe_handler: {e}")
        await update.message.reply_text(
            "❌ Error processing unsubscription. Please try again later."
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard button presses"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data == "current":
        await current_callback(query)
    elif callback_data == "subscribe":
        await subscribe_callback(query)
    elif callback_data == "unsubscribe":
        await unsubscribe_callback(query)
    elif callback_data == "help":
        await help_callback(query)

async def current_callback(query):
    """Handle current button callback"""
    try:
        fetcher = DataFetcher()
        current_data = await fetcher.get_current_fear_greed_index()
        
        if current_data:
            index_value = current_data.get('score', 'N/A')
            sentiment = get_sentiment_text(index_value)
            emoji = get_sentiment_emoji(index_value)
            
            message = (
                f"📊 **Current Fear & Greed Index**\n\n"
                f"🎯 **Index**: {index_value}\n"
                f"{emoji} **Sentiment**: {sentiment}\n\n"
                f"📅 **Last Updated**: {current_data.get('timestamp', 'Unknown')}"
            )
        else:
            message = "❌ Unable to fetch current data. Please try again later."
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error in current_callback: {e}")
        await query.edit_message_text("❌ Error fetching data.")

async def subscribe_callback(query):
    """Handle subscribe button callback"""
    user_id = query.from_user.id
    
    try:
        success = await UserRepository.update_user_subscription(user_id, True)
        
        if success:
            message = "🔔 Successfully subscribed to daily updates!"
        else:
            message = "❌ Error subscribing. Please try again."
        
        await query.edit_message_text(message)
        
    except Exception as e:
        logger.error(f"Error in subscribe_callback: {e}")
        await query.edit_message_text("❌ Error processing subscription.")

async def unsubscribe_callback(query):
    """Handle unsubscribe button callback"""
    user_id = query.from_user.id
    
    try:
        success = await UserRepository.update_user_subscription(user_id, False)
        
        if success:
            message = "❌ Successfully unsubscribed from daily updates!"
        else:
            message = "❌ Error unsubscribing. Please try again."
        
        await query.edit_message_text(message)
        
    except Exception as e:
        logger.error(f"Error in unsubscribe_callback: {e}")
        await query.edit_message_text("❌ Error processing unsubscription.")

async def help_callback(query):
    """Handle help button callback"""
    help_text = (
        "🤖 **CNN Fear & Greed Index Bot**\n\n"
        "**Commands:**\n"
        "• /current - Current index\n"
        "• /subscribe - Daily updates\n"
        "• /unsubscribe - Stop updates\n"
        "• /settings - Configure preferences\n"
        "• /history - Historical data\n"
        "• /help - This help\n\n"
        "**Index Scale:**\n"
        "• 0-24: Extreme Fear 😨\n"
        "• 25-49: Fear 😟\n"
        "• 50: Neutral 😐\n"
        "• 51-74: Greed 😃\n"
        "• 75-100: Extreme Greed 🤑"
    )
    
    await query.edit_message_text(
        help_text,
        parse_mode=ParseMode.MARKDOWN
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors"""
    logger.error(f"Exception while handling an update: {context.error}")

# Utility functions
def get_sentiment_text(index_value):
    """Get sentiment text based on index value"""
    try:
        value = float(index_value)
        if value <= 24:
            return "Extreme Fear"
        elif value <= 49:
            return "Fear"
        elif value == 50:
            return "Neutral"
        elif value <= 74:
            return "Greed"
        else:
            return "Extreme Greed"
    except (ValueError, TypeError):
        return "Unknown"

def get_sentiment_emoji(index_value):
    """Get emoji based on index value"""
    try:
        value = float(index_value)
        if value <= 24:
            return "😨"
        elif value <= 49:
            return "😟"
        elif value == 50:
            return "😐"
        elif value <= 74:
            return "😃"
        else:
            return "🤑"
    except (ValueError, TypeError):
        return "❓"

async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /settings command"""
    user_id = update.effective_user.id if update.effective_user else None
    if not user_id:
        return
    
    try:
        # Check if user is subscribed
        is_subscribed = await is_user_subscribed(user_id)
        subscription_status = "🔔 Subscribed" if is_subscribed else "❌ Not subscribed"
        
        settings_msg = (
            "⚙️ **Your Current Settings:**\n\n"
            f"🔔 **Subscription:** {subscription_status}\n"
            f"⏰ **Notification Time:** {config.DEFAULT_NOTIFICATION_TIME} UTC\n"
            f"🌍 **Timezone:** UTC\n\n"
            "**Available Actions:**"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🔔 Toggle Subscription", callback_data="subscribe" if not is_subscribed else "unsubscribe")
            ],
            [
                InlineKeyboardButton("📊 Current Index", callback_data="current"),
                InlineKeyboardButton("❓ Help", callback_data="help")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            settings_msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in settings_handler: {e}")
        await update.message.reply_text(
            "❌ Error loading settings. Please try again later."
        )

async def history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /history command"""
    user_id = update.effective_user.id if update.effective_user else None
    if not user_id:
        return
    
    loading_msg = await update.message.reply_text("📈 Fetching historical data...")
    
    try:
        # For now, provide a simple message about historical data
        message = (
            "📈 **Historical Data Feature**\n\n"
            "This feature will show historical Fear & Greed Index data and trends.\n\n"
            "📊 **Coming Soon:**\n"
            "• 7-day trends\n"
            "• 30-day averages\n"
            "• Market correlation data\n\n"
            "For now, use /current to get the latest index value."
        )
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Current Index", callback_data="current"),
                InlineKeyboardButton("🔔 Subscribe", callback_data="subscribe")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await loading_msg.edit_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in history_handler: {e}")
        await loading_msg.edit_text(
            "❌ Error fetching historical data. Please try again later."
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle general text messages"""
    user_id = update.effective_user.id if update.effective_user else None
    if not user_id:
        return
    
    # General help message for any text input
    response = (
        "🤖 I'm here to help you track market sentiment!\n\n"
        "📊 Use /current to get the latest Fear & Greed Index\n"
        "🔔 Use /subscribe for daily updates\n"
        "⚙️ Use /settings to configure preferences\n"
        "❓ Use /help for all commands\n\n"
        "Or use the buttons below:"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Current", callback_data="current"),
            InlineKeyboardButton("🔔 Subscribe", callback_data="subscribe")
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        response,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    ) 