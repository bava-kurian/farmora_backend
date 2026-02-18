from pydantic import BaseModel, Field
from typing import Optional, List
from app.models.shared import PyObjectId, Location
from enum import Enum

class EquipmentStatus(str, Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    MAINTENANCE = "maintenance"

class EquipmentBase(BaseModel):
    owner_id: PyObjectId
    equipment_type: str
    description: str
    hourly_price: float
    daily_price: float
    availability_status: EquipmentStatus = EquipmentStatus.AVAILABLE
    location: Location
    images: List[str] = []

class EquipmentCreate(BaseModel):
    equipment_type: str
    description: str
    hourly_price: float
    daily_price: float
    location_lat: float
    location_long: float
    images: List[str] = []

class EquipmentDB(EquipmentBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    rating: float = 0.0
    review_count: int = 0

    class Config:
        populate_by_name = True
        json_encoders = {PyObjectId: str}

class EquipmentResponse(EquipmentDB):
    pass
