"""
LastPerson07Bot Error Handler Module
Comprehensive error handling for all bot operations
"""

import logging
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

class LastPerson07ErrorHandler:
    """Comprehensive error handler for the bot"""
    
    def __init__(self):
        """Initialize the error handler"""
        self.config = None  # Would inject config if needed
    
    async def handle_error(self, update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle any error that occurs during bot operation"""
        try:
            # Get the error details
            error = context.error
            error_type = type(error).__name__
            error_message = str(error)
            
            # Log the error
            logger.error(f"Exception while handling an update: {error}")
            
            # Handle specific error types
            if isinstance(error, TelegramError):
                await self._handle_telegram_error(update, context, error)
            else:
                await self._handle_generic_error(update, context, error)
                
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
    
    async def _handle_telegram_error(self, update: Optional[Update], context: ContextTypes.DEFAULT_TYPE, error: TelegramError) -> None:
        """Handle Telegram-specific errors"""
        logger.warning(f"Telegram error: {error}")
        
        # Don't try to send messages back if we're forbidden
        if "bot was blocked by the user" in str(error).lower():
            logger.info("User blocked the bot, skipping notification")
            return
        
        # Send generic error message to user
        if update and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ Sorry, I encountered an error. Please try again later."
                )
            except Exception:
                pass  # If we can't send the error message, just log it
    
    async def _handle_generic_error(self, update: Optional[Update], context: ContextTypes.DEFAULT_TYPE, error: Exception) -> None:
        """Handle generic/unknown errors"""
        logger.error(f"Unknown error occurred: {error}")
        
        # Send generic error message to user if possible
        if update and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ An unexpected error occurred. Please try again later."
                )
            except Exception:
                pass

# Global error handler instance
error_handler = LastPerson07ErrorHandler()

async def handle_error(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    """Main error handler function for the bot"""
    await error_handler.handle_error(update, context)
