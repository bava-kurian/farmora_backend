from pydantic import BaseModel, Field
from app.models.shared import PyObjectId
from datetime import datetime

class ReviewBase(BaseModel):
    booking_id: PyObjectId
    rating: float = Field(..., ge=1, le=5)
    review_text: str

class ReviewCreate(BaseModel):
    booking_id: str
    rating: float = Field(..., ge=1, le=5)
    review_text: str

class ReviewDB(ReviewBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)
    reviewer_id: PyObjectId
    equipment_id: PyObjectId

    class Config:
        populate_by_name = True
        json_encoders = {PyObjectId: str}

class ReviewResponse(ReviewDB):
    pass
