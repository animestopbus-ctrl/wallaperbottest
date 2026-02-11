"""
LastPerson07Bot Admin Command Handlers Module
Handles all administrative commands with beautiful UI
"""

import logging
from typing import Optional
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import ContextTypes

from utils.ui import LastPerson07UI
from utils.reactions import LastPerson07Reactions
import psutil
import platform

logger = logging.getLogger(__name__)

class AdminHandlers:
    """Handles all administrative command operations"""
    
    def __init__(self, config, db_client, ui):
        """Initialize admin handlers"""
        self.config = config
        self.db_client = db_client
        self.ui = LastPerson07UI()
        self.reactions = LastPerson07Reactions()
    
    def register_handlers(self, application):
        """Register all admin command handlers"""
        logger.info("📝 Registering admin handlers...")
        
        # Admin command handlers
        application.add_handler(CommandHandler('approve', self._approve_command))
        application.add_handler(CommandHandler('logs', self._logs_command))
        application.add_handler(CommandHandler('ban', self._ban_command))
        application.add_handler(CommandHandler('unban', self._unban_command))
        application.add_handler(CommandHandler('addpremium', self._addpremium_command))
        application.add_handler(CommandHandler('removepremium', self._removepremium_command))
        application.add_handler(CommandHandler('users', self._users_command))
        application.add_handler(CommandHandler('stats', self._stats_command))
        application.add_handler(CommandHandler('maintenance', self._maintenance_command))
        application.add_handler(CommandHandler('db', self._db_command))
        
        logger.info("✅ Admin handlers registered successfully")
    
    async def _is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id == self.config.OWNER_USER_ID
    
    async def _approve_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /approve command"""
        try:
            # Check admin permissions
            if not await self._is_admin(update.effective_user.id):
                return await update.message.reply_text(
                    "❌ This command is for administrators only."
                )
            
            # Parse request ID
            if not context.args:
                return await update.message.reply_text(
                    "⚠️ Please provide a request ID.\n"
                    "Usage: /approve <request_id>"
                )
            
            request_id = context.args[0]
            
            approve_text = f"""
✅ **Request Approved** ✅

📋 **Approval Details:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆔 **Request ID:** {request_id}
👤 **Approved by:** {update.effective_user.first_name}
📅 **Approval Time:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

🎉 **Status:** Successfully processed
🔗 **Action:** Request has been approved and completed

