"""
Bot Utility Functions
Helper functions for message formatting, translations, and common operations
"""

import re
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

import config
from data.database import get_user, update_user_settings

logger = logging.getLogger(__name__)

# Translation dictionaries
TRANSLATIONS = {
    "en": {
        # Greetings and basic messages
        "welcome": "Welcome to CNN Fear & Greed Index Bot!",
        "error": "❌ Sorry, there was an error. Please try again later.",
        "loading": "📊 Loading...",
        "success": "✅ Success!",
        "failed": "❌ Failed",
        
        # Commands
        "current_index": "📊 Current Index",
        "subscribe": "🔔 Subscribe",
        "unsubscribe": "❌ Unsubscribe",
        "settings": "⚙️ Settings",
        "history": "📈 History",
        "help": "❓ Help",
        "language": "🌐 Language",
        "refresh": "🔄 Refresh",
        "back": "🔙 Back",
        
        # Market sentiment
        "extreme_fear": "Extreme Fear",
        "fear": "Fear",
        "neutral": "Neutral",
        "greed": "Greed",
        "extreme_greed": "Extreme Greed",
        
        # Time and dates
        "today": "Today",
        "yesterday": "Yesterday",
        "week_ago": "1 week ago",
        "month_ago": "1 month ago",
        
        # Analysis
        "market_sentiment": "Market Sentiment",
        "trend_analysis": "Trend Analysis",
        "historical_comparison": "Historical Comparison",
        "key_indicators": "Key Indicators",
        
        # Settings
        "notification_time": "Notification Time",
        "timezone": "Timezone",
        "subscription_status": "Subscription Status",
        "subscribed": "Subscribed",
        "not_subscribed": "Not Subscribed",
        
        # Market indicators
        "vix_index": "VIX Index",
        "put_call_ratio": "Put/Call Ratio",
        "market_momentum": "Market Momentum",
        "safe_haven_demand": "Safe Haven Demand",
        "junk_bond_demand": "Junk Bond Demand",
        "stock_price_strength": "Stock Price Strength",
        "stock_price_breadth": "Stock Price Breadth",
    },
    "zh": {
        # Greetings and basic messages
        "welcome": "欢迎使用CNN恐慌贪婪指数Bot！",
        "error": "❌ 抱歉，出现了错误。请稍后重试。",
        "loading": "📊 加载中...",
        "success": "✅ 成功！",
        "failed": "❌ 失败",
        
        # Commands
        "current_index": "📊 当前指数",
        "subscribe": "🔔 订阅",
        "unsubscribe": "❌取消订阅",
        "settings": "⚙️ 设置",
        "history": "📈 历史",
        "help": "❓ 帮助",
        "language": "🌐 语言",
        "refresh": "🔄 刷新",
        "back": "🔙 返回",
        
        # Market sentiment
        "extreme_fear": "极度恐慌",
        "fear": "恐慌",
        "neutral": "中性",
        "greed": "贪婪",
        "extreme_greed": "极度贪婪",
        
        # Time and dates
        "today": "今天",
        "yesterday": "昨天",
        "week_ago": "一周前",
        "month_ago": "一个月前",
        
        # Analysis
        "market_sentiment": "市场情绪",
        "trend_analysis": "趋势分析",
        "historical_comparison": "历史对比",
        "key_indicators": "关键指标",
        
        # Settings
        "notification_time": "通知时间",
        "timezone": "时区",
        "subscription_status": "订阅状态",
        "subscribed": "已订阅",
        "not_subscribed": "未订阅",
        
        # Market indicators
        "vix_index": "VIX指数",
        "put_call_ratio": "Put/Call比率",
        "market_momentum": "市场动量",
        "safe_haven_demand": "避险需求",
        "junk_bond_demand": "垃圾债券需求",
        "stock_price_strength": "股价强度",
        "stock_price_breadth": "股价广度",
    }
}

async def translate_text(text: str, language: str = "en") -> str:
    """
    Translate text based on language preference
    
    Args:
        text: Text to translate (can contain placeholders)
        language: Target language code
    
    Returns:
        Translated text
    """
    if language not in TRANSLATIONS:
        language = "en"
    
    # For complex text, return as-is for now
    # In a production system, you might want to use a proper translation service
    return text

