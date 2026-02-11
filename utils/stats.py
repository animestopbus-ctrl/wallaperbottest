"""
LastPerson07Bot Statistics Module
Handles collection and analysis of bot statistics
"""

import logging
import psutil
import platform
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class LastPerson07Stats:
    """Comprehensive statistics collection and analysis"""
    
    def __init__(self, db_client):
        """Initialize statistics collector"""
        self.db_client = db_client
    
    async def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive bot statistics"""
        try:
            stats = {}
            
            # User statistics
            stats['users'] = await self._get_user_stats()
            
            # System statistics
            stats['system'] = await self._get_system_stats()
            
            # Wallpaper statistics
            stats['wallpapers'] = await self._get_wallpaper_stats()
            
            # Financial statistics
            stats['financial'] = await self._get_financial_stats()
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting comprehensive stats: {e}")
            return {'error': str(e)}
    
    async def _get_user_stats(self) -> Dict[str, Any]:
        """Get user-related statistics"""
        try:
            users_collection = self.db_client.database[self.db_client.COLLECTIONS['users']]
            
            # Basic counts
            total_users = await users_collection.count_documents({})
            premium_users = await users_collection.count_documents({'tier': 'premium'})
            banned_users = await users_collection.count_documents({'banned': True})
            free_users = total_users - premium_users - banned_users
            
            # New users (last 7 days)
            from datetime import timedelta
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            new_users = await users_collection.count_documents({'join_date': {'$gte': seven_days_ago}})
            
            return {
                'total_users': total_users,
                'premium_users': premium_users,
                'free_users': free_users,
                'banned_users': banned_users,
                'new_users_7_days': new_users,
                'premium_percentage': (premium_users / total_users * 100) if total_users > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting user stats: {e}")
            return {'error': str(e)}
    
    async def _get_system_stats(self) -> Dict[str, Any]:
        """Get system-related statistics"""
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory information
            memory = psutil.virtual_memory()
            
            # Disk information
            disk = psutil.disk_usage('/')
            
            # Boot time
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            return {
                'cpu': {
                    'percentage': cpu_percent,
                    'count': cpu_count
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percentage': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percentage': disk.percent
                },
                'uptime': {
                    'hours': uptime.total_seconds() / 3600,
                    'days': uptime.days,
                    'boot_time': boot_time.isoformat()
                },
                'system': {
                    'platform': platform.system(),
                    'platform_release': platform.release(),
                    'platform_version': platform.version(),
                    'python_version': platform.python_version()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting system stats: {e}")
            return {'error': str(e)}
    
    async def _get_wallpaper_stats(self) -> Dict[str, Any]:
        """Get wallpaper-related statistics"""
        try:
            # For demo, return placeholder data
            return {
                'total_fetches': 1000,
                'unique_users': 150,
                'api_status': {
                    'unsplash': 'active',
                    'pexels': 'active',
                    'pixabay': 'active'
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting wallpaper stats: {e}")
            return {'error': str(e)}
    
    async def _get_financial_stats(self) -> Dict[str, Any]:
        """Get financial-related statistics"""
        try:
            users_collection = self.db_client.database[self.db_client.COLLECTIONS['users']
            
            # Premium users count
            premium_users = await users_collection.count_documents({'tier': 'premium'})
            
            # Revenue calculation ($2 per premium user)
            monthly_revenue = premium_users * 2.0
            
            return {
                'premium_users': premium_users,
                'monthly_revenue': monthly_revenue,
                'annual_revenue': monthly_revenue * 12,
                'currency': 'USD'
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting financial stats: {e}")
            return {'error': str(e)}
    
    async def generate_report(self, report_type: str) -> str:
        """Generate formatted report"""
        try:
            stats = await self.get_comprehensive_stats()
            
            if report_type == 'summary':
                return self._format_summary_report(stats)
            elif report_type == 'detailed':
                return self._format_detailed_report(stats)
            elif report_type == 'financial':
                return self._format_financial_report(stats)
            else:
                return "Invalid report type"
                
        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")
            return f"Error generating report: {e}"
    
    def _format_summary_report(self, stats: Dict[str, Any]) -> str:
        """Format summary report"""
        report = f"📊 **Summary Report** 📊\n\n"
        
        if 'users' in stats:
            user_stats = stats['users']
            report += f"👥 **Users:** {user_stats.get('total_users', 0)} total\n"
            report += f"💎 **Premium:** {user_stats.get('premium_users', 0)}\n"
            report += f"🆓 **Free:** {user_stats.get('free_users', 0)}\n\n"
        
        if 'system' in stats:
            system_stats = stats['system']
            report += f"💻 **CPU:** {system_stats.get('cpu', {}).get('percentage', 0)}%\n"
            report += f"🧠 **RAM:** {system_stats.get('memory', {}).get('percentage', 0)}%\n"
            report += f"⏰ **Uptime:** {system_stats.get('uptime', {}).get('hours', 0):.1f}h\n"
        
        return report
    
    def _format_detailed_report(self, stats: Dict[str, Any]) -> str:
        """Format detailed report"""
        # This would create a more detailed report
        return self._format_summary_report(stats) + "\n\n(Detailed report format coming soon)"
    
    def _format_financial_report(self, stats: Dict[str, Any]) -> str:
        """Format financial report"""
        if 'financial' in stats:
            financial_stats = stats['financial']
            return f"💰 **Financial Report** 💰\n\n" + \
                   f"💎 **Premium Users:** {financial_stats.get('premium_users', 0)}\n" + \
                   f"💸 **Monthly Revenue:** ${financial_stats.get('monthly_revenue', 0):.2f}\n" + \
                   f"💵 **Annual Revenue:** ${financial_stats.get('annual_revenue', 0):.2f}\n"
        
        return "No financial data available"
