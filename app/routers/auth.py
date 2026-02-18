from fastapi import APIRouter, Depends, HTTPException, Body
from app.auth import get_current_user
from app.models.user import UserRegister, UserResponse, UserDB, UserProfileUpdate, UserCropsUpdate, UserRole
from database import get_db

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    db = get_db()
    existing_user = await db["users"].find_one({"mobile_number": user_data.mobile_number})
    if existing_user:
        return UserDB(**existing_user)
    
    new_user_dict = {
        "mobile_number": user_data.mobile_number,
        "name": None,
        "role": None,
        "location": None,
        "acres_land": None,
        "years_experience": None,
        "crops_rotation": []
    }
    
    result = await db["users"].insert_one(new_user_dict)
    created_user = await db["users"].find_one({"_id": result.inserted_id})
    return UserDB(**created_user)

@router.post("/updateprofile", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: UserDB = Depends(get_current_user)
):
    db = get_db()
    
    update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
    
    if update_data:
        # Check if id needs to be objectId
        await db["users"].update_one(
            {"mobile_number": current_user.mobile_number}, # PyObjectId fits here
            {"$set": update_data}
        )
        
    updated_user = await db["users"].find_one({"mobile_number": current_user.mobile_number})
    return UserDB(**updated_user)

@router.post("/updatecrops", response_model=UserResponse)
async def update_crops(
    crops_data: UserCropsUpdate,
    current_user: UserDB = Depends(get_current_user)
):
    db = get_db()
    await db["users"].update_one(
        {"mobile_number": current_user.mobile_number},
        {"$set": {"crops_rotation": crops_data.crops_rotation}}
    )
    
    updated_user = await db["users"].find_one({"mobile_number": current_user.mobile_number})
    return UserDB(**updated_user)

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserDB = Depends(get_current_user)):
    return current_user
