"""
Telegram Bot Command Handlers
Handles all user interactions and commands
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from data.database import (
    get_user, create_user, update_user_settings, 
    subscribe_user, unsubscribe_user, get_user_subscriptions
)
from data.fetcher import DataFetcher
from bot.utils import (
    format_fear_greed_message, format_historical_message,
    get_user_language, set_user_language, validate_time_format,
    get_sentiment_emoji, translate_text
)

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
        db_user = await get_user(user.id)
        if not db_user:
            await create_user(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                language_code=user.language_code or config.DEFAULT_LANGUAGE
            )
            logger.info(f"Created new user: {user.id}")
        
        # Get current market data
        fetcher = DataFetcher()
        current_data = await fetcher.get_current_fear_greed_index()
        
        user_lang = await get_user_language(user.id)
        
        # Welcome message
        welcome_msg = await translate_text(
            "🎯 **Welcome to CNN Fear & Greed Index Bot!**\n\n"
            "📊 Get daily market sentiment updates delivered to your Telegram\n"
            "📈 Track market fear and greed indicators\n" 
            "🔔 Set custom notification times\n"
            "📋 Access historical data and trends\n\n"
            "**Available Commands:**\n"
            "• /current - Current market sentiment\n"
            "• /subscribe - Subscribe to daily updates\n"
            "• /settings - Configure your preferences\n"
            "• /history - View historical data\n"
            "• /help - Show all commands\n\n",
            user_lang
        )
        
        # Add current market data if available
        if current_data:
            current_msg = await format_fear_greed_message(current_data, user_lang)
            welcome_msg += current_msg
        
        # Create inline keyboard
        keyboard = [
            [
                InlineKeyboardButton(
                    await translate_text("📊 Current Index", user_lang), 
                    callback_data="current"
                ),
                InlineKeyboardButton(
                    await translate_text("🔔 Subscribe", user_lang), 
                    callback_data="subscribe"
                )
            ],
            [
                InlineKeyboardButton(
                    await translate_text("⚙️ Settings", user_lang), 
                    callback_data="settings"
                ),
                InlineKeyboardButton(
                    await translate_text("📈 History", user_lang), 
                    callback_data="history"
                )
            ],
            [
                InlineKeyboardButton(
                    await translate_text("🌐 Language", user_lang), 
                    callback_data="language"
                ),
                InlineKeyboardButton(
                    await translate_text("❓ Help", user_lang), 
                    callback_data="help"
                )
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
    user_id = update.effective_user.id if update.effective_user else None
    if not user_id:
        return
        
    user_lang = await get_user_language(user_id)
    
    help_text = await translate_text(
        "🤖 **CNN Fear & Greed Index Bot Help**\n\n"
        "**📊 Market Sentiment Commands:**\n"
        "• `/current` - Get current Fear & Greed Index\n"
        "• `/history` - View historical data and trends\n\n"
        "**🔔 Subscription Commands:**\n"
        "• `/subscribe` - Subscribe to daily updates\n"
        "• `/unsubscribe` - Unsubscribe from updates\n\n"
        "**⚙️ Settings Commands:**\n"
        "• `/settings` - Configure notification time and preferences\n\n"
        "**📈 About the Index:**\n"
        "The CNN Fear & Greed Index measures market sentiment using 7 indicators:\n"
        "• Market Momentum (S&P 500 vs 125-day MA)\n"
        "• Stock Price Strength (52-week highs/lows)\n"
        "• Stock Price Breadth (McClellan Volume Index)\n"
        "• Put/Call Options ratio\n"
        "• Market Volatility (VIX)\n"
        "• Safe Haven Demand (stocks vs bonds)\n"
        "• Junk Bond Demand (yield spreads)\n\n"
        "**📊 Index Scale:**\n"
        "• 0-24: Extreme Fear 😨\n"
        "• 25-49: Fear 😟\n"
        "• 50: Neutral 😐\n"
        "• 51-74: Greed 😃\n"
        "• 75-100: Extreme Greed 🤑\n\n"
        "⚠️ **Disclaimer:** This information is for educational purposes only. "
        "Always do your own research before making investment decisions.",
        user_lang
    )
    
    keyboard = [
        [
            InlineKeyboardButton(
                await translate_text("📊 Current Index", user_lang), 
                callback_data="current"
            ),
            InlineKeyboardButton(
                await translate_text("🔔 Subscribe", user_lang), 
                callback_data="subscribe"
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

async def current_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /current command"""
    user_id = update.effective_user.id if update.effective_user else None
    if not user_id:
        return
    
    # Send "loading" message
    loading_msg = await update.message.reply_text("📊 Fetching current market sentiment...")
    
    try:
        fetcher = DataFetcher()
        current_data = await fetcher.get_current_fear_greed_index()
        user_lang = await get_user_language(user_id)
        
        if current_data:
            message = await format_fear_greed_message(current_data, user_lang, include_details=True)
            
            # Add additional market indicators if enabled
            if config.ENABLE_MARKET_INDICATORS:
                vix_data = await fetcher.get_vix_data()
                if vix_data:
                    message += f"\n🔹 **VIX**: {vix_data.get('value', 'N/A')} "
                    change = vix_data.get('change', 0)
                    if change > 0:
                        message += f"(+{change:.1f}%) 📈"
                    elif change < 0:
                        message += f"({change:.1f}%) 📉"
                    else:
                        message += "(0.0%) ➡️"
            
            # Create action buttons
            keyboard = [
                [
                    InlineKeyboardButton(
                        await translate_text("📈 History", user_lang), 
                        callback_data="history"
                    ),
                    InlineKeyboardButton(
                        await translate_text("🔔 Subscribe", user_lang), 
                        callback_data="subscribe"
                    )
                ],
                [
                    InlineKeyboardButton(
                        await translate_text("🔄 Refresh", user_lang), 
                        callback_data="current"
                    )
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
        else:
            message = await translate_text(
                "❌ Unable to fetch current market data. Please try again later.",
                user_lang
            )
            reply_markup = None
        
        # Edit the loading message
        await loading_msg.edit_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in current_handler: {e}")
        await loading_msg.edit_text(
            "❌ Error fetching market data. Please try again later."
        )

async def subscribe_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /subscribe command"""
    user_id = update.effective_user.id if update.effective_user else None
    if not user_id:
        return
    
    try:
        # Check if user exists
        user = await get_user(user_id)
        if not user:
            await update.message.reply_text(
                "❌ Please start the bot first with /start"
            )
            return
        
        # Subscribe user
        success = await subscribe_user(user_id)
        user_lang = await get_user_language(user_id)
        
        if success:
            message = await translate_text(
                "🔔 **Successfully subscribed to daily updates!**\n\n"
                f"📅 You'll receive daily Fear & Greed Index updates at {user.notification_time or config.DEFAULT_NOTIFICATION_TIME} UTC\n\n"
                "⚙️ Use /settings to customize your notification time and preferences\n"
                "❌ Use /unsubscribe to stop receiving updates",
                user_lang
            )
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        await translate_text("⚙️ Settings", user_lang), 
                        callback_data="settings"
                    ),
                    InlineKeyboardButton(
                        await translate_text("📊 Current", user_lang), 
                        callback_data="current"
                    )
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            message = await translate_text(
                "ℹ️ You're already subscribed to daily updates!\n\n"
                "⚙️ Use /settings to modify your preferences",
                user_lang
            )
            reply_markup = None
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
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
        success = await unsubscribe_user(user_id)
        user_lang = await get_user_language(user_id)
        
        if success:
            message = await translate_text(
                "❌ **Successfully unsubscribed from daily updates**\n\n"
                "You'll no longer receive daily Fear & Greed Index notifications.\n\n"
                "🔔 Use /subscribe to re-enable daily updates anytime\n"
                "📊 You can still use /current to check the index manually",
                user_lang
            )
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        await translate_text("🔔 Re-subscribe", user_lang), 
                        callback_data="subscribe"
                    ),
                    InlineKeyboardButton(
                        await translate_text("📊 Current", user_lang), 
                        callback_data="current"
                    )
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            message = await translate_text(
                "ℹ️ You're not currently subscribed to daily updates.\n\n"
                "🔔 Use /subscribe to start receiving daily notifications",
                user_lang
            )
            reply_markup = None
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in unsubscribe_handler: {e}")
        await update.message.reply_text(
            "❌ Error processing unsubscription. Please try again later."
        )

async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /settings command"""
    user_id = update.effective_user.id if update.effective_user else None
    if not user_id:
        return
    
    try:
        user = await get_user(user_id)
        if not user:
            await update.message.reply_text("❌ Please start the bot first with /start")
            return
        
        user_lang = await get_user_language(user_id)
        
        # Current settings
        subscription_status = "🔔 Subscribed" if user.subscribed else "❌ Not subscribed"
        notification_time = user.notification_time or config.DEFAULT_NOTIFICATION_TIME
        timezone = user.timezone or config.DEFAULT_TIMEZONE
        language = user.language_code or config.DEFAULT_LANGUAGE
        
        settings_msg = await translate_text(
            f"⚙️ **Your Current Settings:**\n\n"
            f"🔔 **Subscription:** {subscription_status}\n"
            f"⏰ **Notification Time:** {notification_time} ({timezone})\n"
            f"🌐 **Language:** {language.upper()}\n"
            f"📊 **Historical Data:** {'✅ Enabled' if config.ENABLE_HISTORICAL_DATA else '❌ Disabled'}\n"
            f"📈 **VIX Data:** {'✅ Enabled' if config.ENABLE_VIX_DATA else '❌ Disabled'}\n\n"
            "**Configure your preferences:**",
            user_lang
        )
        
        keyboard = [
            [
                InlineKeyboardButton(
                    await translate_text("⏰ Time", user_lang), 
                    callback_data="settings_time"
                ),
                InlineKeyboardButton(
                    await translate_text("🌐 Language", user_lang), 
                    callback_data="settings_language"
                )
            ],
            [
                InlineKeyboardButton(
                    await translate_text("🔔 Toggle Subscription", user_lang), 
                    callback_data="settings_subscription"
                )
            ],
            [
                InlineKeyboardButton(
                    await translate_text("📊 Current Index", user_lang), 
                    callback_data="current"
                )
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
    
    if not config.ENABLE_HISTORICAL_DATA:
        await update.message.reply_text(
            "❌ Historical data feature is currently disabled."
        )
        return
    
    loading_msg = await update.message.reply_text("📈 Fetching historical data...")
    
    try:
        fetcher = DataFetcher()
        historical_data = await fetcher.get_historical_data(days=30)
        user_lang = await get_user_language(user_id)
        
        if historical_data:
            message = await format_historical_message(historical_data, user_lang)
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        await translate_text("📊 Current", user_lang), 
                        callback_data="current"
                    ),
                    InlineKeyboardButton(
                        await translate_text("🔄 Refresh", user_lang), 
                        callback_data="history"
                    )
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            message = await translate_text(
                "❌ Unable to fetch historical data. Please try again later.",
                user_lang
            )
            reply_markup = None
        
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
    
    message_text = update.message.text.strip()
    user_lang = await get_user_language(user_id)
    
    # Check if it's a time format (for settings)
    if validate_time_format(message_text):
        try:
            await update_user_settings(user_id, notification_time=message_text)
            response = await translate_text(
                f"✅ Notification time updated to {message_text} UTC\n\n"
                "🔔 You'll receive daily updates at this time if subscribed.",
                user_lang
            )
        except Exception as e:
            logger.error(f"Error updating notification time: {e}")
            response = await translate_text(
                "❌ Error updating notification time. Please try again.",
                user_lang
            )
    else:
        # General help message
        response = await translate_text(
            "🤖 I'm here to help you track market sentiment!\n\n"
            "📊 Use /current to get the latest Fear & Greed Index\n"
            "🔔 Use /subscribe for daily updates\n"
            "❓ Use /help for all commands\n\n"
            "Or use the buttons below:",
            user_lang
        )
    
    keyboard = [
        [
            InlineKeyboardButton(
                await translate_text("📊 Current", user_lang), 
                callback_data="current"
            ),
            InlineKeyboardButton(
                await translate_text("❓ Help", user_lang), 
                callback_data="help"
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        response,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard button presses"""
    query = update.callback_query
    if not query:
        return
    
    await query.answer()
    
    user_id = query.from_user.id if query.from_user else None
    if not user_id:
        return
    
    user_lang = await get_user_language(user_id)
    
    try:
        if query.data == "current":
            await current_callback(query, user_lang)
        elif query.data == "subscribe":
            await subscribe_callback(query, user_lang)
        elif query.data == "unsubscribe":
            await unsubscribe_callback(query, user_lang)
        elif query.data == "settings":
            await settings_callback(query, user_lang)
        elif query.data == "history":
            await history_callback(query, user_lang)
        elif query.data == "help":
            await help_callback(query, user_lang)
        elif query.data == "language":
            await language_callback(query, user_lang)
        elif query.data.startswith("lang_"):
            await set_language_callback(query, query.data.split("_")[1])
        elif query.data.startswith("settings_"):
            await settings_submenu_callback(query, query.data, user_lang)
        else:
            await query.edit_message_text("❌ Unknown action")
            
    except Exception as e:
        logger.error(f"Error in button_handler: {e}")
        await query.edit_message_text("❌ Error processing request")

async def current_callback(query, user_lang):
    """Handle current data callback"""
    try:
        fetcher = DataFetcher()
        current_data = await fetcher.get_current_fear_greed_index()
        
        if current_data:
            message = await format_fear_greed_message(current_data, user_lang, include_details=True)
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        await translate_text("📈 History", user_lang), 
                        callback_data="history"
                    ),
                    InlineKeyboardButton(
                        await translate_text("🔔 Subscribe", user_lang), 
                        callback_data="subscribe"
                    )
                ],
                [
                    InlineKeyboardButton(
                        await translate_text("🔄 Refresh", user_lang), 
                        callback_data="current"
                    )
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            message = await translate_text(
                "❌ Unable to fetch current market data.",
                user_lang
            )
            reply_markup = None
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in current_callback: {e}")
        await query.edit_message_text("❌ Error fetching data")

async def language_callback(query, user_lang):
    """Handle language selection callback"""
    keyboard = [
        [
            InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
            InlineKeyboardButton("🇨🇳 中文", callback_data="lang_zh")
        ],
        [
            InlineKeyboardButton(
                await translate_text("🔙 Back", user_lang), 
                callback_data="settings"
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        await translate_text("🌐 Choose your language:", user_lang),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def set_language_callback(query, lang_code):
    """Set user language"""
    user_id = query.from_user.id if query.from_user else None
    if not user_id:
        return
    
    try:
        await set_user_language(user_id, lang_code)
        
        message = await translate_text(
            f"✅ Language updated to {lang_code.upper()}",
            lang_code
        )
        
        keyboard = [
            [
                InlineKeyboardButton(
                    await translate_text("⚙️ Settings", lang_code), 
                    callback_data="settings"
                )
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error setting language: {e}")
        await query.edit_message_text("❌ Error updating language")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates"""
    logger.error('Update "%s" caused error "%s"', update, context.error)

# Additional callback functions would be implemented here
async def subscribe_callback(query, user_lang):
    """Handle subscribe callback"""
    # Implementation similar to subscribe_handler but for callback queries
    pass

async def unsubscribe_callback(query, user_lang):
    """Handle unsubscribe callback"""
    # Implementation similar to unsubscribe_handler but for callback queries
    pass

async def settings_callback(query, user_lang):
    """Handle settings callback"""
    # Implementation similar to settings_handler but for callback queries
    pass

async def history_callback(query, user_lang):
    """Handle history callback"""
    # Implementation similar to history_handler but for callback queries
    pass

async def help_callback(query, user_lang):
    """Handle help callback"""
    # Implementation similar to help_handler but for callback queries
    pass

async def settings_submenu_callback(query, callback_data, user_lang):
    """Handle settings submenu callbacks"""
    # Implementation for settings submenus
    pass 