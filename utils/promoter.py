"""
LastPerson07Bot Promoter Module
Handles user promotion to premium and promotional content
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config.config import LastPerson07Config

logger = logging.getLogger(__name__)

class LastPerson07Promoter:
    """Handles user promotion management and promotional content"""
    
    def __init__(self, db_client, config: LastPerson07Config):
        """Initialize the promoter"""
        self.db_client = db_client
        self.config = config
        
        # Promotional messages
        self.promo_messages = [
            "🎉 Enjoying these wallpapers? 💎 Upgrade to Premium for unlimited access!",
            "⚡ Daily limit reached? 🚀 Get Premium for unlimited wallpapers!",
            "💎 Unlock all features with Premium! 🖼️ Unlimited wallpapers, no ads!",
            "🌟 Want more? 💎 Premium gives you unlimited beautiful wallpapers!",
            "⭐ Love wallpapers? 💎 Get Premium for endless inspiration!"
        ]
        
        # Premium features list
        self.premium_features = [
            "🖼️ Unlimited wallpaper downloads",
            "⚡ No advertisements",
            "🎨 Custom emoji support",
            "🚀 Priority API access",
            "📊 Download statistics",
            "⚡ Faster response times",
            "🎯 Custom categories",
            "📧 Priority support"
        ]
    
    async def check_and_show_promotion(self, context: ContextTypes.DEFAULT_TYPE, user_id: int, chat_id: int) -> None:
        """Check if user should see promotional content and show it"""
        try:
            # Get user data
            user_data = await self.db_client.get_user(user_id)
            
            if not user_data or user_data.get('tier') == 'premium':
                return  # No promo for premium users
            
            # Check if user has reached daily limit
            fetch_count = user_data.get('fetch_count', 0)
            last_fetch = user_data.get('last_fetch_date')
            
            today = datetime.utcnow().date()
            if last_fetch and last_fetch.date() == today:
                remaining = self.config.FREE_FETCH_LIMIT - fetch_count
                
                # Show promo at certain points
                if remaining <= 1 or fetch_count == self.config.FREE_FETCH_LIMIT // 2:
                    await self._send_promotional_message(context, chat_id, user_data)
        
        except Exception as e:
            logger.error(f"❌ Error showing promotion: {e}")
    
    async def _send_promotional_message(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_data: Dict[str, Any]) -> None:
        """Send promotional message to user"""
        try:
            # Select random promo message
            promo_text = random.choice(self.promo_messages)
            
            # Build full message
            message_text = f"💎 **Premium Upgrade** 💎\n\n"
            message_text += f"{promo_text}\n\n"
            message_text += "**✨ Premium Features:**\n"
            
            for feature in self.premium_features[:4]:  # Limit to 4 features
                message_text += f"• {feature}\n"
            
            message_text += f"\n💰 **Only $2/month!**\n\n"
            message_text += f"🚀 **Ready to upgrade?**\n"
            message_text += f"Use /premium or /buy to get started!"
            
            # Create promotional buttons
            keyboard = [
                [
                    InlineKeyboardButton(
                        text="💎 Upgrade to Premium",
                        callback_data="upgrade_premium"
                    ),
                    InlineKeyboardButton(
                        text="💳 Buy Now",
                        callback_data="buy_premium"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❓ Learn More",
                        callback_data="premium_info"
                    ),
                    InlineKeyboardButton(
                        text="🙏 Not Now",
                        callback_data="dismiss_promo"
                    )
                ]
            ]
            
            # Add promo channel button if configured
            if self.config.PROMO_CHANNEL:
                keyboard.append([
                    InlineKeyboardButton(
                        text=f"Join {self.config.PROMO_CHANNEL}",
                        url=f"https://t.me/{self.config.PROMO_CHANNEL.lstrip('@')}"
                    )
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send message
            await context.bot.send_message(
                chat_id=chat_id,
                text=message_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"💰 Sent promotional message to user {user_data['_id']}")
            
        except Exception as e:
            logger.error(f"❌ Error sending promotional message: {e}")
    
    async def promote_user(self, user_id: int, duration_days: int = 30) -> bool:
        """Promote a user to premium status"""
        try:
            # Calculate expiration
            expiration = datetime.utcnow() + timedelta(days=duration_days)
            
            # Update user in database
            await self.db_client.set_user_tier(user_id, 'premium', expiration)
            
            logger.info(f"💎 Promoted user {user_id} to premium for {duration_days} days")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error promoting user {user_id}: {e}")
            return False
    
    async def demote_user(self, user_id: int) -> bool:
        """Demote a premium user back to free"""
        try:
            # Update user in database
            await self.db_client.set_user_tier(user_id, 'free')
            
            logger.info(f"❌ Demoted user {user_id} to free tier")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error demoting user {user_id}: {e}")
            return False
    
    async def send_premium_welcome(self, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
        """Send welcome message to new premium users"""
        try:
            welcome_text = "🎉 **Welcome to Premium!** 🎉\n\n"
            welcome_text += "Congratulations on upgrading to Premium!\n\n"
            welcome_text += "💎 **Your Premium Benefits:**\n"
            
            for feature in self.premium_features:
                welcome_text += f"✅ {feature}\n"
            
            welcome_text += f"\n🚀 **Start enjoying unlimited downloads!**\n"
            welcome_text += f"Use /fetch to get started with your unlimited access!\n\n"
            welcome_text += f"⭐ Thank you for your support!"
            
            # Send message
            await context.bot.send_message(
                chat_id=user_id,
                text=welcome_text,
                parse_mode='Markdown'
            )
            
            logger.info(f"🎉 Sent premium welcome to user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error sending premium welcome: {e}")
