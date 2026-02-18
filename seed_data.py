import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from app.models.user import UserRole

load_dotenv()

async def seed_data():
    mongo_url = os.getenv("MONGODB_URL")
    db_name = os.getenv("DB_NAME")
    
    if not mongo_url or not db_name:
        print("Error: MONGODB_URL or DB_NAME not set.")
        return

    print(f"Connecting to {db_name}...")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    # clear existing data (optional, maybe safe to keep adding?)
    # await db["users"].delete_many({})
    # await db["equipment"].delete_many({})
    # await db["bookings"].delete_many({})
    
    print("Creating dummy users...")
    owner = {
        "name": "Ramesh Farmer",
        "phone": "9876543210",
        "role": UserRole.OWNER,
        "password_hash": "dummy_hash",
        "location": {"type": "Point", "coordinates": [76.2673, 9.9312]} # Kochi
    }
    
    renter = {
        "name": "Suresh Renter",
        "phone": "9123456780",
        "role": UserRole.RENTER,
        "password_hash": "dummy_hash",
        "location": {"type": "Point", "coordinates": [76.2700, 9.9350]}
    }
    
    owner_result = await db["users"].insert_one(owner)
    owner_id = owner_result.inserted_id
    
    await db["users"].insert_one(renter)
    
    print("Creating dummy equipment...")
    equipment_list = [
        {
            "owner_id": str(owner_id),
            "equipment_type": "Tractor",
            "description": "Mahindra 575 DI, good condition, 45HP",
            "hourly_price": 500.0,
            "daily_price": 4000.0,
            "availability_status": "available",
            "location": {"type": "Point", "coordinates": [76.2673, 9.9312]}, # Kochi
            "rating": 4.5,
            "review_count": 10,
            "images": ["https://example.com/tractor1.jpg"]
        },
        {
            "owner_id": str(owner_id),
            "equipment_type": "Harvester",
            "description": "Combine Harvester, efficient for paddy",
            "hourly_price": 1200.0,
            "daily_price": 10000.0,
            "availability_status": "available",
            "location": {"type": "Point", "coordinates": [76.3000, 9.9500]}, # Nearby
            "rating": 4.8,
            "review_count": 5,
            "images": ["https://example.com/harvester1.jpg"]
        }
    ]
    
    await db["equipment"].insert_many(equipment_list)
    
    print("Dummy data seeded successfully!")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_data())
