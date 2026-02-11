"""
LastPerson07Bot Database Queries Module
Specialized database query operations
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class LastPerson07Queries:
    """Database query operations for LastPerson07Bot"""
    
    def __init__(self, db_client):
        """Initialize with database client"""
        self.db_client = db_client
    
    async def get_or_create_user(self, user_id: int, username: str, first_name: str) -> Dict[str, Any]:
        """Get user from database or create if not exists"""
        try:
            user = await self.db_client.get_user(user_id)
            
            if user:
                return user
            
            return await self.db_client.create_user(user_id, username, first_name)
            
        except Exception as e:
            logger.error(f"❌ Error in get_or_create_user: {e}")
            return {}
    
    async def can_user_fetch_today(self, user_id: int) -> tuple[bool, int]:
        """Check if user can fetch wallpapers today"""
        try:
            user = await self.db_client.get_user(user_id)
            
            if not user:
                return True, 5  # Default limit
            
            if user.get('banned', False):
                return False, 0
            
            if user.get('tier') == 'premium':
                return True, float('inf')  # Unlimited for premium
            
            # Check daily limit for free users
            today_fetches = await self._get_today_fetches(user_id)
            remaining = 5 - today_fetches  # Default limit
            
            return remaining > 0, max(0, remaining)
            
        except Exception as e:
            logger.error(f"❌ Error in can_user_fetch_today: {e}")
            return False, 0
    
    async def _get_today_fetches(self, user_id: int) -> int:
        """Get today's fetch count for user"""
        try:
            user = await self.db_client.get_user(user_id)
            
            if not user:
                return 0
            
            today = datetime.utcnow().date()
            last_fetch = user.get('last_fetch_date')
            
            if last_fetch and last_fetch.date() == today:
                return user.get('fetch_count', 0)
            else:
                # Reset count if it's a new day
                await self.db_client.update_user(user_id, {'fetch_count': 0})
                return 0
                
        except Exception as e:
            logger.error(f"❌ Error in _get_today_fetches: {e}")
            return 0
    
    async def record_wallpaper_fetch(self, user_id: int, wallpaper_info: Dict[str, Any]) -> None:
        """Record a wallpaper fetch event"""
        try:
            await self.db_client.update_user_fetch_count(user_id)
            await self.db_client.log_event(
                level='INFO',
                message=f"User {user_id} fetched wallpaper from {wallpaper_info.get('source', 'unknown')}",
                user_id=user_id
            )
            
        except Exception as e:
            logger.error(f"❌ Error in record_wallpaper_fetch: {e}")
    
    async def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive statistics for a user"""
        try:
            user = await self.db_client.get_user(user_id)
            
            if not user:
                return {}
            
            today_fetches = await self._get_today_fetches(user_id)
            
            return {
                'user_id': user_id,
                'username': user.get('username', 'Unknown'),
                'first_name': user.get('first_name', 'Unknown'),
                'tier': user.get('tier', 'free'),
                'total_fetches': user.get('fetch_count', 0),
                'today_fetches': today_fetches,
                'remaining_fetches': max(0, 5 - today_fetches) if user.get('tier') == 'free' else 'unlimited',
                'join_date': user.get('join_date'),
                'last_fetch': user.get('last_fetch_date'),
                'banned': user.get('banned', False),
                'premium_expires': user.get('expiration')
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_user_statistics: {e}")
            return {}
