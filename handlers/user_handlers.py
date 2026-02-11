"""
LastPerson07Bot User Command Handlers Module
Handles all user-facing commands with beautiful UI
"""

import logging
import random
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import ContextTypes, ConversationHandler

from utils.ui import LastPerson07UI
from utils.reactions import LastPerson07Reactions
from utils.metadata import LastPerson07ImageProcessor
from utils.fetcher import LastPerson07WallpaperFetcher

logger = logging.getLogger(__name__)

class UserHandlers:
    """Handles all user command operations"""
    
    def __init__(self, config, db_client, ui, reactions):
        """Initialize user handlers"""
        self.config = config
        self.db_client = db_client
        self.ui = LastPerson07UI()
        self.reactions = LastPerson07Reactions()
        self.image_processor = LastPerson07ImageProcessor()
        self.fetcher = None  # Will be initialized with db_client
    
    def register_handlers(self, application):
        """Register all user command handlers"""
        logger.info("📝 Registering user handlers...")
        
        # User command handlers
        application.add_handler(CommandHandler('start', self._start_command))
        application.add_handler(CommandHandler('fetch', self._fetch_command))
        application.add_handler(CommandHandler('premium', self._premium_command))
        application.add_handler(CommandHandler('myplan', self._myplan_command))
        application.add_handler(CommandHandler('buy', self._buy_command))
        application.add_handler(CommandHandler('info', self._info_command))
        application.add_handler(CommandHandler('categories', self._categories_command))
        application.add_handler(CommandHandler('schedule', self._schedule_command))
        application.add_handler(CommandHandler('help', self._help_command))
        application.add_handler(CommandHandler('report', self._report_command))
        application.add_handler(CommandHandler('feedback', self._feedback_command))
        
        logger.info("✅ User handlers registered successfully")
    
    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /start command with beautiful welcome"""
        try:
            user = update.effective_user
            chat_id = update.effective_chat.id
            
            logger.info(f"👋 User {user.username} ({user.id}) started the bot")
            
            # Get or create user in database
            if self.db_client:
                await self._ensure_user_exists(user.id, user.username, user.first_name)
            
            # Format beautiful welcome message
            welcome_text = self.ui.get_welcome_message(user.first_name)
            
            # Create beautiful inline keyboard
            keyboard = [
                [
                    InlineKeyboardButton(
                        text="🖼️ Fetch Wallpaper 🎨",
                        callback_data="fetch_main"
                    ),
                    InlineKeyboardButton(
                        text="💎 Premium Benefits ✨",
                        callback_data="premium_info"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📂 Browse Categories 📚",
                        callback_data="categories_main"
                    ),
                    InlineKeyboardButton(
                        text="ℹ️ Bot Information ℹ️",
                        callback_data="info_main"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❓ Help & Guide 📖",
                        callback_data="help_main"
                    ),
                    InlineKeyboardButton(
                        text="💬 Send Feedback 💭",
                        callback_data="feedback_main"
                    )
                ]
            ]
            
            # Add promo button for free users
            if self.db_client:
                user_data = await self.db_client.get_user(user.id)
                if user_data and user_data.get('tier') == 'free':
                    keyboard.append([
                        InlineKeyboardButton(
                            text="🌟 Join Our Channel ✨",
                            url=f"https://t.me/{self.config.PROMO_CHANNEL.lstrip('@')}"
                        )
                    ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send beautiful welcome message
            sent_message = await update.message.reply_text(
                text=welcome_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # Set random reaction
            await self.reactions.set_random_reaction(
                context.bot, 
                chat_id, 
                sent_message.message_id
            )
            
            logger.info(f"✅ Welcome message sent to user {user.id}")
            return sent_message
            
        except Exception as e:
            logger.error(f"❌ Error in start command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, I encountered an error. Please try again later."
            )
    
    async def _fetch_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /fetch command with beautiful UI"""
        try:
            user = update.effective_user
            chat_id = update.effective_chat.id
            
            # Parse category
            category = ' '.join(context.args) if context.args else 'nature'
            
            logger.info(f"🖼️ User {user.username} ({user.id}) requested wallpaper: {category}")
            
            # Check user's fetch allowance if database available
            can_fetch = True
            if self.db_client:
                can_fetch, remaining = await self._check_fetch_allowance(user.id)
                
                if not can_fetch:
                    limit_text = self.ui.get_fetch_limit_message(self.config.FREE_FETCH_LIMIT)
                    
                    keyboard = [
                        [
                            InlineKeyboardButton(
                                text="💎 Upgrade to Premium ✨",
                                callback_data="premium_upgrade"
                            ),
                            InlineKeyboardButton(
                                text="📋 View Plans 📝",
                                callback_data="premium_info"
                            )
                        ]
                    ]
                    
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(limit_text, reply_markup=reply_markup)
                    return None
            
            # Send typing action
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")
            
            # Initialize fetcher if needed
            if not self.fetcher and self.db_client:
                self.fetcher = LastPerson07WallpaperFetcher(self.db_client, self.config)
                await self.fetcher.initialize()
            
            # Fetch wallpaper
            await context.bot.send_chat_action(chat_id=chat_id, action="upload_photo")
            
            wallpaper_info = None
            if self.fetcher:
                wallpaper_info = await self.fetcher.fetch_wallpaper(category)
            else:
                # Create mock wallpaper info for demo
                wallpaper_info = {
                    'url': 'https://picsum.photos/1920/1080',
                    'source': 'demo',
                    'width': 1920,
                    'height': 1080,
                    'description': 'Beautiful nature wallpaper',
                    'photographer': 'Demo User',
                    'download_url': 'https://picsum.photos/1920/1080'
                }
            
            if not wallpaper_info:
                error_text = self.ui.get_fetch_error_message(category)
                
                keyboard = [
                    [
                        InlineKeyboardButton(
                            text="🔄 Try Again 🔄",
                            callback_data=f"fetch_{category}"
                        ),
                        InlineKeyboardButton(
                            text="📂 Other Categories 📚",
                            callback_data="categories_main"
                        )
                    ]
                ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                return await update.message.reply_text(error_text, reply_markup=reply_markup)
            
            # Download image
            image_data = None
            if self.fetcher:
                image_data = await self.fetcher.download_image(wallpaper_info['url'])
            
            if not image_data:
                # Use placeholder image for demo
                import requests
                response = requests.get('https://picsum.photos/1920/1080')
                image_data = response.content
            
            # Validate image quality
            is_valid = await self.image_processor.validate_image(image_data)
            if not is_valid:
                return await update.message.reply_text(
                    "❌ The image doesn't meet our quality standards. Please try another."
                )
            
            # Extract image metadata
            metadata = await self.image_processor.extract_metadata(image_data)
            
            # Create beautiful caption
            caption = f"""
🎨 **{wallpaper_info['source'].title()} Masterpiece** 🎨

📊 **Image Details:**
• 📏 Size: {wallpaper_info['width']}×{wallpaper_info['height']}
• 📂 Category: {category.title()}

📸 **Photographer:** {wallpaper_info.get('photographer', 'Unknown')}
🏷️ **Source:** {wallpaper_info['source'].title()}
🔗 **Download:** [High Resolution]({wallpaper_info.get('download_url', '#')})

💫 "Every picture tells a story, make it yours!" 💫
"""
            
            # Create beautiful inline keyboard
            keyboard = [
                [
                    InlineKeyboardButton(
                        text="🔄 Next Wallpaper 🎨",
                        callback_data=f"fetch_{category}"
                    ),
                    InlineKeyboardButton(
                        text="⭐ Save to Favorites ⭐",
                        callback_data=f"favorite_{wallpaper_info.get('url', '')}"
                    )
                ]
            ]
            
            # Add category suggestions
            suggested_categories = random.sample(self.config.WALLPAPER_CATEGORIES, 3)
            category_buttons = [
                InlineKeyboardButton(
                    text=f"📂 {cat.title()}",
                    callback_data=f"fetch_{cat}"
                )
                for cat in suggested_categories
            ]
            keyboard.append(category_buttons)
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send beautiful wallpaper
            sent_message = await context.bot.send_photo(
                chat_id=chat_id,
                photo=image_data,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # Record the fetch if database available
            if self.db_client:
                await self._record_wallpaper_fetch(user.id, wallpaper_info)
            
            # Set random reaction
            await self.reactions.set_random_reaction(
                context.bot, 
                chat_id, 
                sent_message.message_id
            )
            
            logger.info(f"✅ Wallpaper sent to user {user.id}")
            return sent_message
            
        except Exception as e:
            logger.error(f"❌ Error in fetch command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, I encountered an error. Please try again later."
            )
    
    async def _premium_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /premium command with beautiful UI"""
        try:
            user = update.effective_user
            user_data = None
            
            if self.db_client:
                user_data = await self.db_client.get_user(user.id)
            
            is_premium = user_data and user_data.get('tier') == 'premium' if user_data else False
            
            if is_premium:
                expiration_date = user_data.get('expiration')
                premium_text = self.ui.get_premium_welcome_message(
                    user.first_name, 
                    expiration_date.strftime('%B %d, %Y') if expiration_date else None
                )
                
                keyboard = [
                    [
                        InlineKeyboardButton(
                            text="📊 My Statistics 📈",
                            callback_data="my_stats"
                        ),
                        InlineKeyboardButton(
                            text="🖼️ Start Exploring 🎨",
                            callback_data="fetch_main"
                        )
                    ]
                ]
                
            else:
                premium_text = self.ui.get_premium_info()
                
                keyboard = [
                    [
                        InlineKeyboardButton(
                            text="💳 Buy Premium ($2/month) 🚀",
                            callback_data="buy_premium"
                        ),
                        InlineKeyboardButton(
                            text="📋 View Plans 📝",
                            callback_data="compare_plans"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="💬 Contact Owner 💭",
                            url=f"https://t.me/{self.config.OWNER_USERNAME.lstrip('@')}"
                        )
                    ]
                ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            sent_message = await update.message.reply_text(
                text=premium_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # Set random reaction
            await self.reactions.set_random_reaction(
                context.bot, 
                update.effective_chat.id, 
                sent_message.message_id
            )
            
            return sent_message
            
        except Exception as e:
            logger.error(f"❌ Error in premium command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, couldn't load premium information. Please try again later."
            )
    
    async def _myplan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /myplan command with beautiful UI"""
        try:
            user = update.effective_user
            user_data = None
            
            if self.db_client:
                user_data = await self.db_client.get_user(user.id)
            
            tier = user_data.get('tier', 'free') if user_data else 'free'
            
            # Get statistics
            total_fetches = user_data.get('fetch_count', 0) if user_data else 0
            today_fetches = await self._get_today_fetches(user.id) if self.db_client else 0
            join_date = user_data.get('join_date') if user_data else None
            
            myplan_text = self.ui.get_myplan_status_message(
                user.first_name,
                user.id,
                tier,
                total_fetches,
                today_fetches,
                self.config.FREE_FETCH_LIMIT,
                join_date.strftime('%B %d, %Y') if join_date else None
            )
            
            # Create action buttons
            keyboard = []
            
            if tier == 'free':
                keyboard.append([
                    InlineKeyboardButton(
                        text="💎 Upgrade to Premium ✨",
                        callback_data="upgrade_premium"
                    )
                ])
            
            keyboard.append([
                InlineKeyboardButton(
                    text="📊 View Statistics 📈",
                    callback_data="view_stats"
                ),
                InlineKeyboardButton(
                    text="🖼️ Fetch Wallpaper 🎨",
                    callback_data="fetch_main"
                )
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            sent_message = await update.message.reply_text(
                text=myplan_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # Set random reaction
            await self.reactions.set_random_reaction(
                context.bot,
                update.effective_chat.id,
                sent_message.message_id
            )
            
            return sent_message
            
        except Exception as e:
            logger.error(f"❌ Error in myplan command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, couldn't retrieve your plan information. Please try again later."
            )
    
    async def _buy_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /buy command with beautiful UI"""
        try:
            buy_text = self.ui.get_buy_process_message()
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        text="👤 Contact Owner to Buy 💬",
                        url=f"https://t.me/{self.config.OWNER_USERNAME.lstrip('@')}"
                    )
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            sent_message = await update.message.reply_text(
                text=buy_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # Set random reaction
            await self.reactions.set_random_reaction(
                context.bot,
                update.effective_chat.id,
                sent_message.message_id
            )
            
            # Log purchase attempt
            if self.db_client:
                await self.db_client.log_event(
                    level='INFO',
                    message=f"User {update.effective_user.id} initiated premium purchase",
                    user_id=update.effective_user.id
                )
            
            return sent_message
            
        except Exception as e:
            logger.error(f"❌ Error in buy command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, couldn't process your request. Please try again later."
            )
    
    async def _info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /info command with beautiful UI"""
        try:
            info_text = f"""
ℹ️ **Bot Information** ℹ️

🤖 **LastPerson07Bot Details:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 🏷️ **Name:** LastPerson07Bot
• 👤 **Owner:** @{self.config.OWNER_USERNAME}
• 📅 **Version:** 2.0.0
• 📚 **Library:** python-telegram-bot v20.7+
• 🔗 **API Version:** Bot API 7.0

🎨 **Wallpaper Sources:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 🎨 **Unsplash:** High-quality, artistic wallpapers
• 📸 **Pexels:** Free stock photography
• 🌈 **Pixabay:** Royalty-free images

⚡ **Features:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 🖼️ Wallpaper fetching with beautiful formatting
• 💎 Free & Premium subscription tiers
• 🎮 Custom emoji reactions and support
• ⏰ Scheduled posting for groups/channels
• 📊 Comprehensive user statistics
• 🔧 Full admin management tools

🌟 "Bringing beautiful wallpapers to your fingertips!" 🌟
"""
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        text="🖼️ Start Using Bot 🎨",
                        callback_data="fetch_main"
                    ),
                    InlineKeyboardButton(
                        text="💎 Upgrade to Premium ✨",
                        callback_data="premium_info"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📂 View Categories 📚",
                        callback_data="categories_main"
                    ),
                    InlineKeyboardButton(
                        text="📋 Full Help Guide 📖",
                        callback_data="help_main"
                    )
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            sent_message = await update.message.reply_text(
                text=info_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # Set random reaction
            await self.reactions.set_random_reaction(
                context.bot,
                update.effective_chat.id,
                sent_message.message_id
            )
            
            return sent_message
            
        except Exception as e:
            logger.error(f"❌ Error in info command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, couldn't load bot information. Please try again later."
            )
    
    async def _categories_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /categories command with beautiful UI"""
        try:
            categories = self.config.WALLPAPER_CATEGORIES
            featured = random.choice(categories)
            
            categories_text = self.ui.get_categories_message(categories, featured)
            
            # Create inline keyboard
            keyboard_rows = []
            
            # First row - main categories
            row1 = []
            for cat in categories[:5]:
                emoji = self.ui.category_emojis.get(cat, '📸')
                row1.append(InlineKeyboardButton(
                    text=f"{emoji} {cat.title()}",
                    callback_data=f"fetch_{cat}"
                ))
            keyboard_rows.append(row1)
            
            # Second row - remaining categories
            row2 = []
            for cat in categories[5:]:
                emoji = self.ui.category_emojis.get(cat, '📸')
                row2.append(InlineKeyboardButton(
                    text=f"{emoji} {cat.title()}",
                    callback_data=f"fetch_{cat}"
                ))
            if row2:
                keyboard_rows.append(row2)
            
            # Special category buttons
            keyboard_rows.append([
                InlineKeyboardButton(
                    text="🎲 Random Category 🎲",
                    callback_data="fetch_random"
                ),
                InlineKeyboardButton(
                    text="⭐ Featured Today ⭐",
                    callback_data=f"fetch_{featured}"
                )
            ])
            
            # Navigation buttons
            keyboard_rows.append([
                InlineKeyboardButton(
                    text="🔙 Back to Menu 🔙",
                    callback_data="main_menu"
                ),
                InlineKeyboardButton(
                    text="💎 Premium Access 💎",
                    callback_data="premium_info"
                )
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard_rows)
            
            sent_message = await update.message.reply_text(
                text=categories_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # Set random reaction
            await self.reactions.set_random_reaction(
                context.bot,
                update.effective_chat.id,
                sent_message.message_id
            )
            
            return sent_message
            
        except Exception as e:
            logger.error(f"❌ Error in categories command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, couldn't load categories. Please try again later."
            )
    
    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /help command with beautiful UI"""
        try:
            help_text = self.ui.get_help_message()
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        text="🖼️ Start Fetching 🎨",
                        callback_data="fetch_main"
                    ),
                    InlineKeyboardButton(
                        text="📂 Browse Categories 📚",
                        callback_data="categories_main"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="💎 Premium Benefits ✨",
                        callback_data="premium_info"
                    ),
                    InlineKeyboardButton(
                        text="ℹ️ Bot Information ℹ️",
                        callback_data="info_main"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="👤 Contact Owner 💭",
                        url=f"https://t.me/{self.config.OWNER_USERNAME.lstrip('@')}"
                    )
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            sent_message = await update.message.reply_text(
                text=help_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # Set random reaction
            await self.reactions.set_random_reaction(
                context.bot,
                update.effective_chat.id,
                sent_message.message_id
            )
            
            return sent_message
            
        except Exception as e:
            logger.error(f"❌ Error in help command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, couldn't load help. Please try again later."
            )
    
    async def _schedule_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /schedule command with beautiful UI"""
        try:
            # Parse arguments
            if len(context.args) < 2:
                help_text = """
⏰ **Schedule Setup** ⏰

📋 **Usage:** /schedule <interval> <category>

🎯 **Available Intervals:**
• hourly - Every hour
• daily - Once per day
• weekly - Once per week

📂 **Available Categories:**
""" + '\n'.join([f"• {cat}" for cat in self.config.WALLPAPER_CATEGORIES])

💡 **Example:** /schedule daily nature

📱 **Works in:** Groups, channels, and private chats

💫 "Let automation bring beauty to your chat!" 💫
"""
                
                return await update.message.reply_text(help_text, parse_mode='Markdown')
            
            interval = context.args[0].lower()
            category = context.args[1].lower()
            
            # Validate inputs
            valid_intervals = ['hourly', 'daily', 'weekly']
            if interval not in valid_intervals:
                return await update.message.reply_text(
                    f"❌ Invalid interval. Use: {', '.join(valid_intervals)}"
                )
            
            if category not in self.config.WALLPAPER_CATEGORIES:
                return await update.message.reply_text(
                    f"❌ Invalid category. Use: {', '.join(self.config.WALLPAPER_CATEGORIES)}"
                )
            
            # Set up schedule in database
            if self.db_client:
                await self.db_client.set_schedule(update.effective_chat.id, category, interval)
            
            # Create beautiful confirmation
            schedule_text = self.ui.get_schedule_success_message(interval, category)
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        text="🖼️ Test Now 🎨",
                        callback_data=f"fetch_{category}"
                    )
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            sent_message = await update.message.reply_text(
                text=schedule_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # Set random reaction
            await self.reactions.set_random_reaction(
                context.bot,
                update.effective_chat.id,
                sent_message.message_id
            )
            
            return sent_message
            
        except Exception as e:
            logger.error(f"❌ Error in schedule command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, couldn't set up schedule. Please try again later."
            )
    
    async def _report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /report command with beautiful UI"""
        try:
            if not context.args:
                return await update.message.reply_text(
                    "⚠️ Please provide a description of the issue.\n"
                    "Usage: /report <description of the problem>\n\n"
                    "Example: /report Bot is not sending wallpapers"
                )
            
            report_text = ' '.join(context.args)
            user = update.effective_user
            
            # Log the report
            if self.db_client:
                await self.db_client.log_event(
                    level='REPORT',
                    message=f"User {user.id}: {report_text}",
                    user_id=user.id
                )
            
            # Create beautiful confirmation
            confirmation = self.ui.get_report_success_message(report_text, user.first_name, user.id)
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        text="👤 Contact Owner 💭",
                        url=f"https://t.me/{self.config.OWNER_USERNAME.lstrip('@')}"
                    ),
                    InlineKeyboardButton(
                        text="🖼️ Continue Using Bot 🎨",
                        callback_data="fetch_main"
                    )
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            sent_message = await update.message.reply_text(
                text=confirmation,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # Set random reaction
            await self.reactions.set_random_reaction(
                context.bot,
                update.effective_chat.id,
                sent_message.message_id
            )
            
            return sent_message
            
        except Exception as e:
            logger.error(f"❌ Error in report command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, couldn't submit your report. Please try again later."
            )
    
    async def _feedback_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
        """Handle /feedback command with beautiful UI"""
        try:
            if not context.args:
                return await update.message.reply_text(
                    "💬 Please provide your feedback message.\n"
                    "Usage: /feedback <your message>\n\n"
                    "Example: /feedback Love the bot! Add more categories please!"
                )
            
            feedback_text = ' '.join(context.args)
            user = update.effective_user
            
            # Log the feedback
            if self.db_client:
                await self.db_client.log_event(
                    level='FEEDBACK',
                    message=f"User {user.id}: {feedback_text}",
                    user_id=user.id
                )
            
            # Create beautiful confirmation
            confirmation = self.ui.get_feedback_success_message(feedback_text, user.first_name, user.id)
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        text="📊 My Statistics 📈",
                        callback_data="my_stats"
                    ),
                    InlineKeyboardButton(
                        text="🖼️ More Wallpapers 🎨",
                        callback_data="fetch_main"
                    )
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            sent_message = await update.message.reply_text(
                text=confirmation,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # Set random reaction
            await self.reactions.set_random_reaction(
                context.bot,
                update.effective_chat.id,
                sent_message.message_id
            )
            
            return sent_message
            
        except Exception as e:
            logger.error(f"❌ Error in feedback command: {e}")
            return await update.message.reply_text(
                "❌ Sorry, couldn't send your feedback. Please try again later."
            )
    
    # Helper methods
    async def _ensure_user_exists(self, user_id: int, username: str, first_name: str) -> None:
        """Ensure user exists in database"""
        if self.db_client:
            user_data = await self.db_client.get_user(user_id)
            if not user_data:
                await self.db_client.create_user(user_id, username, first_name)
    
    async def _check_fetch_allowance(self, user_id: int) -> tuple[bool, int]:
        """Check if user can fetch wallpapers"""
        user_data = await self.db_client.get_user(user_id)
        
        if not user_data:
            return True, self.config.FREE_FETCH_LIMIT
        
        if user_data.get('banned', False):
            return False, 0
        
        if user_data.get('tier') == 'premium':
            return True, float('inf')  # Unlimited for premium
        
        # Check daily limit for free users
        today_fetches = await self._get_today_fetches(user_id)
        remaining = self.config.FREE_FETCH_LIMIT - today_fetches
        
        return remaining > 0, max(0, remaining)
    
    async def _get_today_fetches(self, user_id: int) -> int:
        """Get today's fetch count for user"""
        if not self.db_client:
            return 0
            
        user_data = await self.db_client.get_user(user_id)
        if not user_data:
            return 0
        
        today = datetime.utcnow().date()
        last_fetch = user_data.get('last_fetch_date')
        
        if last_fetch and last_fetch.date() == today:
            return user_data.get('fetch_count', 0)
        else:
            # Reset count if it's a new day
            await self.db_client.update_user(user_id, {'fetch_count': 0})
            return 0
    
    async def _record_wallpaper_fetch(self, user_id: int, wallpaper_info: dict) -> None:
        """Record wallpaper fetch in database"""
        if self.db_client:
            await self.db_client.update_user_fetch_count(user_id)
            await self.db_client.log_event(
                level='INFO',
                message=f"User {user_id} fetched wallpaper from {wallpaper_info.get('source', 'unknown')}",
                user_id=user_id
            )