async def get_user_language(user_id: int) -> str:
    """Get user's preferred language"""
    try:
        user = await get_user(user_id)
        if user and user.language_code:
            return user.language_code
        return config.DEFAULT_LANGUAGE
    except Exception as e:
        logger.error(f"Error getting user language: {e}")
        return config.DEFAULT_LANGUAGE

async def set_user_language(user_id: int, language: str) -> bool:
    """Set user's preferred language"""
    try:
        if language not in config.SUPPORTED_LANGUAGES:
            return False
        
        await update_user_settings(user_id, language_code=language)
        return True
    except Exception as e:
        logger.error(f"Error setting user language: {e}")
        return False

def get_sentiment_emoji(value: float) -> str:
    """Get emoji based on fear & greed index value"""
    if value <= 24:
        return "😨"  # Extreme Fear
    elif value <= 49:
        return "😟"  # Fear
    elif value == 50:
        return "😐"  # Neutral
    elif value <= 74:
        return "😃"  # Greed
    else:
        return "🤑"  # Extreme Greed

def get_sentiment_text(value: float, language: str = "en") -> str:
    """Get sentiment text based on fear & greed index value"""
    sentiment_map = {
        "en": {
            "extreme_fear": "Extreme Fear",
            "fear": "Fear", 
            "neutral": "Neutral",
            "greed": "Greed",
            "extreme_greed": "Extreme Greed"
        },
        "zh": {
            "extreme_fear": "极度恐慌",
            "fear": "恐慌",
            "neutral": "中性", 
            "greed": "贪婪",
            "extreme_greed": "极度贪婪"
        }
    }
    
    lang_map = sentiment_map.get(language, sentiment_map["en"])
    
    if value <= 24:
        return lang_map["extreme_fear"]
    elif value <= 49:
        return lang_map["fear"]
    elif value == 50:
        return lang_map["neutral"]
    elif value <= 74:
        return lang_map["greed"]
    else:
        return lang_map["extreme_greed"]

def get_trend_arrow(current: float, previous: float) -> str:
    """Get trend arrow based on value comparison"""
    if current > previous:
        return "📈"
    elif current < previous:
        return "📉"
    else:
        return "➡️"

def get_change_text(current: float, previous: float) -> str:
    """Get change text with appropriate formatting"""
    diff = current - previous
    if diff > 0:
        return f"+{diff:.1f}"
    elif diff < 0:
        return f"{diff:.1f}"
    else:
        return "0.0"

async def format_fear_greed_message(
    data: Dict[str, Any], 
    language: str = "en", 
    include_details: bool = False
) -> str:
    """
    Format fear & greed index data into a message
    
    Args:
        data: Market data dictionary
        language: Language for formatting
        include_details: Whether to include detailed analysis
    
    Returns:
        Formatted message string
    """
    try:
        current_value = data.get("value", 0)
        timestamp = data.get("timestamp", datetime.now())
        previous_value = data.get("previous_value", current_value)
        
        # Format timestamp
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        emoji = get_sentiment_emoji(current_value)
        sentiment = get_sentiment_text(current_value, language)
        trend_arrow = get_trend_arrow(current_value, previous_value)
        change = get_change_text(current_value, previous_value)
        
        # Basic message
        message = f"📊 **CNN Fear & Greed Index**\n\n"
        message += f"🎯 **{current_value:.0f} - {sentiment}** {emoji}\n"
        
        if previous_value != current_value:
            message += f"📊 {trend_arrow} {change} from yesterday\n"
        
        message += f"🗓️ Updated: {timestamp.strftime('%B %d, %Y at %H:%M UTC')}\n\n"
        
        # Add scale reference
        if language == "zh":
            message += "📊 **指数范围：**\n"
            message += "• 0-24: 极度恐慌 😨\n"
            message += "• 25-49: 恐慌 😟\n" 
            message += "• 50: 中性 😐\n"
            message += "• 51-74: 贪婪 😃\n"
            message += "• 75-100: 极度贪婪 🤑\n"
        else:
            message += "📊 **Index Scale:**\n"
            message += "• 0-24: Extreme Fear 😨\n"
            message += "• 25-49: Fear 😟\n"
            message += "• 50: Neutral 😐\n" 
            message += "• 51-74: Greed 😃\n"
            message += "• 75-100: Extreme Greed 🤑\n"
        
        # Add detailed analysis if requested
        if include_details and config.INCLUDE_ANALYSIS:
            analysis = get_market_analysis(current_value, language)
            if analysis:
                message += f"\n🔍 **Analysis:**\n{analysis}\n"
        
        # Add disclaimer
        if language == "zh":
            message += "\n⚠️ **免责声明：** 此信息仅供教育目的。投资前请自行研究。"
        else:
            message += "\n⚠️ **Disclaimer:** This information is for educational purposes only. Always do your own research before investing."
        
        return message
        
    except Exception as e:
        logger.error(f"Error formatting fear greed message: {e}")
        return "❌ Error formatting market data"

