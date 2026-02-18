from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from app.models.shared import PyObjectId
from datetime import datetime

class Product(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., description="Name of the product")
    category: str = Field(..., description="Category of the product (e.g., Fertilizers, Tools, Seeds)")
    description: str = Field(..., description="Detailed description of the product")
    original_price: float = Field(..., description="Original market price")
    our_price: float = Field(..., description="Discounted price")
    seller: str = Field(..., description="Name of the seller/vendor")
    image: str = Field(..., description="Base64 encoded image string")
    stock: int = Field(default=100, description="Available stock")
    rating: float = Field(default=0.0, description="Average rating")
    
    class Config:
        populate_by_name = True
        json_encoders = {PyObjectId: str}

class CartItem(BaseModel):
    product_id: str
    quantity: int = 1
    
class Cart(BaseModel):
    user_id: str = Field(..., description="User's mobile number or ID")
    items: List[CartItem] = []
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {PyObjectId: str}

class CartResponse(BaseModel):
    items: List[dict] # detailed items with product info
    total_price: float
    total_items: int

