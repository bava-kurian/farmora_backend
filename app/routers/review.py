from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
from app.models.user import UserDB
from app.models.review import ReviewCreate, ReviewResponse, ReviewDB
from database import get_db
from bson import ObjectId

router = APIRouter(prefix="/uber/review", tags=["Review"])

@router.post("/add", response_model=ReviewResponse)
async def add_review(review: ReviewCreate, current_user: UserDB = Depends(get_current_user)):
    db = get_db()
    
    # Check if booking exists and belongs to user
    booking = await db["bookings"].find_one({
        "_id": ObjectId(review.booking_id),
        "renter_id": str(current_user.id),
        "status": "completed"
    })
    
    if not booking:
        raise HTTPException(status_code=400, detail="Booking not found or not completed")
    
    # Create review
    review_dict = review.dict()
    review_dict["reviewer_id"] = str(current_user.id)
    review_dict["booking_id"] = ObjectId(review.booking_id)
    review_dict["equipment_id"] = booking["equipment_id"]
    
    new_review = await db["reviews"].insert_one(review_dict)
    
    # Update equipment rating
    equipment_id = booking["equipment_id"]
    
    # Aggregation pipeline to calculate new average
    pipeline = [
        {"$match": {"equipment_id": equipment_id}},
        {"$group": {"_id": "$equipment_id", "average_rating": {"$avg": "$rating"}, "count": {"$sum": 1}}}
    ]
    
    result = await db["reviews"].aggregate(pipeline).to_list(length=1)
    
    if result:
        avg_rating = result[0]["average_rating"]
        count = result[0]["count"]
        
        await db["equipment"].update_one(
            {"_id": equipment_id},
            {"$set": {"rating": avg_rating, "review_count": count}}
        )

    created_review = await db["reviews"].find_one({"_id": new_review.inserted_id})
    return ReviewDB(**created_review)
