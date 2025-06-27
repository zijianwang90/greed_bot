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

from data.database import get_subscribed_users, update_last_notification
from data.fetcher import DataFetcher
from bot.utils import format_fear_greed_message, get_user_language
import config

logger = logging.getLogger(__name__)

class NotificationScheduler:
    """Handles scheduling of notifications and data updates"""
    
    def __init__(self, app: Application):
        self.app = app
        self.scheduler = AsyncIOScheduler()
        self.data_fetcher = DataFetcher()
        
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
                    logger.error(f"Error processing notification for user {user.user_id}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in daily notification check: {e}")
    
    async def _should_send_notification(self, user, current_time: datetime) -> bool:
        """Check if user should receive notification now"""
        try:
            # Get user's notification time
            notification_time = user.push_time or config.DEFAULT_NOTIFICATION_TIME
            user_timezone = user.timezone or config.DEFAULT_TIMEZONE
            
            # Parse notification time
            hour, minute = map(int, notification_time.split(':'))
            
            # Convert to user's timezone (simplified - in production use proper timezone handling)
            user_current_time = current_time
            
            # Check if it's the right time to send notification
            if (user_current_time.hour == hour and 
                user_current_time.minute == minute):
                
                # Check if we haven't already sent today
                last_notification = user.last_notification_sent
                if last_notification:
                    last_date = last_notification.date()
                    current_date = current_time.date()
                    
                    if last_date >= current_date:
                        return False  # Already sent today
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking notification time for user {user.user_id}: {e}")
            return False
    
    async def _send_daily_notification(self, user):
        """Send daily notification to a user"""
        try:
            # Get current market data
            current_data = await self.data_fetcher.get_current_fear_greed_index()
            
            if not current_data:
                logger.warning(f"No market data available for notification to user {user.user_id}")
                return
            
            # Get user language
            user_lang = user.language_code or config.DEFAULT_LANGUAGE
            
            # Format message
            message = await format_fear_greed_message(
                current_data, 
                user_lang, 
                include_details=config.INCLUDE_ANALYSIS
            )
            
            # Add daily notification header
            if user_lang == "zh":
                header = "🌅 **每日市场情绪报告**\n"
                header += f"📅 {datetime.now().strftime('%Y年%m月%d日')}\n\n"
            else:
                header = "🌅 **Daily Market Sentiment Report**\n"
                header += f"📅 {datetime.now().strftime('%B %d, %Y')}\n\n"
            
            full_message = header + message
            
            # Send message
            await self.app.bot.send_message(
                chat_id=user.user_id,
                text=full_message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
            # Update last notification time
            await update_last_notification(user.user_id, datetime.now(timezone.utc))
            
            logger.info(f"Daily notification sent to user {user.user_id}")
            
        except Exception as e:
            logger.error(f"Error sending daily notification to user {user.user_id}: {e}")
    
    async def _update_market_data(self):
        """Update market data cache"""
        try:
            logger.debug("Updating market data cache")
            
            # Fetch current data to update cache
            current_data = await self.data_fetcher.get_current_fear_greed_index()
            
            if current_data:
                logger.debug("Market data updated successfully")
            else:
                logger.warning("Failed to update market data")
                
            # Also update VIX data if enabled
            if config.ENABLE_VIX_DATA:
                vix_data = await self.data_fetcher.get_vix_data()
                if vix_data:
                    logger.debug("VIX data updated successfully")
                
        except Exception as e:
            logger.error(f"Error updating market data: {e}")
    
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
            logger.info("Starting data cleanup")
            
            # This would clean up old data from database
            # Implementation depends on your database schema
            
            logger.info("Data cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during data cleanup: {e}")
    
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
                        chat_id=user.user_id,
                        text=message,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    
                    sent_count += 1
                    
                    # Rate limiting - small delay between messages
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error broadcasting to user {user.user_id}: {e}")
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