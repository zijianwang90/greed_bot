"""
Scheduler Module
Handles periodic tasks like daily notifications and data updates
"""

import asyncio
import logging
from datetime import datetime, time, timezone, timedelta
from typing import Optional, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from telegram.ext import Application

from data.database import get_subscribed_users, update_last_notification, FearGreedRepository
from data.cache_service import get_smart_fetcher, force_refresh_data
from bot.utils import format_fear_greed_message, get_user_language
import config

logger = logging.getLogger(__name__)

class NotificationScheduler:
    """Handles scheduling of notifications and data updates"""
    
    def __init__(self, app: Application):
        self.app = app
        self.scheduler = AsyncIOScheduler()
        self.data_fetcher = get_smart_fetcher(cache_timeout_minutes=60)  # 1小时缓存超时
        
    async def start(self):
        """Start the scheduler"""
        if self.scheduler.running:
            logger.warning("Scheduler is already running, skipping start.")
            return

        try:
            # Add jobs
            await self._setup_jobs()
            
            # Start scheduler
            self.scheduler.start()
            logger.info("Notification scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Notification scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    async def _setup_jobs(self):
        """Setup all scheduled jobs"""
        try:
            # Daily notification check - runs every minute to check if any users need notifications
            self.scheduler.add_job(
                self._check_daily_notifications,
                trigger=IntervalTrigger(minutes=config.NOTIFICATION_CHECK_INTERVAL),
                id="daily_notification_check",
                name="Daily Notification Check",
                misfire_grace_time=60,
                coalesce=True,
                max_instances=1,
                replace_existing=True
            )
            
            # Data update job - runs every hour to fetch fresh market data
            self.scheduler.add_job(
                self._update_market_data,
                trigger=IntervalTrigger(minutes=config.DATA_UPDATE_INTERVAL),
                id="market_data_update",
                name="Market Data Update",
                misfire_grace_time=300,
                coalesce=True,
                max_instances=1,
                replace_existing=True
            )
            
            # Health check job - runs every 15 minutes
            self.scheduler.add_job(
                self._health_check,
                trigger=IntervalTrigger(minutes=15),
                id="health_check",
                name="Health Check",
                misfire_grace_time=60,
                coalesce=True,
                max_instances=1,
                replace_existing=True
            )
            
            # Cleanup job - runs daily at 02:00 UTC
            self.scheduler.add_job(
                self._cleanup_old_data,
                trigger=CronTrigger(hour=2, minute=0),
                id="cleanup_old_data",
                name="Cleanup Old Data",
                misfire_grace_time=3600,
                replace_existing=True
            )
            
            logger.info("Scheduled jobs set up successfully")
            
        except Exception as e:
            logger.error(f"Error setting up scheduled jobs: {e}")
            raise
    
    async def _check_daily_notifications(self):
        """Check if any users need to receive daily notifications"""
        try:
            current_time = datetime.now(timezone.utc)
            logger.debug(f"Checking daily notifications at {current_time}")
            
            # Get all subscribed users
            users = await get_subscribed_users()
            
            for user in users:
                try:
                    # Check if user needs notification
                    if await self._should_send_notification(user, current_time):
                        await self._send_daily_notification(user)
                        
                except Exception as e:
                    logger.error(f"Error processing notification for user {user.telegram_id}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in daily notification check: {e}")
    
    async def _should_send_notification(self, user, current_time: datetime) -> bool:
        """Check if user should receive notification now"""
        try:
            # Get user's notification time and timezone
            notification_time = user.push_time or config.DEFAULT_NOTIFICATION_TIME
            user_timezone = user.timezone or config.DEFAULT_TIMEZONE
            
            logger.debug(f"Checking notification for user {user.telegram_id}: time={notification_time}, tz={user_timezone}")
            
            # Parse notification time
            hour, minute = map(int, notification_time.split(':'))
            
            # Convert current UTC time to user's timezone
            try:
                # Import timezone handling
                try:
                    from zoneinfo import ZoneInfo
                except ImportError:
                    # Fallback for Python < 3.9
                    import pytz
                    ZoneInfo = None
                
                if ZoneInfo is not None:
                    # Use zoneinfo (Python 3.9+)
                    user_tz = ZoneInfo(user_timezone)
                    user_current_time = current_time.astimezone(user_tz)
                else:
                    # Use pytz (Python < 3.9)
                    user_tz = pytz.timezone(user_timezone)
                    user_current_time = current_time.astimezone(user_tz)
                
                logger.debug(f"User {user.telegram_id} local time: {user_current_time}, target: {hour:02d}:{minute:02d}")
                
            except Exception as tz_error:
                logger.warning(f"Invalid timezone '{user_timezone}' for user {user.telegram_id}: {tz_error}, using UTC")
                user_current_time = current_time
            
            # Check if it's the right time to send notification (within 1 minute window)
            if (user_current_time.hour == hour and 
                user_current_time.minute == minute):
                
                # Check if we haven't already sent today
                last_notification = user.last_notification_sent
                if last_notification:
                    # Convert last notification to user timezone for comparison
                    try:
                        if ZoneInfo is not None:
                            last_notification_local = last_notification.astimezone(user_tz)
                        else:
                            last_notification_local = user_tz.normalize(user_tz.localize(last_notification.replace(tzinfo=None)) if last_notification.tzinfo is None else last_notification.astimezone(user_tz))
                        
                        last_date = last_notification_local.date()
                        current_date = user_current_time.date()
                        
                        logger.debug(f"User {user.telegram_id} last notification: {last_date}, current: {current_date}")
                        
                        if last_date >= current_date:
                            logger.debug(f"User {user.telegram_id} already received notification today")
                            return False  # Already sent today
                    except Exception as date_error:
                        logger.warning(f"Error comparing notification dates for user {user.telegram_id}: {date_error}")
                        # If there's an error, check based on UTC dates as fallback
                        last_date = last_notification.date() if last_notification.tzinfo else last_notification.date()
                        current_date = current_time.date()
                        if last_date >= current_date:
                            return False
                
                logger.info(f"User {user.telegram_id} should receive notification now")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking notification time for user {user.telegram_id}: {e}")
            return False
    
    async def _send_daily_notification(self, user):
        """Send daily notification to a user"""
        try:
            logger.info(f"Sending daily notification to user {user.telegram_id}")
            
            # Get current market data
            current_data = await self.data_fetcher.get_current_fear_greed_index()
            
            if not current_data:
                logger.warning(f"No market data available for notification to user {user.telegram_id}")
                return
            
            logger.debug(f"Market data for user {user.telegram_id}: {current_data}")
            
            # Get user language
            user_lang = user.language_code or config.DEFAULT_LANGUAGE
            
            # Format message
            message = await format_fear_greed_message(
                current_data, 
                user_lang, 
                include_details=config.INCLUDE_ANALYSIS
            )
            
            # Get current time in user's timezone for header
            try:
                # Import timezone handling
                try:
                    from zoneinfo import ZoneInfo
                except ImportError:
                    import pytz
                    ZoneInfo = None
                
                user_timezone = user.timezone or config.DEFAULT_TIMEZONE
                current_utc = datetime.now(timezone.utc)
                
                if ZoneInfo is not None:
                    user_tz = ZoneInfo(user_timezone)
                    user_time = current_utc.astimezone(user_tz)
                else:
                    user_tz = pytz.timezone(user_timezone)
                    user_time = current_utc.astimezone(user_tz)
                    
            except Exception as tz_error:
                logger.warning(f"Error getting user timezone for notification header: {tz_error}")
                user_time = datetime.now(timezone.utc)
            
            # Add daily notification header with user's local time
            if user_lang == "zh":
                header = "🌅 **每日市场情绪报告**\n"
                header += f"📅 {user_time.strftime('%Y年%m月%d日')}\n\n"
            else:
                header = "🌅 **Daily Market Sentiment Report**\n"
                header += f"📅 {user_time.strftime('%B %d, %Y')}\n\n"
            
            full_message = header + message
            
            logger.debug(f"Sending message to user {user.telegram_id}, length: {len(full_message)}")
            
            # Send message
            await self.app.bot.send_message(
                chat_id=user.telegram_id,
                text=full_message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
            # Update last notification time
            await update_last_notification(user.telegram_id, datetime.now(timezone.utc))
            
            logger.info(f"Daily notification sent successfully to user {user.telegram_id}")
            
        except Exception as e:
            logger.error(f"Error sending daily notification to user {user.telegram_id}: {e}", exc_info=True)
    
    async def _update_market_data(self):
        """Update market data cache"""
        try:
            logger.info("强制刷新市场数据缓存...")
            
            # 强制刷新缓存，获取最新数据
            current_data = await force_refresh_data()
            
            if current_data:
                logger.info(f"市场数据更新成功: Index={current_data.get('score')}, Source={current_data.get('source')}")
            else:
                logger.warning("市场数据更新失败")
                
        except Exception as e:
            logger.error(f"更新市场数据时出错: {e}")
    
    async def _health_check(self):
        """Perform health check"""
        try:
            logger.debug("Performing health check")
            
            # Check if we can fetch market data
            test_data = await self.data_fetcher.get_current_fear_greed_index()
            
            if not test_data:
                logger.warning("Health check failed: Unable to fetch market data")
            else:
                logger.debug("Health check passed")
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old data and logs"""
        try:
            logger.info("开始清理旧数据...")
            
            # 清理超过30天的恐慌贪婪指数数据
            cleaned_count = await FearGreedRepository.cleanup_old_data(days_to_keep=config.CACHE_CLEANUP_DAYS)
            
            logger.info(f"数据清理完成: 清理了 {cleaned_count} 条旧记录")
            
        except Exception as e:
            logger.error(f"数据清理过程中出错: {e}")
    
    async def send_immediate_notification(self, user_id: int, message: str):
        """Send immediate notification to a specific user"""
        try:
            await self.app.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
            logger.info(f"Immediate notification sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error sending immediate notification to user {user_id}: {e}")
    
    async def broadcast_message(self, message: str, language: Optional[str] = None):
        """Broadcast message to all subscribed users"""
        try:
            users = await get_subscribed_users()
            
            sent_count = 0
            failed_count = 0
            
            for user in users:
                try:
                    # Filter by language if specified
                    if language and user.language_code != language:
                        continue
                    
                    await self.app.bot.send_message(
                        chat_id=user.telegram_id,
                        text=message,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    
                    sent_count += 1
                    
                    # Rate limiting - small delay between messages
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error broadcasting to user {user.telegram_id}: {e}")
                    failed_count += 1
                    continue
            
            logger.info(f"Broadcast completed: {sent_count} sent, {failed_count} failed")
            
        except Exception as e:
            logger.error(f"Error during broadcast: {e}")
    
    def get_scheduler_status(self) -> dict:
        """Get scheduler status information"""
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger)
                })
            
            return {
                "running": self.scheduler.running,
                "jobs": jobs
            }
            
        except Exception as e:
            logger.error(f"Error getting scheduler status: {e}")
            return {"running": False, "jobs": [], "error": str(e)}

# Global scheduler instance
_scheduler_instance: Optional[NotificationScheduler] = None

async def setup_scheduler(app: Application) -> NotificationScheduler:
    """Setup and return scheduler instance"""
    global _scheduler_instance
    
    try:
        _scheduler_instance = NotificationScheduler(app)
        await _scheduler_instance.start()
        return _scheduler_instance
        
    except Exception as e:
        logger.error(f"Error setting up scheduler: {e}")
        raise

def get_scheduler() -> Optional[NotificationScheduler]:
    """Get current scheduler instance"""
    return _scheduler_instance

async def shutdown_scheduler():
    """Shutdown scheduler gracefully"""
    global _scheduler_instance
    
    if _scheduler_instance:
        _scheduler_instance.stop()
        _scheduler_instance = None
        logger.info("Scheduler shutdown completed")

# Utility functions for manual operations

async def send_test_notification(user_id: int) -> bool:
    """Send test notification to a user"""
    try:
        scheduler = get_scheduler()
        if not scheduler:
            return False
        
        test_message = "🧪 **Test Notification**\n\nThis is a test message from the Fear & Greed Index Bot."
        await scheduler.send_immediate_notification(user_id, test_message)
        return True
        
    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        return False

async def trigger_manual_broadcast(message: str, admin_user_id: int) -> bool:
    """Manually trigger broadcast message (admin only)"""
    try:
        if config.ADMIN_USER_ID and admin_user_id != int(config.ADMIN_USER_ID):
            logger.warning(f"Unauthorized broadcast attempt by user {admin_user_id}")
            return False
        
        scheduler = get_scheduler()
        if not scheduler:
            return False
        
        await scheduler.broadcast_message(message)
        return True
        
    except Exception as e:
        logger.error(f"Error in manual broadcast: {e}")
        return False

async def force_data_update() -> bool:
    """Force immediate data update"""
    try:
        scheduler = get_scheduler()
        if not scheduler:
            return False
        
        await scheduler._update_market_data()
        return True
        
    except Exception as e:
        logger.error(f"Error forcing data update: {e}")
        return False

async def trigger_test_notification(user_id: int) -> bool:
    """Trigger immediate test notification for a specific user (admin only)"""
    try:
        logger.info(f"Starting test notification for user {user_id}")
        
        # Check if scheduler is available
        scheduler = get_scheduler()
        if not scheduler:
            logger.error("Scheduler not available for test notification")
            return False
        
        logger.debug(f"Scheduler available, checking user {user_id}")
        
        # Get user from database
        from data.database import UserRepository
        user = await UserRepository.get_user_by_telegram_id(user_id)
        if not user:
            logger.error(f"User {user_id} not found in database for test notification")
            return False
        
        logger.debug(f"User {user_id} found: subscribed={user.is_subscribed}, tz={user.timezone}")
        
        if not user.is_subscribed:
            logger.warning(f"User {user_id} is not subscribed, sending test notification anyway")
        
        # Check if we have market data
        current_data = await scheduler.data_fetcher.get_current_fear_greed_index()
        if not current_data:
            logger.error(f"No market data available for test notification to user {user_id}")
            return False
        
        logger.debug(f"Market data available for user {user_id}: {current_data}")
        
        # Send test notification
        await scheduler._send_daily_notification(user)
        logger.info(f"Test notification sent successfully to user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending test notification to user {user_id}: {e}", exc_info=True)
        return False

async def check_notification_status() -> dict:
    """Get notification status for debugging"""
    try:
        logger.debug("Checking notification status...")
        
        from data.database import get_subscribed_users
        
        scheduler = get_scheduler()
        current_time = datetime.now(timezone.utc)
        
        # Initialize status with basic info
        status = {
            "scheduler_running": scheduler and scheduler.scheduler.running if scheduler else False,
            "current_utc_time": current_time.strftime('%Y-%m-%d %H:%M:%S UTC'),
            "subscribed_users_count": 0,
            "users_ready_for_notification": 0,
            "user_details": []
        }
        
        try:
            users = await get_subscribed_users()
            status["subscribed_users_count"] = len(users)
            logger.debug(f"Found {len(users)} subscribed users")
        except Exception as db_error:
            logger.error(f"Error getting subscribed users: {db_error}")
            return {**status, "error": f"Database error: {str(db_error)}"}
        
        if scheduler and users:
            for user in users:
                try:
                    should_notify = await scheduler._should_send_notification(user, current_time)
                    user_info = {
                        "user_id": user.telegram_id,
                        "push_time": user.push_time or "09:00",
                        "timezone": user.timezone or "UTC", 
                        "last_notification": user.last_notification_sent.strftime('%Y-%m-%d %H:%M:%S') if user.last_notification_sent else None,
                        "should_notify_now": should_notify
                    }
                    status["user_details"].append(user_info)
                    
                    if should_notify:
                        status["users_ready_for_notification"] += 1
                        
                except Exception as user_error:
                    logger.warning(f"Error processing user {user.telegram_id}: {user_error}")
                    # Add user with error info
                    status["user_details"].append({
                        "user_id": user.telegram_id,
                        "error": str(user_error)
                    })
        
        logger.debug(f"Notification status check completed: {status['users_ready_for_notification']} ready")
        return status
        
    except Exception as e:
        logger.error(f"Error checking notification status: {e}", exc_info=True)
        return {"error": str(e)} 