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
        # Handle different data formats - check for both 'value' and 'score' fields
        current_value = data.get("value") or data.get("score", 0)
        timestamp = data.get("timestamp", datetime.now())
        previous_value = data.get("previous_value") or data.get("previous_close", current_value)
        
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

async def format_historical_data_enhanced(
    historical_records: List, 
    days: int = 7,
    user_timezone: str = "UTC",
    language: str = "zh"
) -> str:
    """增强版历史数据格式化函数"""
    try:
        from data.models import FearGreedData
        
        if not historical_records:
            return "❌ 暂无历史数据"
        
        # 导入时区相关模块
        try:
            from zoneinfo import ZoneInfo
        except ImportError:
            import pytz
            ZoneInfo = None
        
        # 转换为字典格式并按日期排序
        data_points = []
        for record in historical_records:
            if isinstance(record, FearGreedData):
                # 时区转换
                record_time = record.date
                if ZoneInfo:
                    try:
                        if record_time.tzinfo is None:
                            record_time = record_time.replace(tzinfo=ZoneInfo('UTC'))
                        user_time = record_time.astimezone(ZoneInfo(user_timezone))
                    except:
                        user_time = record_time
                else:
                    try:
                        if record_time.tzinfo is None:
                            utc_time = pytz.UTC.localize(record_time)
                        else:
                            utc_time = record_time
                        user_tz = pytz.timezone(user_timezone)
                        user_time = utc_time.astimezone(user_tz)
                    except:
                        user_time = record_time
                
                data_points.append({
                    'value': record.current_value,
                    'rating': record.rating,
                    'date': record.date,
                    'display_time': user_time,
                    'previous_close': record.previous_close,
                    'week_ago': record.week_ago,
                    'month_ago': record.month_ago,
                    'year_ago': record.year_ago
                })
        
        # 按日期降序排序
        data_points.sort(key=lambda x: x['date'], reverse=True)
        
        if not data_points:
            return "❌ 历史数据格式错误"
        
        # 构建消息
        message = f"📈 **恐慌贪婪指数历史 ({days}天)**\n\n"
        
        # 最新数据
        latest = data_points[0]
        sentiment = get_sentiment_text(latest['value'], language)
        emoji = get_sentiment_emoji(latest['value'])
        
        formatted_time = latest['display_time'].strftime("%m月%d日 %H:%M")
        message += f"📊 **最新数据:** {latest['value']} - {sentiment} {emoji}\n"
        message += f"🕐 **更新时间:** {formatted_time}\n\n"
        
        # 计算统计信息
        values = [dp['value'] for dp in data_points]
        stats = calculate_market_statistics(values, days)
        
        if stats:
            message += f"📊 **{days}天统计信息:**\n"
            message += f"• 平均值: {stats['average']:.1f}\n"
            message += f"• 最高值: {stats['max']} {get_sentiment_emoji(stats['max'])}\n"
            message += f"• 最低值: {stats['min']} {get_sentiment_emoji(stats['min'])}\n"
            message += f"• 波动幅度: {stats['volatility']}\n\n"
            
            # 情绪分布统计
            dist = stats.get('sentiment_distribution', {})
            if dist:
                message += f"📈 **情绪分布统计:**\n"
                if dist['extreme_fear'] > 0:
                    message += f"• 极度恐慌: {dist['extreme_fear']}天 ({dist['extreme_fear']/len(values)*100:.1f}%)\n"
                if dist['fear'] > 0:
                    message += f"• 恐慌: {dist['fear']}天 ({dist['fear']/len(values)*100:.1f}%)\n"
                if dist['neutral'] > 0:
                    message += f"• 中性: {dist['neutral']}天 ({dist['neutral']/len(values)*100:.1f}%)\n"
                if dist['greed'] > 0:
                    message += f"• 贪婪: {dist['greed']}天 ({dist['greed']/len(values)*100:.1f}%)\n"
                if dist['extreme_greed'] > 0:
                    message += f"• 极度贪婪: {dist['extreme_greed']}天 ({dist['extreme_greed']/len(values)*100:.1f}%)\n"
                message += "\n"
        else:
            avg_value = sum(values) / len(values)
            max_value = max(values)
            min_value = min(values)
            
            message += f"📊 **{days}天统计信息:**\n"
            message += f"• 平均值: {avg_value:.1f}\n"
            message += f"• 最高值: {max_value} {get_sentiment_emoji(max_value)}\n"
            message += f"• 最低值: {min_value} {get_sentiment_emoji(min_value)}\n"
            message += f"• 波动幅度: {max_value - min_value}\n\n"
        
        # 趋势分析
        if stats and 'trend_change' in stats:
            trend_change = stats['trend_change']
            direction = stats.get('trend_direction', 'stable')
            
            if direction == 'up':
                trend_text = f"📈 **趋势:** 市场情绪转向贪婪 (+{trend_change:.1f})"
            elif direction == 'down':
                trend_text = f"📉 **趋势:** 市场情绪转向恐慌 ({trend_change:.1f})"
            else:
                trend_text = "📊 **趋势:** 市场情绪相对稳定"
            
            message += f"{trend_text}\n\n"
        elif len(data_points) >= 3:
            # 备用趋势分析
            recent_values = values[:3]
            older_values = values[-3:] if len(values) >= 6 else values[3:6] if len(values) > 3 else values
            
            recent_avg = sum(recent_values) / len(recent_values)
            older_avg = sum(older_values) / len(older_values)
            
            trend_change = recent_avg - older_avg
            
            if abs(trend_change) > 5:
                if trend_change > 0:
                    trend_text = f"📈 **趋势:** 市场情绪转向贪婪 (+{trend_change:.1f})"
                else:
                    trend_text = f"📉 **趋势:** 市场情绪转向恐慌 ({trend_change:.1f})"
            else:
                trend_text = "📊 **趋势:** 市场情绪相对稳定"
            
            message += f"{trend_text}\n\n"
        
        # 显示最近几天的详细数据
        message += f"📅 **最近{min(7, len(data_points))}天详情:**\n"
        
        for i, dp in enumerate(data_points[:7]):
            date_str = dp['display_time'].strftime("%m/%d")
            value = dp['value']
            emoji = get_sentiment_emoji(value)
            
            # 计算与前一天的变化
            if i < len(data_points) - 1:
                prev_value = data_points[i + 1]['value']
                change = value - prev_value
                if change > 0:
                    change_str = f"(+{change})"
                elif change < 0:
                    change_str = f"({change})"
                else:
                    change_str = "(±0)"
            else:
                change_str = ""
            
            message += f"• {date_str}: {value} {emoji} {change_str}\n"
        
        # 添加简单的ASCII图表
        if len(data_points) >= 2:
            chart = generate_simple_chart(values[:min(14, len(values))])
            message += f"\n📊 **趋势图表 (最近{min(14, len(values))}天):**\n```\n{chart}\n```\n"
        
        # 添加数据来源和免责声明
        message += f"📝 **数据来源:** CNN Fear & Greed Index\n"
        message += f"⏰ **时区:** {user_timezone}\n"
        message += f"📊 **记录数量:** {len(data_points)} 条"
        
        return message
        
    except Exception as e:
        logger.error(f"Error formatting enhanced historical data: {e}")
        return f"❌ 格式化历史数据时出错: {str(e)}"

