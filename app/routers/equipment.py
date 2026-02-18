from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.auth import get_current_user
from app.models.user import UserDB, UserRole
from app.models.equipment import EquipmentCreate, EquipmentResponse, EquipmentDB, Location, EquipmentCreateByMobile
from database import get_db
from bson import ObjectId

router = APIRouter(prefix="/uber/equipment", tags=["Equipment"])

@router.post("/register", response_model=EquipmentResponse)
async def register_equipment(equipment: EquipmentCreate, current_user: UserDB = Depends(get_current_user)):
    if current_user.role != UserRole.OWNER:
        raise HTTPException(status_code=403, detail="Only owners can register equipment")
    
    db = get_db()
    equipment_dict = equipment.dict()
    equipment_dict["owner_id"] = str(current_user.id)
    equipment_dict["location"] = {
        "type": "Point",
        "coordinates": [equipment.location_long, equipment.location_lat]
    }
    # Remove temporary lat/long fields
    del equipment_dict["location_lat"]
    del equipment_dict["location_long"]

    new_equipment = await db["equipment"].insert_one(equipment_dict)
    created_equipment = await db["equipment"].find_one({"_id": new_equipment.inserted_id})
    return EquipmentDB(**created_equipment)

@router.post("/register-by-mobile", response_model=EquipmentResponse)
async def register_equipment_by_mobile(equipment: EquipmentCreateByMobile):
    db = get_db()
    
    # Check if user exists, else create guest
    user = await db["users"].find_one({"mobile_number": equipment.mobile_number})
    if not user:
        from app.auth import get_password_hash
        user_dict = {
            "name": "Guest Owner",
            "email": f"{equipment.mobile_number}@example.com", # Placeholder
            "mobile_number": equipment.mobile_number,
            "hashed_password": get_password_hash("guest123"),
            "role": UserRole.OWNER,
            "is_active": True
        }
        item = await db["users"].insert_one(user_dict)
        user_id = item.inserted_id
    else:
        user_id = user["_id"]
        # Ensure user has OWNER role or upgrade? For now, assume it's fine or upgrade if needed.
        if user.get("role") != UserRole.OWNER:
             # promote to owner? or just allow. Let's just allow for simplicity or maybe update role.
             pass

    equipment_dict = equipment.dict(exclude={"mobile_number"})
    equipment_dict["owner_id"] = str(user_id)
    equipment_dict["availability_status"] = "available"
    equipment_dict["location"] = {
        "type": "Point",
        "coordinates": [equipment.location_long, equipment.location_lat]
    }
    # Remove temporary lat/long fields
    if "location_lat" in equipment_dict: del equipment_dict["location_lat"]
    if "location_long" in equipment_dict: del equipment_dict["location_long"]

    new_equipment = await db["equipment"].insert_one(equipment_dict)
    created_equipment = await db["equipment"].find_one({"_id": new_equipment.inserted_id})
    return EquipmentDB(**created_equipment)

@router.get("/nearby", response_model=List[EquipmentResponse])
async def get_nearby_equipment(
    lat: float, 
    long: float, 
    radius_km: float = 10.0,
    equipment_type: Optional[str] = Query(None)
):
    db = get_db()
    
    query = {
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [long, lat]
                },
                "$maxDistance": radius_km * 1000 # Convert to meters
            }
        },
        "availability_status": "available"
    }
    
    if equipment_type:
        query["equipment_type"] = equipment_type
    
    cursor = db["equipment"].find(query)
    equipments = await cursor.to_list(length=100)
    return [EquipmentDB(**eq) for eq in equipments]

@router.get("/{id}", response_model=EquipmentResponse)
async def get_equipment(id: str):
    db = get_db()
    equipment = await db["equipment"].find_one({"_id": ObjectId(id)})
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return EquipmentDB(**equipment)
