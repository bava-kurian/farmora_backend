import asyncio
import os
from database import connect_to_mongo, close_mongo_connection, get_db
from app.models.store import Product
from dotenv import load_dotenv

load_dotenv()

# Using reliable public image URLs (Wikipedia/Commons or detailed stock previews that work)
# If these fail, we can switch to a placeholder service like 'https://placehold.co/600x400?text=Product'

dummy_products = [
    {
        "name": "Organic Fertilizer 50kg",
        "category": "Fertilizers",
        "description": "High quality organic fertilizer rich in nitrogen. Improves soil structure and water retention.",
        "original_price": 1200.0,
        "our_price": 950.0,
        "seller": "Green Earth Co.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/DAP_Fertilizer.jpg/640px-DAP_Fertilizer.jpg", # Using generic fertilizer image
        "stock": 50,
        "rating": 4.5
    },
    {
        "name": "DAP Fertilizer",
        "category": "Fertilizers",
        "description": "Di-ammonium Phosphate fertilizer for root development. Essential for initial growth stages.",
        "original_price": 1500.0,
        "our_price": 1350.0,
        "seller": "AgriBest",
        "image": "https://5.imimg.com/data5/SELLER/Default/2023/1/YI/QZ/OY/3906323/dap-fertilizer.jpg", # Sourced from common industry images
        "stock": 100,
        "rating": 4.2
    },
    {
        "name": "Power Tiller 7HP",
        "category": "Machines",
        "description": "7HP Power Tiller for small farms. reliable engine, easy maneuverability.",
        "original_price": 45000.0,
        "our_price": 42000.0,
        "seller": "FarmMachinery Ltd.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Power_tiller_in_use.jpg/640px-Power_tiller_in_use.jpg",
        "stock": 5,
        "rating": 4.8
    },
    {
        "name": "Heavy Duty Spade",
        "category": "Tools",
        "description": "Heave duty iron spade with wooden handle. Perfect for digging and trenching.",
        "original_price": 350.0,
        "our_price": 280.0,
        "seller": "Local Tools",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Spade.jpg/367px-Spade.jpg",
        "stock": 200,
        "rating": 4.0
    },
    {
        "name": "Knapsack Sprayer 16L",
        "category": "Tools",
        "description": "Manual knapsack sprayer for pesticides. Comfortable straps and durable tank.",
        "original_price": 1800.0,
        "our_price": 1500.0,
        "seller": "AgriSpray",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Knapsack_sprayer.jpg/640px-Knapsack_sprayer.jpg",
        "stock": 30,
        "rating": 4.3
    },
     {
        "name": "Premium Wheat Seeds 10kg",
        "category": "Seeds",
        "description": "High yield wheat seeds treated for disease resistance. Certified organic.",
        "original_price": 800.0,
        "our_price": 720.0,
        "seller": "SeedCorp",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Vehn%C3%A4n_jyvi%C3%A4_-_Wheat_grains.jpg/640px-Vehn%C3%A4n_jyvi%C3%A4_-_Wheat_grains.jpg",
        "stock": 80,
        "rating": 4.6
    }
]

async def seed_products():
    await connect_to_mongo()
    db = get_db()
    
    # Clear existing products
    await db["products"].delete_many({})
    print("Cleared existing products.")
    
    # Insert new products
    result = await db["products"].insert_many(dummy_products)
    print(f"Inserted {len(result.inserted_ids)} products.")
    
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(seed_products())
