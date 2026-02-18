from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from app.models.user import UserCreate, UserResponse, UserDB, Location
from database import get_db

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    db = get_db()
    existing_user = await db["users"].find_one({"phone": user.phone})
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    user_dict = user.dict()
    user_dict["password_hash"] = get_password_hash(user_dict.pop("password"))
    
    # Ensure location is properly formatted if provided
    if user_dict.get("location"):
         user_dict["location"]["type"] = "Point"
    
    new_user = await db["users"].insert_one(user_dict)
    created_user = await db["users"].find_one({"_id": new_user.inserted_id})
    return UserDB(**created_user)

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_db()
    user = await db["users"].find_one({"phone": form_data.username}) # Using phone as username
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["phone"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserDB = Depends(get_current_user)):
    return current_user
