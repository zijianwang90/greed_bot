"""
临时简化的handlers模块
包含基本功能以让bot能够启动运行
"""

import logging
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Fallback for Python < 3.9
    from datetime import timezone
    import pytz
    ZoneInfo = None
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from data.database import get_user_or_create, UserRepository, is_user_subscribed, get_cached_fear_greed_data
# Use cache-aware data fetcher
from data.cache_service import get_smart_fetcher, get_data_cache_status, force_refresh_data

import config
import config_local

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
        
        # Get current market data (using cache)
        fetcher = get_smart_fetcher(cache_timeout_minutes=30)
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
            "• /history - View historical data and trends\n"
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
                InlineKeyboardButton("📈 History", callback_data="history_7")
            ],
            [
                InlineKeyboardButton("🔔 Subscribe", callback_data="subscribe"),
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
        "• `/history [days]` - View historical data (default: 7 days)\n"
        "• `/subscribe` - Subscribe to daily updates\n"
        "• `/unsubscribe` - Unsubscribe from updates\n"
        "• `/settings` - Configure your preferences\n"
        "• `/timezone` - Set your timezone for time displays\n"
        "• `/help` - Show this help message\n\n"
        "**🔧 Admin Commands:**\n"
        "• `/cache` - View cache status\n"
        "• `/refresh` - Force refresh cache\n"
        "• `/debug` - Debug cache issues\n"
        "• `/test_notification [user_id]` - Send test notification\n"
        "• `/notification_status` - Check notification status\n\n"
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
        fetcher = get_smart_fetcher(cache_timeout_minutes=30)
        current_data = await fetcher.get_current_fear_greed_index()
        
        if current_data:
            index_value = current_data.get('score', 'N/A')
            sentiment = get_sentiment_text(index_value)
            emoji = get_sentiment_emoji(index_value)
            
            # Add cache info to message
            cache_info = ""
            if current_data.get('cached'):
                if current_data.get('is_stale'):
                    cache_info = "\n⚠️ *Using cached data (API temporarily unavailable)*"
                else:
                    cache_info = "\n✅ *Data from cache (recently updated)*"
            else:
                cache_info = "\n🔄 *Fresh data from API*"
            
            # Get user ID for timezone formatting
            user_id = update.effective_user.id if update.effective_user else None
            formatted_time = await format_timestamp(current_data.get('timestamp', 'Unknown'), user_id)
            
            message = (
                f"📊 **Current Fear & Greed Index**\n\n"
                f"🎯 **Index**: {index_value}\n"
                f"{emoji} **Sentiment**: {sentiment}\n\n"
                f"📅 **Last Updated**: {formatted_time}{cache_info}\n\n"
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
            # Format notification time in user's timezone
            formatted_notification_time = await format_notification_time(config.DEFAULT_NOTIFICATION_TIME, user_id)
            
            message = (
                "🔔 **Successfully subscribed to daily updates!**\n\n"
                f"📅 You'll receive daily Fear & Greed Index updates at {formatted_notification_time}\n\n"
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
    elif callback_data == "force_refresh":
        await force_refresh_callback(query)
    elif callback_data.startswith("history_"):
        await history_callback(query, callback_data)
    elif callback_data == "refresh":
        await refresh_callback(query)

async def current_callback(query):
    """Handle current button callback"""
    try:
        fetcher = get_smart_fetcher(cache_timeout_minutes=30)
        current_data = await fetcher.get_current_fear_greed_index()
        
        if current_data:
            index_value = current_data.get('score', 'N/A')
            sentiment = get_sentiment_text(index_value)
            emoji = get_sentiment_emoji(index_value)
            
            # Add cache indicator for callback
            cache_indicator = ""
            if current_data.get('cached'):
                cache_indicator = " 💾" if not current_data.get('is_stale') else " ⚠️"
            else:
                cache_indicator = " 🔄"
            
            # Get user ID for timezone formatting
            user_id = query.from_user.id
            formatted_time = await format_timestamp(current_data.get('timestamp', 'Unknown'), user_id)
            
            message = (
                f"📊 **Current Fear & Greed Index**\n\n"
                f"🎯 **Index**: {index_value}\n"
                f"{emoji} **Sentiment**: {sentiment}\n\n"
                f"📅 **Last Updated**: {formatted_time}{cache_indicator}"
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

async def format_timestamp(timestamp_str, user_id=None):
    """Format timestamp string to more readable format using user's timezone or configured timezone"""
    if not timestamp_str or timestamp_str == 'Unknown':
        return 'Unknown'
    
    try:
        # Get user's timezone if user_id is provided
        user_timezone = None
        if user_id:
            try:
                user_timezone = await UserRepository.get_user_timezone(user_id)
            except Exception as e:
                logger.warning(f"Could not get user timezone for {user_id}: {e}")
        
        # Fallback to configured timezone
        configured_tz = user_timezone or getattr(config_local, 'DEFAULT_TIMEZONE', 'UTC')
        
        # Handle different timestamp formats
        if 'T' in timestamp_str:
            # ISO format: 2025-08-25T14:52:46+00:00
            if '+' in timestamp_str or timestamp_str.endswith('Z'):
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                # Handle format without timezone - assume UTC
                dt = datetime.fromisoformat(timestamp_str + '+00:00')
        else:
            # Try other formats - assume UTC if no timezone info
            dt = datetime.fromisoformat(timestamp_str + '+00:00')
        
        # Convert to target timezone
        if configured_tz != 'UTC':
            try:
                if ZoneInfo is not None:
                    # Use zoneinfo (Python 3.9+)
                    target_tz = ZoneInfo(configured_tz)
                    dt_converted = dt.astimezone(target_tz)
                    # Format with timezone abbreviation
                    tz_name = dt_converted.strftime('%Z') or configured_tz
                    return dt_converted.strftime(f"%b %d, %Y at %H:%M {tz_name}")
                else:
                    # Use pytz (Python < 3.9)
                    target_tz = pytz.timezone(configured_tz)
                    dt_converted = dt.astimezone(target_tz)
                    # Format with timezone abbreviation
                    tz_name = dt_converted.strftime('%Z') or configured_tz
                    return dt_converted.strftime(f"%b %d, %Y at %H:%M {tz_name}")
            except Exception as tz_error:
                logger.warning(f"Invalid timezone '{configured_tz}': {tz_error}, falling back to UTC")
                # Fallback to UTC
                return dt.strftime("%b %d, %Y at %H:%M UTC")
        else:
            # Use UTC directly
            return dt.strftime("%b %d, %Y at %H:%M UTC")
            
    except (ValueError, TypeError) as e:
        logger.warning(f"Could not parse timestamp '{timestamp_str}': {e}")
        return timestamp_str

async def format_notification_time(utc_time_str, user_id=None):
    """Format notification time string to user's timezone"""
    try:
        # Get user's timezone if user_id is provided
        user_timezone = None
        if user_id:
            try:
                user_timezone = await UserRepository.get_user_timezone(user_id)
            except Exception as e:
                logger.warning(f"Could not get user timezone for {user_id}: {e}")
        
        # Fallback to configured timezone
        configured_tz = user_timezone or getattr(config_local, 'DEFAULT_TIMEZONE', 'UTC')
        
        # Parse UTC time (format: HH:MM)
        hour, minute = map(int, utc_time_str.split(':'))
        
        # Create a datetime object for today at the specified UTC time
        from datetime import timezone as tz
        utc_dt = datetime.now(tz.utc).replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Convert to user's timezone
        if configured_tz != 'UTC':
            try:
                if ZoneInfo is not None:
                    # Use zoneinfo (Python 3.9+)
                    target_tz = ZoneInfo(configured_tz)
                    local_dt = utc_dt.astimezone(target_tz)
                    tz_name = local_dt.strftime('%Z') or configured_tz
                    return f"{local_dt.strftime('%H:%M')} {tz_name}"
                else:
                    # Use pytz (Python < 3.9)
                    target_tz = pytz.timezone(configured_tz)
                    local_dt = utc_dt.astimezone(target_tz)
                    tz_name = local_dt.strftime('%Z') or configured_tz
                    return f"{local_dt.strftime('%H:%M')} {tz_name}"
            except Exception as tz_error:
                logger.warning(f"Invalid timezone '{configured_tz}': {tz_error}, falling back to UTC")
                return f"{utc_time_str} UTC"
        else:
            return f"{utc_time_str} UTC"
            
    except Exception as e:
        logger.warning(f"Could not format notification time '{utc_time_str}': {e}")
        return f"{utc_time_str} UTC"

async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /settings command"""
    user_id = update.effective_user.id if update.effective_user else None
    if not user_id:
        return
    
    try:
        # Get user settings
        is_subscribed = await is_user_subscribed(user_id)
        user_timezone = await UserRepository.get_user_timezone(user_id) or "Asia/Shanghai"
        subscription_status = "🔔 Subscribed" if is_subscribed else "❌ Not subscribed"
        
        # Show current time in user's timezone
        current_time = datetime.now().isoformat() + '+00:00'
        formatted_time = await format_timestamp(current_time, user_id)
        
        # Format notification time in user's timezone
        formatted_notification_time = await format_notification_time(config.DEFAULT_NOTIFICATION_TIME, user_id)
        
        settings_msg = (
            "⚙️ **Your Current Settings:**\n\n"
            f"🔔 **Subscription:** {subscription_status}\n"
            f"⏰ **Notification Time:** {formatted_notification_time}\n"
            f"🌍 **Timezone:** {user_timezone}\n"
            f"🕐 **Current Time:** {formatted_time}\n\n"
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
    
    loading_msg = await update.message.reply_text("📈 正在获取历史数据...")
    
    try:
        # 获取用户信息，用于时区设置
        user = await get_user_or_create(update.effective_user)
        user_timezone = user.timezone if user else "UTC"
        
        # 解析命令参数
        args = context.args
        days = 7  # 默认7天
        
        if args and len(args) > 0:
            try:
                days = int(args[0])
                if days <= 0 or days > 365:
                    days = 7
            except ValueError:
                days = 7
        
        # 从数据库获取历史数据
        from data.database import FearGreedRepository
        historical_records = await FearGreedRepository.get_fear_greed_history(days=days)
        
        if not historical_records:
            message = (
                "📈 **历史数据**\n\n"
                "❌ 暂无历史数据可用\n\n"
                "请先使用 /current 获取当前数据，系统会开始收集历史记录。"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("📊 当前指数", callback_data="current"),
                    InlineKeyboardButton("🔔 订阅推送", callback_data="subscribe")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await loading_msg.edit_text(
                message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            return
        
        # 格式化历史数据 (临时使用简化版本避免Markdown错误)
        from bot.utils import format_simple_history
        message = format_simple_history(
            historical_records, 
            days=days,
            user_timezone=user_timezone
        )
        
        # 创建交互按钮
        keyboard = [
            [
                InlineKeyboardButton("📊 7天", callback_data="history_7"),
                InlineKeyboardButton("📊 30天", callback_data="history_30")
            ],
            [
                InlineKeyboardButton("📈 当前指数", callback_data="current"),
                InlineKeyboardButton("🔄 刷新", callback_data="refresh")
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
            "❌ 获取历史数据时出错，请稍后重试。"
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


async def cache_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /cache command - show cache status (admin only)"""
    user_id = update.effective_user.id if update.effective_user else None
    
    # Check if user is admin
    if not user_id or (config.ADMIN_USER_ID and user_id != int(config.ADMIN_USER_ID)):
        await update.message.reply_text("❌ This command is only available to administrators.")
        return
    
    try:
        cache_status = await get_data_cache_status()
        
        if cache_status.get('has_cache'):
            cache_age = cache_status.get('cache_age_minutes', 0)
            is_fresh = cache_status.get('is_fresh', False)
            
            status_emoji = "🟢" if is_fresh else "🟡"
            freshness = "Fresh" if is_fresh else "Stale"
            
            # Get user ID for timezone formatting
            user_id = update.effective_user.id if update.effective_user else None
            formatted_time = await format_timestamp(cache_status.get('last_update', 'Unknown'), user_id)
            
            message = (
                f"📊 **Cache Status**\n\n"
                f"{status_emoji} **Status**: {freshness}\n"
                f"⏱️ **Age**: {cache_age} minutes\n"
                f"📈 **Value**: {cache_status.get('current_value', 'N/A')}\n"
                f"🔗 **Source**: {cache_status.get('source', 'Unknown')}\n"
                f"🕐 **Last Updated**: {formatted_time}\n\n"
                "Use /refresh to force refresh the cache."
            )
        else:
            message = (
                "📊 **Cache Status**\n\n"
                "❌ **No cached data available**\n\n"
                "Use /refresh to fetch fresh data."
            )
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Force Refresh", callback_data="force_refresh"),
                InlineKeyboardButton("📊 Current Data", callback_data="current")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in cache_status_handler: {e}")
        await update.message.reply_text(
            "❌ Error retrieving cache status. Please try again later."
        )


async def refresh_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /refresh command - force refresh cache (admin only)"""
    user_id = update.effective_user.id if update.effective_user else None
    
    # Check if user is admin
    if not user_id or (config.ADMIN_USER_ID and user_id != int(config.ADMIN_USER_ID)):
        await update.message.reply_text("❌ This command is only available to administrators.")
        return
    
    loading_msg = await update.message.reply_text("🔄 Forcing cache refresh...")
    
    try:
        fresh_data = await force_refresh_data()
        
        if fresh_data:
            index_value = fresh_data.get('score', 'N/A')
            sentiment = get_sentiment_text(index_value)
            
            # Get user ID for timezone formatting
            user_id = update.effective_user.id if update.effective_user else None
            formatted_time = await format_timestamp(fresh_data.get('timestamp', 'Now'), user_id)
            
            message = (
                f"✅ **Cache Refreshed Successfully**\n\n"
                f"📊 **New Index**: {index_value} ({sentiment})\n"
                f"🔗 **Source**: {fresh_data.get('source', 'Unknown')}\n"
                f"🕐 **Updated**: {formatted_time}"
            )
        else:
            message = "❌ Failed to refresh cache. API may be temporarily unavailable."
        
        await loading_msg.edit_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error in refresh_handler: {e}")
        await loading_msg.edit_text(
            "❌ Error refreshing cache. Please try again later."
        )


async def force_refresh_callback(query):
    """Handle force refresh button callback (admin only)"""
    user_id = query.from_user.id
    
    # Check if user is admin
    if config.ADMIN_USER_ID and user_id != int(config.ADMIN_USER_ID):
        await query.edit_message_text("❌ This action is only available to administrators.")
        return
    
    try:
        await query.edit_message_text("🔄 Forcing cache refresh...")
        
        fresh_data = await force_refresh_data()
        
        if fresh_data:
            index_value = fresh_data.get('score', 'N/A')
            sentiment = get_sentiment_text(index_value)
            
            message = (
                f"✅ **Cache Refreshed**\n\n"
                f"📊 **Index**: {index_value} ({sentiment})\n"
                f"🔗 **Source**: {fresh_data.get('source', 'Unknown')}"
            )
        else:
            message = "❌ Failed to refresh cache."
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error in force_refresh_callback: {e}")
        await query.edit_message_text("❌ Error refreshing cache.")

async def history_callback(query, callback_data: str):
    """Handle history button callbacks"""
    try:
        # 提取天数参数
        if callback_data == "history_7":
            days = 7
        elif callback_data == "history_30":
            days = 30
        else:
            days = 7
        
        await query.edit_message_text("📈 正在获取历史数据...")
        
        # 获取用户信息
        user_id = query.from_user.id
        from data.database import get_user
        user = await get_user(user_id)
        user_timezone = user.timezone if user else "UTC"
        
        # 从数据库获取历史数据
        from data.database import FearGreedRepository
        historical_records = await FearGreedRepository.get_fear_greed_history(days=days)
        
        if not historical_records:
            message = (
                "📈 **历史数据**\n\n"
                "❌ 暂无历史数据可用\n\n"
                "请先使用 /current 获取当前数据，系统会开始收集历史记录。"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("📊 当前指数", callback_data="current"),
                    InlineKeyboardButton("🔔 订阅推送", callback_data="subscribe")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            return
        
        # 格式化历史数据 (临时使用简化版本避免Markdown错误)
        from bot.utils import format_simple_history
        message = format_simple_history(
            historical_records, 
            days=days,
            user_timezone=user_timezone
        )
        
        # 创建交互按钮
        keyboard = [
            [
                InlineKeyboardButton("📊 7天", callback_data="history_7"),
                InlineKeyboardButton("📊 30天", callback_data="history_30")
            ],
            [
                InlineKeyboardButton("📈 当前指数", callback_data="current"),
                InlineKeyboardButton("🔄 刷新", callback_data="refresh")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in history_callback: {e}")
        await query.edit_message_text("❌ 获取历史数据时出错，请稍后重试。")

async def refresh_callback(query):
    """Handle refresh button callback"""
    try:
        await query.edit_message_text("🔄 正在刷新数据...")
        
        # 强制刷新数据
        fresh_data = await force_refresh_data()
        
        if fresh_data:
            index_value = fresh_data.get('score', 'N/A')
            sentiment = get_sentiment_text(index_value)
            emoji = get_sentiment_emoji(index_value)
            
            # 获取用户ID用于时区格式化
            user_id = query.from_user.id
            formatted_time = await format_timestamp(fresh_data.get('timestamp', 'Now'), user_id)
            
            message = (
                f"✅ **数据已刷新**\n\n"
                f"📊 **当前指数**: {index_value}\n"
                f"{emoji} **市场情绪**: {sentiment}\n\n"
                f"🕐 **更新时间**: {formatted_time}\n"
                f"🔗 **数据来源**: {fresh_data.get('source', 'CNN')}"
            )
            
            # 创建新的按钮
            keyboard = [
                [
                    InlineKeyboardButton("📈 历史数据", callback_data="history_7"),
                    InlineKeyboardButton("🔔 订阅推送", callback_data="subscribe")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text("❌ 刷新失败，API可能暂时不可用。")
        
    except Exception as e:
        logger.error(f"Error in refresh_callback: {e}")
        await query.edit_message_text("❌ 刷新数据时出错。")


async def debug_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /debug command - debug cache issues (admin only)"""
    user_id = update.effective_user.id if update.effective_user else None
    
    # Check if user is admin
    if not user_id or (config.ADMIN_USER_ID and user_id != int(config.ADMIN_USER_ID)):
        await update.message.reply_text("❌ This command is only available to administrators.")
        return
    
    try:
        from data.database import FearGreedRepository
        
        # Check raw database records
        all_records = await FearGreedRepository.get_fear_greed_history(days=1)
        
        debug_msg = "🔍 **Cache Debug Info**\n\n"
        
        if all_records:
            debug_msg += f"📊 **Database Records (last 24h)**: {len(all_records)}\n\n"
            for i, record in enumerate(all_records[:3]):  # Show max 3 records
                age_minutes = (datetime.utcnow() - record.created_at).total_seconds() / 60
                debug_msg += (
                    f"**Record {i+1}:**\n"
                    f"• ID: {record.id}\n"
                    f"• Value: {record.current_value}\n"
                    f"• Created: {record.created_at}\n"
                    f"• Age: {age_minutes:.1f}min\n\n"
                )
        else:
            debug_msg += "❌ **No database records found**\n\n"
        
        # Test cache retrieval directly
        cached_data = await get_cached_fear_greed_data(cache_timeout_minutes=30)
        if cached_data:
            debug_msg += f"✅ **Cache Test**: Found data (Age: {cached_data.get('cache_time')})\n"
        else:
            debug_msg += "❌ **Cache Test**: No valid cache data\n"
        
        # Test with different timeout
        cached_data_long = await get_cached_fear_greed_data(cache_timeout_minutes=1440)
        if cached_data_long:
            debug_msg += f"✅ **Cache Test (24h)**: Found data\n"
        else:
            debug_msg += "❌ **Cache Test (24h)**: No data\n"
        
        await update.message.reply_text(
            debug_msg,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error in debug_handler: {e}")
        await update.message.reply_text(
            f"❌ Debug error: {str(e)}"
        )


async def timezone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /timezone command - allow users to set their timezone"""
    user_id = update.effective_user.id if update.effective_user else None
    if not user_id:
        return
    
    try:
        # Check if user provided a timezone argument
        args = context.args
        
        if not args:
            # Show current timezone and available options
            current_tz = await UserRepository.get_user_timezone(user_id) or "Asia/Shanghai"
            
            message = (
                f"🌍 <b>Your Current Timezone</b>: {current_tz}\n\n"
                "<b>To change your timezone, use:</b>\n"
                "/timezone &lt;timezone_name&gt;\n\n"
                "<b>Popular Timezones:</b>\n"
                "• /timezone UTC - Coordinated Universal Time\n"
                "• /timezone Asia/Shanghai - China Standard Time\n"
                "• /timezone America/New_York - US Eastern Time\n"
                "• /timezone America/Los_Angeles - US Pacific Time\n"
                "• /timezone Europe/London - UK Time\n"
                "• /timezone Asia/Tokyo - Japan Standard Time\n"
                "• /timezone Australia/Sydney - Australia Eastern Time\n\n"
                "💡 <b>Tip</b>: You can find your timezone at worldtimeapi.org"
            )
            
            await update.message.reply_text(
                message,
                parse_mode=ParseMode.HTML
            )
            return
        
        # Validate and set the new timezone
        new_timezone = args[0]
        
        # Test if timezone is valid
        try:
            if ZoneInfo is not None:
                ZoneInfo(new_timezone)
            else:
                pytz.timezone(new_timezone)
        except Exception:
            await update.message.reply_text(
                f"❌ Invalid timezone: {new_timezone}\n\n"
                "Please use a valid timezone name like:\n"
                "• UTC\n"
                "• Asia/Shanghai\n"
                "• America/New_York\n"
                "• Europe/London\n\n"
                "Find your timezone at worldtimeapi.org",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Update user's timezone
        success = await UserRepository.update_user_timezone(user_id, new_timezone)
        
        if success:
            # Test the new timezone with current time
            test_time = datetime.now().isoformat() + '+00:00'
            formatted_time = await format_timestamp(test_time, user_id)
            
            message = (
                f"✅ <b>Timezone Updated Successfully!</b>\n\n"
                f"🌍 <b>New Timezone</b>: {new_timezone}\n"
                f"🕐 <b>Current Time</b>: {formatted_time}\n\n"
                "Your timezone will be used for all time displays in the bot."
            )
        else:
            message = "❌ Failed to update timezone. Please try again later."
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Error in timezone_handler: {e}")
        await update.message.reply_text(
            "❌ Error updating timezone. Please try again later."
        )


async def test_notification_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /test_notification command - send test notification (admin only)"""
    user_id = update.effective_user.id if update.effective_user else None
    
    # Check if user is admin
    if not user_id or (config.ADMIN_USER_ID and user_id != int(config.ADMIN_USER_ID)):
        await update.message.reply_text("❌ This command is only available to administrators.")
        return
    
    try:
        # Check if target user ID is provided
        args = context.args
        target_user_id = int(args[0]) if args else user_id
        
        loading_msg = await update.message.reply_text(f"🔄 Sending test notification to user {target_user_id}...")
        
        # Import scheduler functions
        from bot.scheduler import trigger_test_notification
        
        logger.info(f"Admin {user_id} requested test notification for user {target_user_id}")
        
        # Try to send test notification
        success = await trigger_test_notification(target_user_id)
        
        if success:
            message = f"✅ Test notification sent successfully to user {target_user_id}"
        else:
            message = f"❌ Failed to send test notification to user {target_user_id}. Check logs for details."
        
        await loading_msg.edit_text(message)
        
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID. Usage: /test_notification [user_id]")
    except Exception as e:
        logger.error(f"Error in test_notification_handler: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error sending test notification: {str(e)}")


async def notification_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /notification_status command - show notification status (admin only)"""
    user_id = update.effective_user.id if update.effective_user else None
    
    # Check if user is admin
    if not user_id or (config.ADMIN_USER_ID and user_id != int(config.ADMIN_USER_ID)):
        await update.message.reply_text("❌ This command is only available to administrators.")
        return
    
    try:
        loading_msg = await update.message.reply_text("🔄 Checking notification status...")
        
        from bot.scheduler import check_notification_status
        status = await check_notification_status()
        
        if "error" in status:
            message = f"❌ Error checking status: {status['error']}"
        else:
            # Use HTML parse mode to avoid Markdown conflicts with special characters
            message = (
                f"📊 <b>Notification Status</b>\n\n"
                f"🔧 <b>Scheduler Running</b>: {'✅' if status['scheduler_running'] else '❌'}\n"
                f"🕐 <b>Current UTC Time</b>: {status['current_utc_time']}\n"
                f"👥 <b>Subscribed Users</b>: {status['subscribed_users_count']}\n"
                f"🔔 <b>Ready for Notification</b>: {status['users_ready_for_notification']}\n\n"
            )
            
            if status['user_details']:
                message += "<b>User Details:</b>\n"
                for user_info in status['user_details'][:5]:  # Show first 5 users
                    should_notify = "🔔" if user_info['should_notify_now'] else "⏸️"
                    # Escape HTML special characters in user data
                    user_id = str(user_info['user_id'])
                    push_time = str(user_info['push_time'] or 'N/A')
                    timezone_str = str(user_info['timezone'] or 'N/A')
                    
                    message += (
                        f"{should_notify} User {user_id}: "
                        f"{push_time} {timezone_str}\n"
                    )
                
                if len(status['user_details']) > 5:
                    message += f"... and {len(status['user_details']) - 5} more users\n"
        
        await loading_msg.edit_text(
            message,
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Error in notification_status_handler: {e}")
        await update.message.reply_text(f"❌ Error checking notification status: {str(e)}") 