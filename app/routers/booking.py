from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.auth import get_current_user
from app.models.user import UserDB, UserRole
from app.models.booking import BookingCreate, BookingResponse, BookingDB, BookingStatus, BookingCreateByMobile
from app.models.equipment import EquipmentDB
from database import get_db
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/uber/booking", tags=["Booking"])

@router.post("/create", response_model=BookingResponse)
async def create_booking(booking: BookingCreate, current_user: UserDB = Depends(get_current_user)):
    db = get_db()
    
    # 1. Validate equipment exists
    equipment = await db["equipment"].find_one({"_id": ObjectId(booking.equipment_id)})
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    # 2. Check for conflicts
    # Conflict if (StartA <= EndB) and (EndA >= StartB)
    conflict = await db["bookings"].find_one({
        "equipment_id": ObjectId(booking.equipment_id),
        "status": {"$in": ["pending", "confirmed"]},
        "$or": [
            {"start_time": {"$lte": booking.end_time}, "end_time": {"$gte": booking.start_time}}
        ]
    })
    
    if conflict:
        raise HTTPException(status_code=400, detail="Equipment is not available for the selected dates")

    # 3. Calculate price
    duration = booking.end_time - booking.start_time
    hours = duration.total_seconds() / 3600
    days = duration.days
    
    if days >= 1:
        total_price = days * equipment["daily_price"]
        remaining_hours = (duration.total_seconds() % 86400) / 3600
        total_price += remaining_hours * equipment["hourly_price"]
    else:
        total_price = hours * equipment["hourly_price"]

    # 4. Create booking
    booking_dict = booking.dict()
    booking_dict["renter_id"] = str(current_user.id)
    booking_dict["total_price"] = round(total_price, 2)
    booking_dict["status"] = BookingStatus.PENDING
    booking_dict["equipment_id"] = ObjectId(booking.equipment_id)
    
    new_booking = await db["bookings"].insert_one(booking_dict)
    created_booking = await db["bookings"].find_one({"_id": new_booking.inserted_id})
    
    return BookingDB(**created_booking)

@router.get("/user", response_model=List[BookingResponse])
async def get_user_bookings(current_user: UserDB = Depends(get_current_user)):
    db = get_db()
    bookings = await db["bookings"].find({"renter_id": str(current_user.id)}).to_list(length=100)
    return [BookingDB(**b) for b in bookings]

@router.patch("/status/{booking_id}", response_model=BookingResponse)
async def update_booking_status(booking_id: str, status: BookingStatus, current_user: UserDB = Depends(get_current_user)):
    db = get_db()
    booking = await db["bookings"].find_one({"_id": ObjectId(booking_id)})
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    # Only owner of equipment or the renter (for cancellation) can update status
    # In a real app complexity might be higher (e.g. only owner confirms)
    equipment = await db["equipment"].find_one({"_id": booking["equipment_id"]})
    
    is_owner = str(equipment["owner_id"]) == str(current_user.id)
    is_renter = str(booking["renter_id"]) == str(current_user.id)
    
    if not (is_owner or (is_renter and status == BookingStatus.CANCELLED)):
         raise HTTPException(status_code=403, detail="Not authorized to update this booking")

    await db["bookings"].update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {"status": status}}
    )
    
    updated_booking = await db["bookings"].find_one({"_id": ObjectId(booking_id)})
    return BookingDB(**updated_booking)

@router.post("/create-by-mobile", response_model=BookingResponse)
async def create_booking_by_mobile(booking: BookingCreateByMobile):
    db = get_db()
    
    # 0. Find User by Mobile
    user = await db["users"].find_one({"mobile_number": booking.mobile_number})
    
    if not user:
        # Auto-create user
        new_user = {
            "name": f"Guest {booking.mobile_number}",
            "mobile_number": booking.mobile_number,
            "role": UserRole.RENTER,
            "password_hash": "mock_hash_123456", # In a real app, use proper hashing
            "location": None
        }
        result = await db["users"].insert_one(new_user)
        user = await db["users"].find_one({"_id": result.inserted_id})
    
    current_user_id = user["_id"]
    
    # 1. Validate equipment exists
    equipment = await db["equipment"].find_one({"_id": ObjectId(booking.equipment_id)})
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    # 2. Check for conflicts
    conflict = await db["bookings"].find_one({
        "equipment_id": ObjectId(booking.equipment_id),
        "status": {"$in": ["pending", "confirmed"]},
        "$or": [
            {"start_time": {"$lte": booking.end_time}, "end_time": {"$gte": booking.start_time}}
        ]
    })
    
    if conflict:
        raise HTTPException(status_code=400, detail="Equipment is not available for the selected dates")

    # 3. Calculate price
    duration = booking.end_time - booking.start_time
    hours = duration.total_seconds() / 3600
    days = duration.days
    
    if days >= 1:
        total_price = days * equipment["daily_price"]
        remaining_hours = (duration.total_seconds() % 86400) / 3600
        total_price += remaining_hours * equipment["hourly_price"]
    else:
        total_price = hours * equipment["hourly_price"]

    # 4. Create booking
    booking_dict = booking.dict(exclude={"mobile_number"})
    booking_dict["renter_id"] = str(current_user_id)
    booking_dict["total_price"] = round(total_price, 2)
    booking_dict["status"] = BookingStatus.PENDING
    booking_dict["equipment_id"] = ObjectId(booking.equipment_id)
    
    # booking.dict() includes mobile_number but we don't want to store it in booking if we proceed with renter_id
    # However, 'exclude' in dict() might need explicit handling or just pop it.
    # The 'exclude' argument in Pydantic v1/v2 might vary slightly but usually works. 
    # Let's be safe and pop it if it exists in the dict, or rely on exclude.
    # Actually, BookingCreateByMobile inherits from BookingCreate.
    
    new_booking = await db["bookings"].insert_one(booking_dict)
    created_booking = await db["bookings"].find_one({"_id": new_booking.inserted_id})
    
    return BookingDB(**created_booking)

@router.get("/list-booked", response_model=List[BookingResponse])
async def list_booked_equipment():
    db = get_db()
    # List all bookings that are pending or confirmed
    bookings = await db["bookings"].find({
        "status": {"$in": ["pending", "confirmed"]}
    }).to_list(length=100)
    
    return [BookingDB(**b) for b in bookings]

@router.get("/incoming", response_model=List[BookingResponse])
async def get_incoming_bookings(mobile_number: str):
    db = get_db()
    
    # 1. Find user (owner)
    # Using 'mobile_number' field for guests/owners registered via mobile
    # or 'phone' if that was used. Let's assume mobile_number for consistency with equipment reg.
    # We check both to be safe or stick to one convention. 
    # In equipment reg we used 'mobile_number'.
    
    
    user = await db["users"].find_one({"mobile_number": mobile_number})
        
    if not user:
        return []

    # 2. Find all equipment owned by this user
    equipment_cursor = db["equipment"].find({"owner_id": str(user["_id"])})
    user_equipments = await equipment_cursor.to_list(length=100)
    
    if not user_equipments:
        return []
        
    equipment_ids = [eq["_id"] for eq in user_equipments]
    
    # 3. Find bookings for these equipment IDs
    bookings = await db["bookings"].find({
        "equipment_id": {"$in": equipment_ids}
    }).sort("created_at", -1).to_list(length=100)
    
    return [BookingDB(**b) for b in bookings]