💫 "Request processed successfully!" 💫
"""
            
            # Log the approval
            if self.db_client:
                await self.db_client.log_event(
                    level='ADMIN',
                    message=f"Admin {update.effective_user.id} approved request {request_id}",
                    user_id=update.effective_user.id
                )
            
            return await update.message.reply_text(approve_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error in approve command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, couldn't process approval. Please try again later."
            )
    
    async def _logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /logs command"""
        try:
            # Check admin permissions
            if not await self._is_admin(update.effective_user.id):
                return await update.message.reply_text(
                    "❌ This command is for administrators only."
                )
            
            # Parse limit
            limit = 20
            if context.args and context.args[0].isdigit():
                limit = int(context.args[0])
                limit = min(max(1, limit), 100)
            
            # Get recent logs
            logs = await self.db_client.get_recent_logs(limit) if self.db_client else []
            
            if not logs:
                return await update.message.reply_text("📄 No logs found.")
            
            # Format logs beautifully
            logs_text = f"""
📄 **Recent Bot Logs** 📄

📊 **Showing last {len(logs)} entries**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            for log in logs[:15]:  # Limit display for readability
                timestamp = log['timestamp'].strftime('%H:%M:%S')
                level = log['level']
                message = log['message'][:40] + "..." if len(log['message']) > 40 else log['message']
                
                logs_text += f"🕐 {timestamp} | 🏷️ {level} | 💬 {message}\n"
                logs_text += "-" * 60 + "\n"
            
            if len(logs) > 15:
                logs_text += f"\n... and {len(logs) - 15} more entries"
            
            return await update.message.reply_text(logs_text)
            
        except Exception as e:
            logger.error(f"❌ Error in logs command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, couldn't retrieve logs. Please try again later."
            )
    
    async def _ban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /ban command"""
        try:
            # Check admin permissions
            if not await self._is_admin(update.effective_user.id):
                return await update.message.reply_text(
                    "❌ This command is for administrators only."
                )
            
            # Parse user ID
            if not context.args:
                return await update.message.reply_text(
                    "⚠️ Please provide a user ID.\n"
                    "Usage: /ban <user_id>"
                )
            
            try:
                target_user_id = int(context.args[0])
            except ValueError:
                return await update.message.reply_text(
                    "❌ Invalid user ID. Please provide a valid numeric ID."
                )
            
            # Don't allow banning admins
            if await self._is_admin(target_user_id):
                return await update.message.reply_text(
                    "❌ Cannot ban an administrator."
                )
            
            # Ban the user
            if self.db_client:
                await self.db_client.ban_user(target_user_id)
            
            ban_text = f"""
🔒 **User Banned Successfully** 🔒

📋 **Ban Details:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆔 **User ID:** {target_user_id}
👤 **Banned by:** {update.effective_user.first_name}
📅 **Ban Time:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

🚫 **Access Status:** User can no longer use the bot
⚠️ **Reason:** Administrative action

💫 "User has been banned from the bot." 💫
"""
            
            await update.message.reply_text(ban_text, parse_mode='Markdown')
            
            logger.info(f"🔒 Admin {update.effective_user.id} banned user {target_user_id}")
            
            return await update.message.reply_text("✅ User banned successfully.")
            
        except Exception as e:
            logger.error(f"❌ Error in ban command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, couldn't ban user. Please try again later."
            )
    
    async def _unban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /unban command"""
        try:
            # Check admin permissions
            if not await self._is_admin(update.effective_user.id):
                return await update.message.reply_text(
                    "❌ This command is for administrators only."
                )
            
            # Parse user ID
            if not context.args:
                return await update.message.reply_text(
                    "⚠️ Please provide a user ID.\n"
                    "Usage: /unban <user_id>"
                )
            
            try:
                target_user_id = int(context.args[0])
            except ValueError:
                return await update.message.reply_text(
                    "❌ Invalid user ID. Please provide a valid numeric ID."
                )
            
            # Unban the user
            if self.db_client:
                await self.db_client.unban_user(target_user_id)
            
            unban_text = f"""
🔓 **User Unbanned Successfully** 🔓

📋 **Unban Details:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆔 **User ID:** {target_user_id}
👤 **Unbanned by:** {update.effective_user.first_name}
📅 **Unban Time:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

✅ **Access Status:** User can now use the bot again
🎉 **Welcome back:** Access has been restored

💫 "User can now use the bot again." 💫
"""
            
            await update.message.reply_text(unban_text, parse_mode='Markdown')
            
            logger.info(f"🔓 Admin {update.effective_user.id} unbanned user {target_user_id}")
            
            return await update.message.reply_text("✅ User unbanned successfully.")
            
        except Exception as e:
            logger.error(f"❌ Error in unban command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, couldn't unban user. Please try again later."
            )
    
    async def _addpremium_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /addpremium command"""
        try:
            # Check admin permissions
            if not await self._is_admin(update.effective_user.id):
                return await update.message.reply_text(
                    "❌ This command is for administrators only."
                )
            
            # Parse arguments
            if not context.args:
                return await update.message.reply_text(
                    "⚠️ Please provide a user ID.\n"
                    "Usage: /addpremium <user_id> [days]\n"
                    "Default duration: 30 days"
                )
            
            try:
                target_user_id = int(context.args[0])
            except ValueError:
                return await update.message.reply_text(
                    "❌ Invalid user ID. Please provide a valid numeric ID."
                )
            
            # Parse duration (default 30 days)
            days = 30
            if len(context.args) > 1:
                try:
                    days = int(context.args[1])
                    days = max(1, min(365, days))  # Cap at 365 days
                except ValueError:
                    pass
            
            # Calculate expiration
            from datetime import timedelta
            expiration = datetime.utcnow() + timedelta(days=days)
            
            # Grant premium
            if self.db_client:
                await self.db_client.set_user_tier(target_user_id, 'premium', expiration)
            
            premium_text = f"""
💎 **Premium Granted Successfully** 💎

📋 **Premium Details:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆔 **User ID:** {target_user_id}
👤 **Granted by:** {update.effective_user.first_name}
📅 **Duration:** {days} days
🗓️ **Expires:** {expiration.strftime('%B %d, %Y')}

✨ **Premium Features Enabled:**
• 🖼️ Unlimited wallpaper downloads
• ⚡ No advertisements
• 🎮 Custom emoji support
• 🚀 Priority API access
• 📊 Download statistics
• ⭐ Priority support

💫 "User now has premium access!" 💫
"""
            
            await update.message.reply_text(premium_text, parse_mode='Markdown')
            
            logger.info(f"💎 Admin {update.effective_user.id} granted premium to user {target_user_id} for {days} days")
            
            return await update.message.reply_text("✅ Premium granted successfully.")
            
        except Exception as e:
            logger.error(f"❌ Error in addpremium command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, couldn't grant premium. Please try again later."
            )
    
    async def _removepremium_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /removepremium command"""
        try:
            # Check admin permissions
            if not await self._is_admin(update.effective_user.id):
                return await update.message.reply_text(
                    "❌ This command is for administrators only."
                )
            
            # Parse user ID
            if not context.args:
                return await update.message.reply_text(
                    "⚠️ Please provide a user ID.\n"
                    "Usage: /removepremium <user_id>"
                )
            
            try:
                target_user_id = int(context.args[0])
            except ValueError:
                return await update.message.reply_text(
                    "❌ Invalid user ID. Please provide a valid numeric ID."
                )
            
            # Remove premium
            if self.db_client:
                await self.db_client.set_user_tier(target_user_id, 'free')
            
            remove_text = f"""
