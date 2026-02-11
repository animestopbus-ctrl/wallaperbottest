"""
LastPerson07Bot Reactions Module
Handles emoji reactions and interactive elements
"""

import logging
import random
from typing import List
from telegram import Bot

logger = logging.getLogger(__name__)

class LastPerson07Reactions:
    """Handles emoji reactions and interactive elements"""
    
    def __init__(self):
        """Initialize with reaction list"""
        self.REACTIONS = [
            "👍", "❤️", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬",
            "😢", "🎉", "🤩", "🤮", "💩", "🙏", "👌", "🕊", "🤡", "🥱",
            "🥴", "😍", "🐳", "❤️‍🔥", "🌚", "🌭", "💯", "🤣", "⚡", "🍌",
            "🏆", "💔", "🤨", "😐", "🍓", "🍾", "💋", "🖕", "😈", "😴",
            "😭", "🤓", "👻", "👨‍💻", "👀", "🎃", "🙈", "😇", "😨", "🤝",
            "✍", "🤗", "🫡", "🎅", "🎄", "☃", "💅", "🤪", "🗿", "🆒",
            "💘", "🙉", "🦄", "😘", "💊", "🙊", "😎", "👾", "🤷‍♂️", "🤷‍♀️", "😡"
        ]
    
    async def set_random_reaction(self, bot: Bot, chat_id: int, message_id: int) -> None:
        """Set a random reaction to a message"""
        try:
            # Select random reaction
            emoji = random.choice(self.REACTIONS)
            
            # Set the reaction
            await bot.set_message_reaction(
                chat_id=chat_id,
                message_id=message_id,
                reaction=emoji
            )
            
            logger.debug(f"✅ Set reaction {emoji} to message {message_id} in chat {chat_id}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to set reaction: {e}")
    
    def get_random_reaction(self) -> str:
        """Get a random reaction emoji"""
        return random.choice(self.REACTIONS)
    
    def is_supported_emoji(self, emoji: str) -> bool:
        """Check if emoji is supported"""
        return emoji in self.REACTIONS
