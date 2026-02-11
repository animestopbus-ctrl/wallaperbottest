"""
LastPerson07Bot UI Module
Beautiful UI templates and formatting utilities
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class LastPerson07UI:
    """Beautiful UI templates and formatting utilities"""
    
    def __init__(self):
        """Initialize UI with beautiful templates"""
        self.templates = {
            'welcome': """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    🌟 Welcome to LastPerson07Bot 🌟                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

💫 "Every wallpaper tells a story, let me help you find yours!" 💫

🎨 **{name}**, I'm delighted to have you here!

🌟 **What I Offer:**
• 🖼️ Stunning wallpapers from Unsplash, Pexels & Pixabay
• ⚡ Lightning-fast delivery with emoji reactions
• 💎 Free tier with 5 daily wallpapers
• 🚀 Premium with unlimited access
• 🎮 Custom emojis & beautiful formatting

🎯 **Quick Start:**
• /fetch nature - Get beautiful nature wallpapers
• /categories - Explore all categories
• /premium - Unlock unlimited access

💫 "Your journey to beautiful wallpapers begins now!" 💫
""",
            
            'premium_info': """
💎 PREMIUM SUBSCRIPTION 💎

🌟 **"Unlock Infinite Beauty with Premium"** 🌟

📊 **Monthly Plan - Just $2**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **Unlimited Wallpaper Downloads**
   🎨 "Download as many as your heart desires!"

✅ **No Advertisements**
   🚫 "Pure, uninterrupted beauty"

✅ **Custom Emoji Support**
   😊 "Express yourself with unique emojis"

✅ **Priority API Access**
   ⚡ "Lightning-fast downloads"

✅ **Advanced Categories**
   📂 "Access to exclusive collections"

✅ **Download Statistics**
   📈 "Track your wallpaper journey"

✅ **Premium Support**
   🤝 "We're here for you 24/7"

🎁 **Limited Time Offer:**
   💰 "Save 20% on annual billing!"

🚀 **Ready to upgrade? Use /buy now!**
""",
            
            'help': """
❓ HELP & USAGE GUIDE ❓

📖 **"Your Complete Guide to Wallpaper Excellence"**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 **Basic Commands**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• /start - Welcome message and bot overview
• /fetch <category> - Get beautiful wallpapers
• /categories - Browse all available categories
• /help - This comprehensive help guide

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 **Premium Features**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• /premium - View premium benefits
• /myplan - Check your subscription status
• /buy - Upgrade to premium access

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ **Advanced Features**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• /schedule <interval> <category> - Auto-post wallpapers
• /report <issue> - Report problems
• /feedback <message> - Send us your thoughts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **Pro Tips**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• "Use specific categories for better results"
• "Set up schedules in groups for automatic wallpapers"
• "Premium users enjoy unlimited downloads"
• "Contact us anytime for support!"

🤖 "We're here to make your wallpaper journey amazing!"
""",
            
            'categories': """
📂 BEAUTIFUL CATEGORIES 📂

🌈 "Find your perfect wallpaper from our curated collection"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{categories_grid}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **Pro Tip:** 
   "Try different categories to match your mood!"

🎨 **Featured Today:** {featured_category}
""",
            
            'fetch_limit': """
⚠️ **Daily Limit Reached** ⚠️

📊 **Your Status:**
• 🆓 Free Plan: {limit} wallpapers/day
• 📅 Daily limit resets at 00:00 UTC
• 💎 Upgrade to Premium for unlimited access

💫 "Upgrade to Premium and unlock infinite beauty!" 💫

💎 Use /premium to upgrade now!
""",
            
            'fetch_error': """
❌ **Unable to Fetch Wallpaper** ❌

🎯 **Category:** {category}
📝 **Issue:** All wallpaper sources unavailable

💡 **Suggestions:**
• Try a different category
• Wait a moment and try again
• Contact support if the issue persists

