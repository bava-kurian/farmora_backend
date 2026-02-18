from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.auth import get_current_user
from app.models.user import UserDB
from app.models.booking import BookingCreate, BookingResponse, BookingDB, BookingStatus
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
