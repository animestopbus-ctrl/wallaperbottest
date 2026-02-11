"""
LastPerson07Bot Configuration Module
Handles all configuration management with validation
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LastPerson07Config:
    """Central configuration class for LastPerson07Bot"""
    
    def __init__(self):
        """Initialize configuration with environment variables"""
        
        # Telegram Configuration
        self.TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
        self.OWNER_USERNAME = os.getenv('OWNER_USERNAME', '')
        self.OWNER_USER_ID = int(os.getenv('OWNER_USER_ID', '0'))
        self.PROMO_CHANNEL = os.getenv('PROMO_CHANNEL', '')
        self.BIN_CHANNEL_ID = int(os.getenv('BIN_CHANNEL_ID', '0')) or None
        
        # Database Configuration
        self.MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/lastperson07_bot')
        
        # API Keys
        self.UNSPLASH_KEY = os.getenv('UNSPLASH_KEY', '')
        self.PEXELS_KEY = os.getenv('PEXELS_KEY', '')
        self.PIXABAY_KEY = os.getenv('PIXABAY_KEY', '')
        
        # Premium Features
        self.OWNER_HAS_PREMIUM = os.getenv('OWNER_HAS_PREMIUM', 'false').lower() == 'true'
        self.CUSTOM_EMOJI_ID = os.getenv('CUSTOM_EMOJI_ID', '')
        
        # Bot Settings
        self.MAINTENANCE = os.getenv('MAINTENANCE', 'false').lower() == 'true'
        self.DELAY_MINUTES = int(os.getenv('DELAY_MINUTES', '5'))
        self.FREE_FETCH_LIMIT = int(os.getenv('FREE_FETCH_LIMIT', '5'))
        
        # Wallpaper Categories
        self.WALLPAPER_CATEGORIES = [
            'nature', 'architecture', 'people', 'animals', 'food', 
            'technology', 'objects', 'abstract', 'travel', 'fashion'
        ]
        
        # Category emojis for UI
        self.category_emojis = {
            'nature': '🌿',
            'architecture': '🏛️',
            'people': '👥',
            'animals': '🐾',
            'food': '🍔',
            'technology': '💻',
            'objects': '📦',
            'abstract': '🎨',
            'travel': '✈️',
            'fashion': '👗'
        }
        
        # Interval descriptions
        self.interval_descriptions = {
            'hourly': 'Every Hour',
            'daily': 'Once Daily',
            'weekly': 'Once Weekly'
        }
        
        # Interval emojis
        self.interval_emojis = {
            'hourly': '⏰',
            'daily': '📅',
            'weekly': '📆'
        }
        
        # Reactions List
        self.REACTIONS = [
            "👍", "❤️", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬",
            "😢", "🎉", "🤩", "🤮", "💩", "🙏", "👌", "🕊", "🤡", "🥱",
            "🥴", "😍", "🐳", "❤️‍🔥", "🌚", "🌭", "💯", "🤣", "⚡", "🍌",
            "🏆", "💔", "🤨", "😐", "🍓", "🍾", "💋", "🖕", "😈", "😴",
            "😭", "🤓", "👻", "👨‍💻", "👀", "🎃", "🙈", "😇", "😨", "🤝",
            "✍", "🤗", "🫡", "🎅", "🎄", "☃", "💅", "🤪", "🗿", "🆒",
            "💘", "🙉", "🦄", "😘", "💊", "🙊", "😎", "👾", "🤷‍♂️", "🤷‍♀️", "😡"
        ]
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate all required configuration parameters"""
        errors = []
        
        # Validate Telegram token
        if not self.TELEGRAM_TOKEN or len(self.TELEGRAM_TOKEN) < 20:
            errors.append("Invalid TELEGRAM_TOKEN - must be a valid bot token")
        
        # Validate MongoDB URI
        if not self.MONGODB_URI:
            errors.append("MONGODB_URI is required")
        
        # Validate owner ID
        if self.OWNER_USER_ID <= 0:
            errors.append("OWNER_USER_ID must be a positive integer")
        
        # Validate numeric values
        if self.DELAY_MINUTES <= 0:
            errors.append("DELAY_MINUTES must be positive")
        if self.FREE_FETCH_LIMIT <= 0:
            errors.append("FREE_FETCH_LIMIT must be positive")
        
        # Validate categories
        if not self.WALLPAPER_CATEGORIES:
            errors.append("WALLPAPER_CATEGORIES cannot be empty")
        
        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(errors))
    
    def get_api_keys(self) -> dict:
        """Return available API keys"""
        return {
            'unsplash': self.UNSPLASH_KEY,
            'pexels': self.PEXELS_KEY,
            'pixabay': self.PIXABAY_KEY
        }
    
    def is_premium_user(self, user_id: int) -> bool:
        """Check if user has premium status (placeholder)"""
        return user_id == self.OWNER_USER_ID
