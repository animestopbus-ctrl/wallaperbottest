"""
LastPerson07Bot Scheduler Module
Handles automatic wallpaper posting schedules
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from telegram import Bot

from config.config import LastPerson07Config

logger = logging.getLogger(__name__)

class LastPerson07Scheduler:
    """Task scheduler for automatic wallpaper posting"""
    
    def __init__(self, db_client, bot: Bot, config: LastPerson07Config):
        """Initialize the scheduler"""
        self.db_client = db_client
        self.bot = bot
        self.config = config
        self.scheduler = AsyncIOScheduler()
        
        # Schedule intervals in minutes
        self.intervals = {
            'hourly': 60,
            'daily': 24 * 60,
            'weekly': 7 * 24 * 60,
            'monthly': 30 * 24 * 60
        }
    
    async def start(self) -> None:
        """Start the scheduler and load existing schedules"""
        try:
            # Start scheduler
            self.scheduler.start()
            
            # Load existing schedules from database
            await self.load_schedules()
            
            # Add cleanup job
            self.scheduler.add_job(
                func=self.cleanup_expired_schedules,
                trigger=IntervalTrigger(hours=1),
                id='cleanup_job',
                name='Cleanup expired schedules',
                replace_existing=True
            )
            
            logger.info("✅ Scheduler started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the scheduler and cleanup resources"""
        try:
            # Stop scheduler
            self.scheduler.shutdown(wait=True)
            
            logger.info("✅ Scheduler stopped successfully")
            
        except Exception as e:
            logger.error(f"❌ Error stopping scheduler: {e}")
    
    async def load_schedules(self) -> None:
        """Load all active schedules from database"""
        try:
            schedules = await self.db_client.get_all_schedules()
            
            for schedule in schedules:
                await self.add_schedule_job(schedule)
            
            logger.info(f"✅ Loaded {len(schedules)} schedules from database")
            
        except Exception as e:
            logger.error(f"❌ Error loading schedules: {e}")
    
    async def add_schedule_job(self, schedule: Dict[str, Any]) -> None:
        """Add a schedule job to the scheduler"""
        try:
            chat_id = schedule['chat_id']
            category = schedule['category']
            interval = schedule['interval']
            
            # Create job ID
            job_id = f"schedule_{chat_id}_{category}_{interval}"
            
            # Remove existing job if any
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            # Calculate trigger based on interval
            if interval == 'hourly':
                trigger = IntervalTrigger(minutes=self.intervals['hourly'])
            elif interval == 'daily':
                trigger = IntervalTrigger(hours=24)
            elif interval == 'weekly':
                trigger = IntervalTrigger(days=7)
            elif interval == 'monthly':
                trigger = IntervalTrigger(days=30)
            else:
                # Custom interval in minutes
                trigger = IntervalTrigger(minutes=int(interval))
            
            # Add job to scheduler
            self.scheduler.add_job(
                func=self.post_scheduled_wallpaper,
                trigger=trigger,
                args=[chat_id, category, schedule.get('user_id')],
                id=job_id,
                name=f"Schedule for {chat_id} - {category}",
                replace_existing=True
            )
            
            logger.info(f"✅ Added schedule job: {job_id}")
            
        except Exception as e:
            logger.error(f"❌ Error adding schedule job: {e}")
    
    async def remove_schedule_job(self, chat_id: int, category: str, interval: str) -> None:
        """Remove a schedule job from the scheduler"""
        try:
            job_id = f"schedule_{chat_id}_{category}_{interval}"
            
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                logger.info(f"✅ Removed schedule job: {job_id}")
            
        except Exception as e:
            logger.error(f"❌ Error removing schedule job: {e}")
    
    async def post_scheduled_wallpaper(self, chat_id: int, category: str, user_id: Optional[int] = None) -> None:
        """Post a scheduled wallpaper to a chat"""
        try:
            # Check if maintenance mode is enabled
            maintenance = await self.db_client.get_setting('maintenance')
            if maintenance:
                logger.info(f"Skipping scheduled post due to maintenance mode")
                return
            
            # Import fetcher here to avoid circular imports
            from utils.fetcher import LastPerson07WallpaperFetcher
            fetcher = LastPerson07WallpaperFetcher(self.db_client, self.config)
            await fetcher.initialize()
            
            # Fetch wallpaper
            wallpaper_info = await fetcher.fetch_wallpaper(category)
            
            if not wallpaper_info:
                logger.error(f"Failed to fetch scheduled wallpaper for chat {chat_id}")
                return
            
            # Download image
            image_data = await fetcher.download_image(wallpaper_info['url'])
            if not image_data:
                logger.error(f"Failed to download scheduled wallpaper for chat {chat_id}")
                return
            
            # Create caption
            caption = f"""
🎨 **Scheduled Wallpaper**

📂 Category: {category.title()}
📏 Size: {wallpaper_info['width']}×{wallpaper_info['height']}
📸 Photo by {wallpaper_info.get('photographer', 'Unknown')} on {wallpaper_info['source'].title()}
🔗 [Download]({wallpaper_info.get('download_url', '#')})

💫 "Beauty delivered automatically to your chat!" 💫
"""
            
            # Send to chat
            message = await self.bot.send_photo(
                chat_id=chat_id,
                photo=image_data,
                caption=caption,
                parse_mode='Markdown'
            )
            
            # Set random reaction
            from utils.reactions import LastPerson07Reactions
            reactions = LastPerson07Reactions()
            await reactions.set_random_reaction(self.bot, chat_id, message.message_id)
            
            # Update schedule in database
            await self.db_client.update_schedule_last_post(chat_id, category)
            
            # Log the post
            await self.db_client.log_event(
                level='INFO',
                message=f"Scheduled wallpaper sent to chat {chat_id}"
            )
            
            logger.info(f"✅ Sent scheduled wallpaper to chat {chat_id}")
            
        except Exception as e:
            logger.error(f"❌ Error posting scheduled wallpaper: {e}")
    
    async def cleanup_expired_schedules(self) -> None:
        """Clean up expired schedules and perform maintenance"""
        try:
            # Clean up expired premium users
            expired_users = await self.get_expired_premium_users()
            for user in expired_users:
                await self.db_client.set_user_tier(user['_id'], 'free')
                logger.info(f"Cleaned up expired premium for user {user['_id']}")
            
            # Clean up old logs
            deleted_count = await self.db_client.cleanup_old_logs(days=30)
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old log entries")
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
    
    async def get_expired_premium_users(self) -> List[Dict[str, Any]]:
        """Get users whose premium subscription has expired"""
        try:
            users_collection = self.db_client.database[self.db_client.COLLECTIONS['users']]
            
            now = datetime.utcnow()
            cursor = users_collection.find({
                'tier': 'premium',
                'expiration': {'$lt': now}
            })
            
            return await cursor.to_list(length=None)
            
        except Exception as e:
            logger.error(f"❌ Error getting expired premium users: {e}")
            return []
