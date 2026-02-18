from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from app.models.user import UserDB, UserRole
import os
from database import get_db

# Configuration - Auth disabled for hackathon
SECRET_KEY = os.getenv("SECRET_KEY", "hackathon-mode")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

async def get_current_user(x_user_phone: Optional[str] = Header(None, alias="X-User-Phone")):
    """
    Hackathon Authentication:
    - If 'X-User-Phone' header is present, try to find that user.
    - If not, return/create a default 'hackathon_owner' user.
    """
    db = get_db()
    
    phone = x_user_phone if x_user_phone else "9999999999"
    
    user = await db["users"].find_one({"phone": phone})
    
    if user is None:
        # Auto-create mock user if it doesn't exist
        mock_user = {
            "name": "Hackathon User",
            "phone": phone,
            "role": UserRole.OWNER if phone == "9999999999" else UserRole.RENTER,
            "password_hash": "mock_hash",
            "location": {"type": "Point", "coordinates": [0.0, 0.0]}
        }
        await db["users"].insert_one(mock_user)
        user = await db["users"].find_one({"phone": phone})
        
    return UserDB(**user)

# Keep these for compatibility if needed, or they can be unused
def verify_password(plain_password, hashed_password):
    return True

def get_password_hash(password):
    return "mock_hash"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    return "mock_token"