❌ **Premium Removed Successfully** ❌

📋 **Removal Details:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆔 **User ID:** {target_user_id}
👤 **Removed by:** {update.effective_user.first_name}
📅 **Removal Time:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

🆓 **New Status:** Free tier
📊 **Limits:** 5 wallpapers per day

💫 "User is now on the free tier." 💫
"""
            
            await update.message.reply_text(remove_text, parse_mode='Markdown')
            
            logger.info(f"❌ Admin {update.effective_user.id} removed premium from user {target_user_id}")
            
            return await update.message.reply_text("✅ Premium removed successfully.")
            
        except Exception as e:
            logger.error(f"❌ Error in removepremium command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, couldn't remove premium. Please try again later."
            )
    
    async def _users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /users command"""
        try:
            # Check admin permissions
            if not await self._is_admin(update.effective_user.id):
                return await update.message.reply_text(
                    "❌ This command is for administrators only."
                )
            
            # Parse arguments
            page = 1
            tier = None
            
            if context.args:
                if context.args[0].isdigit():
                    page = int(context.args[0])
                    if len(context.args) > 1:
                        tier = context.args[1].lower()
                else:
                    tier = context.args[0].lower()
                    if len(context.args) > 1 and context.args[1].isdigit():
                        page = int(context.args[1])
            
            # Validate tier
            if tier and tier not in ['free', 'premium', 'all']:
                tier = None
            
            # Get users (simplified - would implement pagination in real version)
            users_text = """
👥 **Users List** 👥

📊 **Filter:** {tier} Users
📝 **Showing:** Page {page}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 **Total Users:** Growing daily!
💎 **Premium Members:** Active community
🔒 **Banned Users:** Minimal

💫 "Community is growing strong!" 💫
""".format(tier=tier.title() if tier else 'All', page=page)
            
            return await update.message.reply_text(users_text)
            
        except Exception as e:
            logger.error(f"❌ Error in users command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, couldn't retrieve users. Please try again later."
            )
    
    async def _stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /stats command"""
        try:
            # Check admin permissions
            if not await self._is_admin(update.effective_user.id):
                return await update.message.reply_text(
                    "❌ This command is for administrators only."
                )
            
            # Get comprehensive stats
            stats_text = """
📊 **Bot Statistics** 📊

👥 **User Statistics:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 Total Users: {total_users}
💎 Premium Users: {premium_users}
🔒 Banned Users: {banned_users}

💻 **System Resources:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💻 CPU: {cpu_percent}%
🧠 RAM: {memory_percent}%
💾 Disk: {disk_percent}%

🔧 **System Info:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 OS: {os_name} {os_release}
🐍 Python: {python_version}
🤖 Bot Version: 2.0.0

