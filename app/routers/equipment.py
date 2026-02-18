from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.auth import get_current_user
from app.models.user import UserDB, UserRole
from app.models.equipment import EquipmentCreate, EquipmentResponse, EquipmentDB, Location
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

@router.get("/nearby", response_model=List[EquipmentResponse])
async def get_nearby_equipment(lat: float, long: float, radius_km: float = 10.0):
    db = get_db()
    # Ensure 2dsphere index exists on 'location' field
    
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
