from pydantic import BaseModel, Field
from typing import Optional, List
from app.models.shared import PyObjectId, Location
from enum import Enum

class UserRole(str, Enum):
    OWNER = "owner"
    RENTER = "renter"

class UserBase(BaseModel):
    mobile_number: str = Field(..., description="User's phone number")
    name: Optional[str] = None
    role: Optional[UserRole] = None
    location: Optional[Location] = None
    acres_land: Optional[float] = None
    years_experience: Optional[int] = None
    crops_rotation: Optional[List[str]] = Field(default_factory=list)

class UserRegister(BaseModel):
    mobile_number: str

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    acres_land: Optional[float] = None
    years_experience: Optional[int] = None

class UserCropsUpdate(BaseModel):
    crops_rotation: List[str]

class UserDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    password_hash: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {PyObjectId: str}

class UserResponse(UserBase):
    id: PyObjectId = Field(alias="_id")

    class Config:
        populate_by_name = True