🌟 "Every cloud has a silver lining, try again soon!" 🌟
""",
            
            'report_success': """
✅ **Report Submitted Successfully** ✅

📝 **Issue Details:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 **Report:** {report_text}
👤 **Reported by:** {user_name}
🆔 **User ID:** {user_id}
📅 **Submitted:** {timestamp}

🔧 **Next Steps:**
• Our team will review your report
• Investigation of the issue begins
• Resolution will be implemented
• Follow-up message sent to you

🙏 **Thank you** for helping us improve!
💫 "Your feedback makes us better!" 💫
""",
            
            'feedback_success': """
💬 **Feedback Received** 💬

📝 **Your Message:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{feedback_text}

👤 **Sender Details:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📛 **Name:** {user_name}
🆔 **ID:** {user_id}
📅 **Time:** {timestamp}

🙏 **Thank You!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💫 Your feedback is invaluable to us!
🎯 We'll carefully review and consider your suggestions
🚀 Your input helps us improve and grow

💫 "We appreciate you taking the time to share your thoughts!" 💫
""",
            
            'premium_welcome': """
✨ **Premium Member Welcome** ✨

🎉 **{user_name}**, you're already Premium!

💎 **Your Benefits:**
• 🖼️ Unlimited wallpaper downloads
• ⚡ No advertisements
• 🎮 Custom emoji support
• 🚀 Priority API access
• 📊 Download statistics
• ⭐ Priority support

{expiration_info}

💫 "Thank you for supporting our bot!" 💫
""",
            
            'myplan_status': """
📋 **Your Subscription Status** 📋

👤 **Account Information:**
• 🏷️ **Name:** {user_name}
• 🆔 **User ID:** {user_id}
• 📅 **Joined:** {join_date}

{tier_status} **Current Plan:** {tier_name}

📊 **Usage Statistics:**
• 🖼️ **Total Fetches:** {total_fetches}
• 📅 **Today's Fetches:** {today_fetches}/{daily_limit}

{premium_info}

💫 "Thank you for being part of our community!" 💫
""",
            
            'schedule_success': """
✅ **Schedule Set Successfully!** ✅

🎯 **Schedule Details:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{interval_emoji} **Interval:** {interval_desc}
📂 **Category:** {category.title()}
💬 **Chat:** This chat

🎉 **Bot will now automatically send beautiful {category.title()} wallpapers!**

{upgrade_promo}

💫 "Beauty delivered automatically to your chat!" 💫
""",
            
            'buy_process': """
💳 **Premium Purchase Process** 💳

🌟 **Monthly Premium Plan - Just $2**

📋 **Purchase Steps:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1️⃣ **Contact the Bot Owner**
   💬 Click the button below to start

2️⃣ **Send Payment Request**
   💰 Owner will provide payment details

3️⃣ **Complete Payment**
   💳 $2 via available payment methods

4️⃣ **Premium Activation**
   🚀 Owner activates your premium immediately

💎 **Premium Benefits:**
• 🖼️ Unlimited wallpaper downloads
• ⚡ No advertisements
• 🎮 Custom emoji support
• 🚀 Priority API access
• 📊 Download statistics
• ⭐ Priority support

🔒 **100% Secure & Safe**
📞 **Support Available Anytime**