async def format_historical_message(
    historical_data: List[Dict[str, Any]], 
    language: str = "en"
) -> str:
    """Format historical data into a message"""
    try:
        if not historical_data:
            return "❌ No historical data available"
        
        # Sort data by date
        historical_data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        current = historical_data[0] if historical_data else None
        week_ago = None
        month_ago = None
        
        # Find week and month ago data
        now = datetime.now(timezone.utc)
        for item in historical_data:
            timestamp = item.get("timestamp")
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            days_diff = (now - timestamp).days
            
            if not week_ago and 6 <= days_diff <= 8:
                week_ago = item
            if not month_ago and 28 <= days_diff <= 32:
                month_ago = item
        
        if language == "zh":
            message = "📈 **恐慌贪婪指数历史**\n\n"
        else:
            message = "📈 **Fear & Greed Index History**\n\n"
        
        # Current value
        if current:
            value = current.get("value", 0)
            sentiment = get_sentiment_text(value, language)
            emoji = get_sentiment_emoji(value)
            
            if language == "zh":
                message += f"📊 **今日:** {value:.0f} - {sentiment} {emoji}\n"
            else:
                message += f"📊 **Today:** {value:.0f} - {sentiment} {emoji}\n"
        
        # Week ago comparison
        if week_ago:
            week_value = week_ago.get("value", 0)
            current_value = current.get("value", 0) if current else 0
            change = get_change_text(current_value, week_value)
            arrow = get_trend_arrow(current_value, week_value)
            
            if language == "zh":
                message += f"📅 **一周前:** {week_value:.0f} ({change} {arrow})\n"
            else:
                message += f"📅 **1 week ago:** {week_value:.0f} ({change} {arrow})\n"
        
        # Month ago comparison
        if month_ago:
            month_value = month_ago.get("value", 0)
            current_value = current.get("value", 0) if current else 0
            change = get_change_text(current_value, month_value)
            arrow = get_trend_arrow(current_value, month_value)
            
            if language == "zh":
                message += f"📅 **一个月前:** {month_value:.0f} ({change} {arrow})\n"
            else:
                message += f"📅 **1 month ago:** {month_value:.0f} ({change} {arrow})\n"
        
        # Add trend analysis
        if len(historical_data) >= 7:
            trend = analyze_trend(historical_data[:7], language)
            message += f"\n{trend}"
        
        return message
        
    except Exception as e:
        logger.error(f"Error formatting historical message: {e}")
        return "❌ Error formatting historical data"

def analyze_trend(data: List[Dict[str, Any]], language: str = "en") -> str:
    """Analyze trend from recent data"""
    try:
        if len(data) < 3:
            return ""
        
        values = [item.get("value", 0) for item in data]
        
        # Calculate simple trend
        recent_avg = sum(values[:3]) / 3
        older_avg = sum(values[-3:]) / 3
        
        if recent_avg > older_avg + 5:
            if language == "zh":
                trend = "📈 **趋势:** 市场情绪转向更加贪婪"
            else:
                trend = "📈 **Trend:** Market sentiment becoming more greedy"
        elif recent_avg < older_avg - 5:
            if language == "zh":
                trend = "📉 **趋势:** 市场情绪转向更加恐慌"
            else:
                trend = "📉 **Trend:** Market sentiment becoming more fearful"
        else:
            if language == "zh":
                trend = "➡️ **趋势:** 市场情绪相对稳定"
            else:
                trend = "➡️ **Trend:** Market sentiment relatively stable"
        
        return trend
        
    except Exception as e:
        logger.error(f"Error analyzing trend: {e}")
        return ""

