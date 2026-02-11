#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                      🌟 LASTPERSON07BOT 🌟                                   ║
║                    Premium Wallpaper Fetching Bot                            ║
║                                                                              ║
║                🎨 Beautiful • 💎 Premium • 🚀 Production Ready              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import logging
import signal
import sys
import os
from typing import Optional
from datetime import datetime
from pathlib import Path

# Ensure directories exist
Path("logs").mkdir(exist_ok=True)
Path("data").mkdir(exist_ok=True)

# Configure logging with beautiful formatting
logging.basicConfig(
    level=logging.INFO,
    format='🕐 %(asctime)s | 📝 %(name)s | 🎯 %(levelname)s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler('logs/bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Load environment before imports
from dotenv import load_dotenv
load_dotenv()

# Core imports
from telegram.ext import Application
from config.config import LastPerson07Config
from db.client import LastPerson07DatabaseClient
from utils.ui import LastPerson07UI
from utils.reactions import LastPerson07Reactions
from handlers.user_handlers import UserHandlers
from handlers.admin_handlers import AdminHandlers
from handlers.error_handler import ErrorHandler

class LastPerson07Bot:
    """🌟 Premium Wallpaper Fetching Bot with Beautiful UI"""
    
    def __init__(self):
        """🔧 Initialize the bot with all components"""
        self.config = LastPerson07Config()
        self.db_client: Optional[LastPerson07DatabaseClient] = None
        self.application: Optional[Application] = None
        self.running = False
        
        # Initialize utility classes
        self.ui = LastPerson07UI()
        self.reactions = LastPerson07Reactions()
        
        # Initialize handlers
        self.user_handlers = UserHandlers(self.config, self.db_client, self.ui, self.reactions)
        self.admin_handlers = AdminHandlers(self.config, self.db_client, self.ui)
        self.error_handler = ErrorHandler()
    
    async def initialize(self) -> bool:
        """🚀 Initialize all components with proper error handling"""
        try:
            logger.info("🌟 Starting LastPerson07Bot initialization...")
            
            # Validate configuration
            if not self.config.TELEGRAM_TOKEN:
                logger.error("❌ TELEGRAM_TOKEN not found in environment variables")
                return False
            
            # Initialize database connection
            logger.info("🔌 Establishing database connection...")
            self.db_client = LastPerson07DatabaseClient(self.config.MONGODB_URI)
            connected = await self.db_client.connect()
            
            if not connected:
                logger.error("❌ Failed to connect to database")
                return False
            
            logger.info("✅ Database connection successful")
            
            # Initialize handlers with database
            self.user_handlers.db_client = self.db_client
            self.admin_handlers.db_client = self.db_client
            
            # Create Telegram application
            logger.info("🤖 Creating Telegram application...")
            self.application = Application.builder().token(self.config.TELEGRAM_TOKEN).build()
            
            # Set up error handler
            self.application.add_error_handler(self.error_handler.handle_error)
            
            # Register all handlers
            await self._register_handlers()
            
            # Set up bot commands
            await self._setup_commands()
            
            logger.info("🎉 Bot initialization completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize bot: {e}")
            logger.exception(e)
            return False
    
    async def _register_handlers(self) -> None:
        """📝 Register all command and callback handlers"""
        logger.info("📝 Registering command handlers...")
        
        # Register user command handlers
        self.user_handlers.register_handlers(self.application)
        
        # Register admin command handlers
        self.admin_handlers.register_handlers(self.application)
        
        logger.info("✅ All handlers registered successfully")
    
    async def _setup_commands(self) -> None:
        """⚙️ Set up bot commands in Telegram"""
        logger.info("⚙️ Setting up bot commands...")
        
        from telegram import BotCommand, BotCommandScopeDefault
        
        commands = [
            BotCommand('start', '🚀 Start your wallpaper journey'),
            BotCommand('fetch', '🖼️ Fetch beautiful wallpapers'),
            BotCommand('categories', '📂 Browse all categories'),
            BotCommand('premium', '💎 View premium benefits'),
            BotCommand('myplan', '📋 Check your subscription'),
            BotCommand('buy', '🛒 Upgrade to premium'),
            BotCommand('info', 'ℹ️ Bot information'),
            BotCommand('schedule', '⏰ Set automatic posting'),
            BotCommand('help', '❓ Get help and guide'),
            BotCommand('report', '⚠️ Report an issue'),
            BotCommand('feedback', '💬 Send feedback'),
            # Admin commands
            BotCommand('approve', '👑 Approve requests'),
            BotCommand('logs', '📝 View bot logs'),
            BotCommand('ban', '🔒 Ban users'),
            BotCommand('unban', '🔓 Unban users'),
            BotCommand('addpremium', '💎 Grant premium'),
            BotCommand('removepremium', '❌ Remove premium'),
            BotCommand('users', '👥 View users'),
            BotCommand('stats', '📊 View statistics'),
            BotCommand('maintenance', '⚙️ Maintenance mode'),
            BotCommand('db', '📊 Database stats')
        ]
        
        await self.application.bot.set_my_commands(commands, scope=BotCommandScopeDefault())
        logger.info("✅ Bot commands configured successfully")
    
    async def shutdown(self) -> None:
        """Graceful shutdown procedure"""
        logger.info("🔄 Starting graceful shutdown...")
        
        try:
            # Close database connection
            if self.db_client:
                await self.db_client.close()
                logger.info("✅ Database connection closed")
            
            logger.info("👋 Bot has been shut down gracefully")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

def main() -> None:
    """Main application entry point"""
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"📡 Received signal {signum}, initiating graceful shutdown...")
        if bot.running:
            asyncio.create_task(bot.shutdown())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🚀 Starting LastPerson07Bot...")
    
    try:
        # Create and initialize bot
        bot = LastPerson07Bot()
        
        if not bot.initialize():
            logger.error("❌ Failed to initialize bot")
            sys.exit(1)
        
        bot.running = True
        
        # Set up shutdown handler
        async def shutdown_handler():
            await bot.shutdown()
        
        # Start the bot with polling
        logger.info("⚡ Starting bot polling...")
        bot.application.run_polling(drop_pending_updates=True, shutdown=shutdown_handler)
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