💎 **Ready for unlimited beauty?** Click below! 🎉
"""
        }
        
        # Category emojis
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
    
    def get_welcome_message(self, name: str) -> str:
        """Get beautiful welcome message"""
        return self.templates['welcome'].format(name=name)
    
    def get_premium_info(self) -> str:
        """Get premium information message"""
        return self.templates['premium_info']
    
    def get_help_message(self) -> str:
        """Get help message"""
        return self.templates['help']
    
    def get_categories_message(self, categories: List[str], featured_category: str) -> str:
        """Get categories message with grid"""
        # Create category grid
        grid_lines = []
        for i in range(0, len(categories), 2):
            if i + 1 < len(categories):
                cat1, cat2 = categories[i], categories[i + 1]
                emoji1 = self.category_emojis.get(cat1, '📸')
                emoji2 = self.category_emojis.get(cat2, '📸')
                grid_lines.append(f"│ {emoji1} {cat1.title():<15} │ {emoji2} {cat2.title():<15} │")
            else:
                cat = categories[i]
                emoji = self.category_emojis.get(cat, '📸')
                grid_lines.append(f"│ {emoji} {cat.title():<15} │ {'':<15} │")
        
        grid_text = '\n'.join(grid_lines)
        
        return self.templates['categories'].format(
            categories_grid=grid_text,
            featured_category=featured_category.title()
        )
    
    def get_fetch_limit_message(self, limit: int) -> str:
        """Get fetch limit message"""
        return self.templates['fetch_limit'].format(limit=limit)
    
    def get_fetch_error_message(self, category: str) -> str:
        """Get fetch error message"""
        return self.templates['fetch_error'].format(category=category)
    
    def get_report_success_message(self, report_text: str, user_name: str, user_id: int) -> str:
        """Get report success message"""
        return self.templates['report_success'].format(
            report_text=report_text,
            user_name=user_name,
            user_id=user_id,
            timestamp=datetime.now().strftime('%B %d, %Y at %I:%M %p')
        )
    
    def get_feedback_success_message(self, feedback_text: str, user_name: str, user_id: int) -> str:
        """Get feedback success message"""
        return self.templates['feedback_success'].format(
            feedback_text=feedback_text,
            user_name=user_name,
            user_id=user_id,
            timestamp=datetime.now().strftime('%B %d, %Y at %I:%M %p')
        )
    
    def get_premium_welcome_message(self, user_name: str, expiration_date: str = None) -> str:
        """Get premium welcome message"""
        expiration_info = ""
        if expiration_date:
            expiration_info = f"📅 **Expires:** {expiration_date}"
        else:
            expiration_info = "🌟 **Lifetime Premium**"
        
        return self.templates['premium_welcome'].format(
            user_name=user_name,
            expiration_info=expiration_info
        )
    
    def get_myplan_status_message(
        self, 
        user_name: str, 
        user_id: int, 
        tier: str, 
        total_fetches: int, 
        today_fetches: int, 
        daily_limit: int,
        join_date: str = None
    ) -> str:
        """Get myplan status message"""
        if tier == 'premium':
            tier_status = "💎"
            tier_name = "Premium"
            premium_info = "✨ **Enjoying unlimited access!**"
            daily_limit_text = "∞"
        else:
            tier_status = "🆓"
            tier_name = "Free"
            premium_info = "⚠️ **Daily Limit:**"
            daily_limit_text = str(daily_limit)
        
        join_date_str = join_date or "Unknown"
        
        return self.templates['myplan_status'].format(
            user_name=user_name,
            user_id=user_id,
            tier_status=tier_status,
            tier_name=tier_name,
            total_fetches=total_fetches,
            today_fetches=today_fetches,
            daily_limit=daily_limit_text,
            premium_info=premium_info,
            join_date=join_date_str
        )
    
    def get_schedule_success_message(
        self, 
        interval: str, 
        category: str, 
        is_premium: bool = False
    ) -> str:
        """Get schedule success message"""
        interval_desc = self.interval_descriptions.get(interval, interval.title())
        interval_emoji = self.interval_emojis.get(interval, '⏰')
        
        upgrade_promo = ""
        if not is_premium:
            upgrade_promo = "💎 **Premium users** can set multiple schedules!"
        
        return self.templates['schedule_success'].format(
            interval_emoji=interval_emoji,
            interval_desc=interval_desc,
            category=category,
            upgrade_promo=upgrade_promo
        )
    
    def get_buy_process_message(self) -> str:
        """Get buy process message"""
        return self.templates['buy_process']
