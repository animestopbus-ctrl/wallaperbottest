"""
LastPerson07Bot Metadata Module
Image processing and validation utilities
"""

import logging
import io
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

import cv2
import numpy as np
from PIL import Image, ImageStat

logger = logging.getLogger(__name__)

class LastPerson07ImageProcessor:
    """Image processing and validation utilities"""
    
    def __init__(self):
        """Initialize the image processor"""
        # Minimum and maximum image dimensions
        self.MIN_WIDTH = 1920
        self.MIN_HEIGHT = 1080
        self.MAX_FILE_SIZE_MB = 20
        
        # Supported formats
        self.SUPPORTED_FORMATS = ['JPEG', 'PNG', 'WEBP', 'JPG']
    
    async def validate_image(self, image_data: bytes) -> bool:
        """Validate image meets quality requirements"""
        try:
            # Convert bytes to image
            image = Image.open(io.BytesIO(image_data))
            
            # Check format
            if image.format not in self.SUPPORTED_FORMATS:
                logger.warning(f"Unsupported image format: {image.format}")
                return False
            
            # Check dimensions
            width, height = image.size
            if width < self.MIN_WIDTH or height < self.MIN_HEIGHT:
                logger.warning(f"Image too small: {width}x{height} < {self.MIN_WIDTH}x{self.MIN_HEIGHT}")
                return False
            
            # Check file size
            file_size_mb = len(image_data) / (1024 * 1024)
            if file_size_mb > self.MAX_FILE_SIZE_MB:
                logger.warning(f"File too large: {file_size_mb:.2f}MB > {self.MAX_FILE_SIZE_MB}MB")
                return False
            
            logger.debug(f"✅ Image validation passed: {width}x{height}, {image.format}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating image: {e}")
            return False
    
    async def extract_metadata(self, image_data: bytes) -> Dict[str, Any]:
        """Extract metadata from image"""
        try:
            # Open image with PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Basic metadata
            metadata = {
                'format': image.format,
                'mode': image.mode,
                'size': image.size,
                'width': image.width,
                'height': image.height,
                'file_size_bytes': len(image_data),
                'file_size_mb': len(image_data) / (1024 * 1024)
            }
            
            # Color analysis
            stat = ImageStat.Stat(image)
            metadata['color_stats'] = {
                'mean_red': stat.mean[0],
                'mean_green': stat.mean[1],
                'mean_blue': stat.mean[2],
                'std_red': stat.stddev[0],
                'std_green': stat.stddev[1],
                'std_blue': stat.stddev[2]
            }
            
            # Aspect ratio
            width, height = image.size
            metadata['aspect_ratio'] = width / height
            
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Error extracting metadata: {e}")
            return {'error': str(e)}
