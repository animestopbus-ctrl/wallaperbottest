"""
LastPerson07Bot Database Models Module
Defines data structures and validation using Pydantic
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator

class User(BaseModel):
    """User model representing Telegram bot users"""
    user_id: int = Field(..., alias='_id', description="Telegram user ID")
    username: Optional[str] = Field(None, description="Telegram username")
    first_name: str = Field(..., description="User's first name")
    tier: str = Field(default='free', description="User tier: 'free' or 'premium'")
    fetch_count: int = Field(default=0, description="Total fetch count")
    last_fetch_date: Optional[datetime] = Field(None, description="Last fetch timestamp")
    join_date: datetime = Field(default_factory=datetime.utcnow, description="User join date")
    banned: bool = Field(default=False, description="Whether user is banned")
    expiration: Optional[datetime] = Field(None, description="Premium expiration date")
    
    @validator('tier')
    def validate_tier(cls, v):
        if v not in ['free', 'premium']:
            raise ValueError('Tier must be either "free" or "premium"')
        return v
    
    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class WallpaperInfo(BaseModel):
    """Wallpaper information model"""
    url: str = Field(..., description="Image URL")
    source: str = Field(..., description="Source name")
    width: int = Field(..., description="Image width")
    height: int = Field(..., description="Image height")
    description: Optional[str] = Field(None, description="Image description")
    photographer: Optional[str] = Field(None, description="Photographer name")
    photographer_url: Optional[str] = Field(None, description="Photographer profile URL")
    download_url: str = Field(..., description="Download URL")
    category: Optional[str] = Field(None, description="Image category")
    
    @validator('width', 'height')
    def validate_dimensions(cls, v):
        if v <= 0:
            raise ValueError('Dimensions must be positive')
        return v

class PremiumPlan(BaseModel):
    """Premium subscription plan model"""
    name: str = Field(..., description="Plan name")
    price: float = Field(..., description="Monthly price in USD")
    features: List[str] = Field(..., description="List of features")
    duration_days: int = Field(default=30, description="Plan duration in days")
    description: Optional[str] = Field(None, description="Plan description")
    
    @validator('price')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('Price cannot be negative')
        return v
