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
    

    if not x_user_phone:
        # Fallback for testing/hackathon mode without header
        mobile_number = "9999999999"
    else:
        mobile_number = x_user_phone

    user = await db["users"].find_one({"mobile_number": mobile_number})
    
    if user is None:
        if mobile_number == "9999999999":
             # Auto-create ONLY the default mock user if it doesn't exist
            mock_user = {
                "name": "Hackathon User",
                "mobile_number": mobile_number,
                "role": UserRole.OWNER,
                "password_hash": "mock_hash",
                "location": {"type": "Point", "coordinates": [0.0, 0.0]}
            }
            await db["users"].insert_one(mock_user)
            user = await db["users"].find_one({"mobile_number": mobile_number})
        else:
             # Genuine access attempt with non-existent user
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not registered. Please register first.",
            )
        
    return UserDB(**user)

# Keep these for compatibility if needed, or they can be unused
def verify_password(plain_password, hashed_password):
    return True

def get_password_hash(password):
    return "mock_hash"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    return "mock_token"