def get_market_analysis(value: float, language: str = "en") -> str:
    """Get market analysis based on current value"""
    try:
        if language == "zh":
            if value <= 24:
                return "市场处于极度恐慌状态，可能是买入机会，但需谨慎。历史上这种水平通常伴随着市场底部。"
            elif value <= 49:
                return "市场情绪偏向恐慌，投资者较为谨慎。这可能预示着市场调整或横盘整理。"
            elif value == 50:
                return "市场情绪中性，投资者态度平衡。市场可能处于观望状态。"
            elif value <= 74:
                return "市场情绪偏向贪婪，投资者信心较高。需关注是否过度乐观。"
            else:
                return "市场处于极度贪婪状态，投资者情绪高涨。历史上这种水平可能预示着市场顶部，需要谨慎。"
        else:
            if value <= 24:
                return "Market is in extreme fear, potentially a buying opportunity but use caution. Historically, these levels often coincide with market bottoms."
            elif value <= 49:
                return "Market sentiment leans toward fear, investors are cautious. This may signal market correction or consolidation."
            elif value == 50:
                return "Market sentiment is neutral, investor attitudes are balanced. Market may be in a wait-and-see mode."
            elif value <= 74:
                return "Market sentiment leans toward greed, investor confidence is high. Watch for signs of overoptimism."
            else:
                return "Market is in extreme greed, investor sentiment is euphoric. Historically, these levels may signal market tops, exercise caution."
    except Exception as e:
        logger.error(f"Error getting market analysis: {e}")
        return ""

def validate_time_format(time_str: str) -> bool:
    """Validate time format (HH:MM)"""
    try:
        pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
        return bool(pattern.match(time_str))
    except Exception:
        return False

def validate_timezone(timezone_str: str) -> bool:
    """Validate timezone string"""
    try:
        # Basic validation - in production you might want to use pytz
        return timezone_str in [
            "UTC", "US/Eastern", "US/Central", "US/Mountain", "US/Pacific",
            "Europe/London", "Europe/Paris", "Europe/Berlin", "Asia/Tokyo",
            "Asia/Shanghai", "Asia/Hong_Kong", "Australia/Sydney"
        ]
    except Exception:
        return False

def format_number(value: float, decimals: int = 1) -> str:
    """Format number with appropriate decimal places"""
    try:
        return f"{value:.{decimals}f}"
    except Exception:
        return str(value)

def get_market_hours_status() -> Dict[str, Any]:
    """Get current market hours status"""
    try:
        now = datetime.now(timezone.utc)
        
        # US market hours (9:30 AM - 4:00 PM ET)
        # This is a simplified check - in production you'd want more sophisticated logic
        et_hour = (now.hour - 5) % 24  # Convert UTC to ET (simplified)
        
        is_open = (9.5 <= et_hour < 16) and (now.weekday() < 5)
        
        return {
            "is_open": is_open,
            "next_open": None,  # Would calculate next market open
            "timezone": "ET"
        }
    except Exception as e:
        logger.error(f"Error getting market hours: {e}")
        return {"is_open": False, "next_open": None, "timezone": "ET"}

def truncate_text(text: str, max_length: int = 4000) -> str:
    """Truncate text to fit Telegram message limits"""
    if len(text) <= max_length:
        return text
    
    # Truncate and add ellipsis
    return text[:max_length-3] + "..."

def escape_markdown(text: str) -> str:
    """Escape special characters for Telegram markdown"""
    # Characters that need to be escaped in Telegram MarkdownV2
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

def format_percentage(value: float, include_sign: bool = True) -> str:
    """Format percentage value"""
    try:
        if include_sign and value > 0:
            return f"+{value:.1f}%"
        else:
            return f"{value:.1f}%"
    except Exception:
        return "N/A"

async def create_inline_keyboard(buttons: List[List[Dict[str, str]]], language: str = "en") -> List[List]:
    """Create inline keyboard from button configuration"""
    try:
        from telegram import InlineKeyboardButton
        
        keyboard = []
        for row in buttons:
            keyboard_row = []
            for button in row:
                text = await translate_text(button["text"], language)
                keyboard_row.append(InlineKeyboardButton(text, callback_data=button["callback_data"]))
            keyboard.append(keyboard_row)
        
        return keyboard
    except Exception as e:
        logger.error(f"Error creating inline keyboard: {e}")
        return [] 