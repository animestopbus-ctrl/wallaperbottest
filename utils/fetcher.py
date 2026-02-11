"""
LastPerson07Bot Wallpaper Fetcher Module
Handles fetching wallpapers from various sources
"""

import asyncio
import logging
import random
from typing import Optional, Dict, Any, List

import aiohttp
import requests
from PIL import Image
import io

from config.config import LastPerson07Config

logger = logging.getLogger(__name__)

class LastPerson07WallpaperFetcher:
    """Wallpaper fetcher with fallback chain support"""
    
    def __init__(self, db_client, config: LastPerson07Config):
        """Initialize the wallpaper fetcher"""
        self.db_client = db_client
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        
        # API configurations
        self.apis = {
            'unsplash': {
                'base_url': 'https://api.unsplash.com',
                'endpoint': '/photos/random',
                'headers': lambda key: {'Authorization': f'Client-ID {key}'} if key else {},
                'params': {
                    'orientation': 'landscape',
                    'content_filter': 'high',
                    'w': 1920,
                    'h': 1080
                }
            },
            'pexels': {
                'base_url': 'https://api.pexels.com/v1',
                'endpoint': '/curated',
                'headers': lambda key: {'Authorization': key} if key else {},
                'params': {
                    'per_page': 1,
                    'orientation': 'landscape'
                }
            },
            'pixabay': {
                'base_url': 'https://pixabay.com/api',
                'endpoint': '/',
                'headers': lambda key: {},
                'params': {
                    'key': key if key else 'demo-key',
                    'per_page': 1,
                    'image_type': 'photo',
                    'orientation': 'horizontal',
                    'min_width': 1920,
                    'min_height': 1080,
                    'category': 'nature',
                    'safesearch': 'true'
                }
            }
        }
    
    async def initialize(self) -> None:
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'LastPerson07Bot/2.0.0'}
        )
        logger.info("✅ Wallpaper fetcher initialized")
    
    async def close(self) -> None:
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            logger.info("✅ Wallpaper fetcher closed")
    
    async def fetch_wallpaper(self, category: str = 'nature') -> Optional[Dict[str, Any]]:
        """Fetch wallpaper information with fallback chain"""
        if not self.session:
            await self.initialize()
        
        # Get active APIs in priority order
        active_apis = await self._get_active_apis()
        
        for api_config in active_apis:
            try:
                logger.info(f"🔄 Trying API: {api_config['source_name']}")
                
                wallpaper_info = await self._fetch_from_api(api_config, category)
                
                if wallpaper_info:
                    logger.info(f"✅ Successfully fetched wallpaper from {api_config['source_name']}")
                    return wallpaper_info
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed to fetch from {api_config['source_name']}: {e}")
                continue
        
        logger.error("❌ All APIs failed to fetch wallpaper")
        return None
    
    async def _get_active_apis(self) -> List[Dict[str, Any]]:
        """Get list of active API configurations sorted by priority"""
        active_apis = []
        
        # Add APIs with keys
        if self.config.UNSPLASH_KEY:
            active_apis.append({
                'source_name': 'unsplash',
                'url': f"{self.apis['unsplash']['base_url']}{self.apis['unsplash']['endpoint']}",
                'api_key': self.config.UNSPLASH_KEY,
                'priority': 1
            })
        
        if self.config.PEXELS_KEY:
            active_apis.append({
                'source_name': 'pexels',
                'url': f"{self.apis['pexels']['base_url']}{self.apis['pexels']['endpoint']}",
                'api_key': self.config.PEXELS_KEY,
                'priority': 2
            })
        
        if self.config.PIXABAY_KEY:
            active_apis.append({
                'source_name': 'pixabay',
                'url': f"{self.apis['pixabay']['base_url']}{self.apis['pixabay']['endpoint']}",
                'api_key': self.config.PIXABAY_KEY,
                'priority': 3
            })
        
        # If no APIs have keys, use demo data
        if not active_apis:
            active_apis = [
                {
                    'source_name': 'demo',
                    'url': 'https://picsum.photos/1920/1080',
                    'api_key': '',
                    'priority': 99
                }
            ]
        
        # Sort by priority
        active_apis.sort(key=lambda x: x['priority'])
        return active_apis
    
    async def _fetch_from_api(self, api_config: Dict[str, Any], category: str) -> Optional[Dict[str, Any]]:
        """Fetch wallpaper from a specific API"""
        source_name = api_config['source_name']
        
        if source_name == 'demo':
            # Return demo data
            return {
                'url': f"https://picsum.photos/1920/1080?random={random.randint(1, 1000)}",
                'source': 'demo',
                'width': 1920,
                'height': 1080,
                'description': f'Beautiful {category} wallpaper',
                'photographer': 'Demo Photographer',
                'download_url': f"https://picsum.photos/1920/1080?random={random.randint(1, 1000)}"
            }
        
        api_info = self.apis.get(source_name)
        if not api_info:
            logger.error(f"Unknown source: {source_name}")
            return None
        
        # Build URL and parameters
        url = api_config['url']
        headers = api_info['headers'](api_config.get('api_key', ''))
        params = api_info['params'].copy()
        
        # Add category-specific parameters
        if source_name == 'unsplash':
            params['query'] = category
        elif source_name == 'pexels':
            params['query'] = category
        elif source_name == 'pixabay':
            params['category'] = category if category in ['nature', 'animals', 'people'] else ''
        
        try:
            # Make request
            if self.session:
                async with self.session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        logger.error(f"API request failed: {response.status}")
                        return None
                    
                    data = await response.json()
            else:
                # Fallback to requests
                import requests
                response = requests.get(url, headers=headers, params=params)
                if response.status_code != 200:
                    logger.error(f"API request failed: {response.status}")
                    return None
                data = response.json()
            
            # Parse response based on API
            if source_name == 'unsplash':
                return await self._parse_unsplash_response(data)
            elif source_name == 'pexels':
                return await self._parse_pexels_response(data)
            elif source_name == 'pixabay':
                return await self._parse_pixabay_response(data)
            
        except Exception as e:
            logger.error(f"Error fetching from {source_name}: {e}")
            return None
        
        return None
    
    async def _parse_unsplash_response(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Unsplash API response"""
        try:
            return {
                'url': data['urls']['regular'],
                'source': 'unsplash',
                'width': data['width'],
                'height': data['height'],
                'description': data.get('description') or data.get('alt_description'),
                'photographer': data['user']['name'],
                'photographer_url': data['user']['links']['html'],
                'download_url': data['links']['download_location']
            }
        except Exception as e:
            logger.error(f"Error parsing Unsplash response: {e}")
            return None
    
    async def _parse_pexels_response(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Pexels API response"""
        try:
            if not data.get('photos'):
                return None
            
            photo = data['photos'][0]
            return {
                'url': photo['src']['large'],
                'source': 'pexels',
                'width': photo['width'],
                'height': photo['height'],
                'description': photo.get('alt'),
                'photographer': photo['photographer'],
                'photographer_url': photo['photographer_url'],
                'download_url': photo['src']['original']
            }
        except Exception as e:
            logger.error(f"Error parsing Pexels response: {e}")
            return None
    
    async def _parse_pixabay_response(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Pixabay API response"""
        try:
            if not data.get('hits'):
                return None
            
            photo = data['hits'][0]
            return {
                'url': photo['webformatURL'],
                'source': 'pixabay',
                'width': photo['imageWidth'],
                'height': photo['imageHeight'],
                'description': photo.get('tags'),
                'photographer': photo.get('user', 'Pixabay User'),
                'photographer_url': f"https://pixabay.com/users/{photo.get('user_id', '')}",
                'download_url': photo['largeImageURL']
            }
        except Exception as e:
            logger.error(f"Error parsing Pixabay response: {e}")
            return None
    
    async def download_image(self, url: str) -> Optional[bytes]:
        """Download image from URL"""
        try:
            if self.session:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.read()
            
            # Fallback to requests
            response = requests.get(url)
            if response.status_code == 200:
                return response.content
                
            return None
            
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            return None
    
    async def validate_image_url(self, url: str) -> bool:
        """Validate if image URL is accessible"""
        try:
            if self.session:
                async with self.session.get(url) as response:
                    return response.status == 200
            
            # Fallback to requests
            response = requests.head(url)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error validating image URL: {e}")
            return False
