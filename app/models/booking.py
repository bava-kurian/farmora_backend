from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.shared import PyObjectId
from enum import Enum

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class BookingBase(BaseModel):
    equipment_id: PyObjectId
    renter_id: PyObjectId
    start_time: datetime
    end_time: datetime
    total_price: float
    status: BookingStatus = BookingStatus.PENDING

class BookingCreate(BaseModel):
    equipment_id: str
    start_time: datetime
    end_time: datetime

class BookingDB(BookingBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        json_encoders = {PyObjectId: str}

class BookingResponse(BookingDB):
    pass
