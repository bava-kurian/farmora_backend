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
    
    print("Preparing images...")
    import base64
    
    def get_image_as_base64(filename):
        try:
            path = os.path.join("dummy", filename)
            with open(path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:image/webp;base64,{encoded_string}"
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            return "https://example.com/placeholder.jpg"

    img_275 = get_image_as_base64("mahindra-275-di-tu.webp")
    img_555 = get_image_as_base64("mahindra-arjun-555-di.webp")
    img_475 = get_image_as_base64("mahindra-yuvo-475-di.webp")

    print("Creating dummy equipment...")
    equipment_list = [
        {
            "owner_id": str(owner_id),
            "equipment_type": "Tractor",
            "description": "Mahindra 275 DI TU, reliable and fuel efficient.",
            "hourly_price": 450.0,
            "daily_price": 3500.0,
            "availability_status": "available",
            "location": {"type": "Point", "coordinates": [76.2673, 9.9312]}, # Kochi
            "rating": 4.5,
            "review_count": 12,
            "images": [img_275]
        },
        {
            "owner_id": str(owner_id),
            "equipment_type": "Tractor",
            "description": "Mahindra Arjun 555 DI, high power for heavy usage.",
            "hourly_price": 600.0,
            "daily_price": 5000.0,
            "availability_status": "available",
            "location": {"type": "Point", "coordinates": [76.2800, 9.9400]}, # Nearby
            "rating": 4.7,
            "review_count": 8,
            "images": [img_555]
        },
        {
            "owner_id": str(owner_id),
            "equipment_type": "Tractor",
            "description": "Mahindra Yuvo 475 DI, advanced features and comfort.",
            "hourly_price": 550.0,
            "daily_price": 4200.0,
            "availability_status": "available",
            "location": {"type": "Point", "coordinates": [76.2900, 9.9350]}, # Nearby
            "rating": 4.6,
            "review_count": 15,
            "images": [img_475]
        }
    ]
    
    await db["equipment"].insert_many(equipment_list)
    print(f"Inserted {len(equipment_list)} tractors with images.")
    
    print("Dummy data seeded successfully!")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_data())
