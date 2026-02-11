"""
LastPerson07Bot Broadcaster Module
Handles broadcasting messages to users, groups, and channels
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from telegram import Bot, Message
from telegram.error import TelegramError, BadRequest, Forbidden

logger = logging.getLogger(__name__)

class LastPerson07Broadcaster:
    """Handles broadcasting messages to various targets"""
    
    def __init__(self, db_client):
        """Initialize the broadcaster"""
        self.db_client = db_client
        
        # Broadcasting limits
        self.BROADCAST_LIMITS = {
            'users_per_minute': 30,
            'groups_per_minute': 10,
            'channels_per_minute': 5
        }
    
    async def broadcast_to_users(self, bot: Bot, message: str, target_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """Broadcast message to users (DMs)"""
        try:
            stats = {
                'target_type': 'users',
                'total_targets': 0,
                'successful': 0,
                'failed': 0,
                'blocked': 0,
                'errors': []
            }
            
            # Get target users
            if target_ids:
                target_users = target_ids
            else:
                # Get all active users
                users_collection = self.db_client.database[self.db_client.COLLECTIONS['users']]
                cursor = users_collection.find({'banned': False})
                users_data = await cursor.to_list(length=None)
                target_users = [user['_id'] for user in users_data]
            
            stats['total_targets'] = len(target_users)
            
            logger.info(f"📢 Starting broadcast to {len(target_users)} users")
            
            # Process users with rate limiting
            semaphore = asyncio.Semaphore(self.BROADCAST_LIMITS['users_per_minute'])
            
            async def send_to_user(user_id: int):
                async with semaphore:
                    try:
                        # Send message
                        message_obj = await bot.send_message(
                            chat_id=user_id,
                            text=message,
                            parse_mode='Markdown'
                        )
                        
                        stats['successful'] += 1
                        logger.debug(f"✅ Sent broadcast to user {user_id}")
                        
                        # Add delay to respect rate limits
                        await asyncio.sleep(60 / self.BROADCAST_LIMITS['users_per_minute'])
                        
                    except Forbidden as e:
                        stats['blocked'] += 1
                        logger.info(f"🚫 User {user_id} blocked the bot")
                        
                        # Mark user as blocked in database
                        await self.db_client.ban_user(user_id)
                        
                    except BadRequest as e:
                        stats['failed'] += 1
                        error_msg = f"BadRequest for user {user_id}: {e}"
                        stats['errors'].append(error_msg)
                        logger.warning(error_msg)
                        
                    except Exception as e:
                        stats['failed'] += 1
                        error_msg = f"Error sending to user {user_id}: {e}"
                        stats['errors'].append(error_msg)
                        logger.error(error_msg)
            
            # Send to all users concurrently with rate limiting
            tasks = [send_to_user(user_id) for user_id in target_users]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.info(f"📢 User broadcast completed: {stats['successful']}/{stats['total_targets']} successful")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error in user broadcast: {e}")
            return {'error': str(e)}
    
    async def broadcast_to_groups(self, bot: Bot, message: str, target_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """Broadcast message to groups"""
        try:
            stats = {
                'target_type': 'groups',
                'total_targets': 0,
                'successful': 0,
                'failed': 0,
                'left_group': 0,
                'errors': []
            }
            
            # For groups, we would need to track groups in database
            # This is a placeholder implementation
            if target_ids:
                target_groups = target_ids
            else:
                target_groups = []  # Placeholder
            
            stats['total_targets'] = len(target_groups)
            
            logger.info(f"📢 Starting broadcast to {len(target_groups)} groups")
            
            # Process groups with rate limiting
            semaphore = asyncio.Semaphore(self.BROADCAST_LIMITS['groups_per_minute'])
            
            async def send_to_group(group_id: int):
                async with semaphore:
                    try:
                        await bot.send_message(
                            chat_id=group_id,
                            text=message,
                            parse_mode='Markdown'
                        )
                        
                        stats['successful'] += 1
                        logger.debug(f"✅ Sent broadcast to group {group_id}")
                        
                        # Add delay
                        await asyncio.sleep(60 / self.BROADCAST_LIMITS['groups_per_minute'])
                        
                    except Forbidden as e:
                        stats['left_group'] += 1
                        logger.info(f"🚫 Bot left group {group_id}")
                        
                    except BadRequest as e:
                        stats['failed'] += 1
                        error_msg = f"BadRequest for group {group_id}: {e}"
                        stats['errors'].append(error_msg)
                        logger.warning(error_msg)
                        
                    except Exception as e:
                        stats['failed'] += 1
                        error_msg = f"Error sending to group {group_id}: {e}"
                        stats['errors'].append(error_msg)
                        logger.error(error_msg)
            
            tasks = [send_to_group(group_id) for group_id in target_groups]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.info(f"📢 Group broadcast completed: {stats['successful']}/{stats['total_targets']} successful")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error in group broadcast: {e}")
            return {'error': str(e)}