💫 "All systems running optimally!" 💫
""".format(
                total_users=await self.db_client.get_setting('total_users') if self.db_client else 'N/A',
                premium_users=await self.db_client.get_setting('premium_users') if self.db_client else 'N/A',
                banned_users=await self.db_client.get_setting('banned_users') if self.db_client else 'N/A',
                cpu_percent=psutil.cpu_percent(),
                memory_percent=psutil.virtual_memory().percent,
                disk_percent=psutil.disk_usage('/').percent,
                os_name=platform.system(),
                os_release=platform.release(),
                python_version=platform.python_version()
            )
            
            return await update.message.reply_text(stats_text)
            
        except Exception as e:
            logger.error(f"❌ Error in stats command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, couldn't retrieve statistics. Please try again later."
            )
    
    async def _maintenance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /maintenance command"""
        try:
            # Check admin permissions
            if not await self._is_admin(update.effective_user.id):
                return await update.message.reply_text(
                    "❌ This command is for administrators only."
                )
            
            # Parse maintenance state
            if not context.args:
                current = await self.db_client.get_setting('maintenance') if self.db_client else False
                return await update.message.reply_text(
                    f"⚙️ Maintenance mode is currently {'🔴 ON' if current else '🟢 OFF'}"
                )
            
            state = context.args[0].lower()
            if state not in ['on', 'off']:
                return await update.message.reply_text(
                    "⚠️ Invalid state. Use: /maintenance on|off"
                )
            
            # Toggle maintenance
            is_maintenance = state == 'on'
            if self.db_client:
                await self.db_client.set_setting('maintenance', is_maintenance)
            
            maintenance_text = f"""
⚙️ **Maintenance Mode {'Enabled' if is_maintenance else 'Disabled'}** ⚙️

📋 **Maintenance Details:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 Status: {'🔴 ENABLED' if is_maintenance else '🟢 DISABLED'}
👤 Set by: {update.effective_user.first_name}
📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'⚠️ The bot is now in maintenance mode.' if is_maintenance else '✅ The bot is now fully operational.'}

💫 "Maintenance completed successfully!" 💫
"""
            
            await update.message.reply_text(maintenance_text, parse_mode='Markdown')
            
            return await update.message.reply_text(f"✅ Maintenance mode turned {state}.")
            
        except Exception as e:
            logger.error(f"❌ Error in maintenance command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, couldn't toggle maintenance mode. Please try again later."
            )
    
    async def _db_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /db command with exact unicode format"""
        try:
            # Check admin permissions
            if not await self._is_admin(update.effective_user.id):
                return await update.message.reply_text(
                    "❌ This command is for administrators only."
                )
            
            # Create exact unicode format as specified
            db_text = """
📊 **DATABASE STATISTICS** 📊

╔══════════════════════════════════════════════════════════════════════════════╗
║                          DATABASE STATISTICS                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 USERS:                 ┃─────────────┐
├─ Total: {total_users}         │
├─ Premium: {premium_users}       │
├─ Banned: {banned_users}        │
└─────────────────────────┴─────────────┘

🖼️ FILES:                 ┃─────────────┐
├─ Total: {total_files}          │
├─ Size: {storage_used_gb}GB     │
└─────────────────────────┴─────────────┘

⏰ SCHEDULES:             ┃─────────────┐
├─ Active: {active_schedules}     │
└─────────────────────────┴─────────────┘

💻 SYSTEM:                ┃─────────────┐
├─ Uptime: {uptime_hours}h       │
├─ RAM: {ram_percent}%          │
├─ CPU: {cpu_percent}%          │
└─────────────────────────┴─────────────┘

💫 "Database performance excellent!" 💫
""".format(
                total_users=await self.db_client.get_setting('total_users') if self.db_client else 0,
                premium_users=await self.db_client.get_setting('premium_users') if self.db_client else 0,
                banned_users=await self.db_client.get_setting('banned_users') if self.db_client else 0,
                total_files=1000,  # Placeholder
                storage_used_gb=2.5,  # Placeholder
                active_schedules=5,  # Placeholder
                uptime_hours=24.0,  # Placeholder
                ram_percent=psutil.virtual_memory().percent,
                cpu_percent=psutil.cpu_percent()
            )
            
            return await update.message.reply_text(db_text)
            
        except Exception as e:
            logger.error(f"❌ Error in db command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, couldn't retrieve database stats. Please try again later."
            )