def generate_simple_chart(values: List[int], width: int = 30, height: int = 8) -> str:
    """生成简单的ASCII图表"""
    try:
        if not values or len(values) < 2:
            return "数据不足以生成图表"
        
        # 确保值在0-100范围内
        values = [max(0, min(100, v)) for v in values]
        
        # 创建图表矩阵
        chart = [[' ' for _ in range(width)] for _ in range(height)]
        
        # 计算每个数据点的位置
        for i, value in enumerate(values[:width]):
            x = i
            y = height - 1 - int((value / 100) * (height - 1))
            
            # 根据值选择字符
            if value >= 75:
                char = '🟢'  # 极度贪婪
            elif value >= 55:
                char = '🟡'  # 贪婪
            elif value >= 45:
                char = '⚪'  # 中性
            elif value >= 25:
                char = '🟠'  # 恐慌
            else:
                char = '🔴'  # 极度恐慌
            
            if x < width and 0 <= y < height:
                chart[y][x] = char
        
        # 添加网格线和标签
        result = []
        
        # 顶部标签
        result.append("100 ┬" + "─" * (width - 2) + "┐")
        
        # 图表内容
        for row_idx, row in enumerate(chart):
            if row_idx == height // 4:
                label = " 75 ├"
            elif row_idx == height // 2:
                label = " 50 ├"
            elif row_idx == 3 * height // 4:
                label = " 25 ├"
            else:
                label = "    │"
            
            result.append(label + "".join(row) + "│")
        
        # 底部标签
        result.append("  0 └" + "─" * (width - 2) + "┘")
        
        # 添加图例
        result.append("")
        result.append("🔴极度恐慌 🟠恐慌 ⚪中性 🟡贪婪 🟢极度贪婪")
        
        return "\n".join(result)
        
    except Exception as e:
        logger.error(f"Error generating chart: {e}")
        return "图表生成失败"

def calculate_market_statistics(values: List[int], days: int) -> Dict[str, Any]:
    """计算市场统计信息"""
    try:
        if not values:
            return {}
        
        stats = {
            'average': sum(values) / len(values),
            'max': max(values),
            'min': min(values),
            'volatility': max(values) - min(values),
            'days_count': len(values),
            'period': days
        }
        
        # 计算情绪分布
        extreme_fear = sum(1 for v in values if v <= 25)
        fear = sum(1 for v in values if 25 < v <= 45)
        neutral = sum(1 for v in values if 45 < v <= 55)
        greed = sum(1 for v in values if 55 < v <= 75)
        extreme_greed = sum(1 for v in values if v > 75)
        
        stats['sentiment_distribution'] = {
            'extreme_fear': extreme_fear,
            'fear': fear,
            'neutral': neutral,
            'greed': greed,
            'extreme_greed': extreme_greed
        }
        
        # 计算趋势
        if len(values) >= 3:
            recent_avg = sum(values[:3]) / 3
            if len(values) >= 6:
                older_avg = sum(values[-3:]) / 3
            else:
                older_avg = sum(values[3:]) / max(1, len(values) - 3)
            
            stats['trend_change'] = recent_avg - older_avg
            stats['trend_direction'] = 'up' if stats['trend_change'] > 5 else 'down' if stats['trend_change'] < -5 else 'stable'
        
        return stats
        
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        return {} 