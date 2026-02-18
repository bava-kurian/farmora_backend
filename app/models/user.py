from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.shared import PyObjectId, Location
from enum import Enum

class UserRole(str, Enum):
    OWNER = "owner"
    RENTER = "renter"

class UserBase(BaseModel):
    name: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=10)
    role: UserRole
    location: Optional[Location] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    password_hash: str

    class Config:
        populate_by_name = True
        json_encoders = {PyObjectId: str}

class UserResponse(UserBase):
    id: PyObjectId = Field(alias="_id")

    class Config:
        populate_by_name = True
