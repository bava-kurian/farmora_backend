import asyncio
import os
import base64
from database import connect_to_mongo, close_mongo_connection, get_db
from app.models.store import Product
from dotenv import load_dotenv

load_dotenv()

def get_base64_image(filename):
    """
    Reads an image file from the 'dummy' directory and returns a data URI.
    """
    filepath = os.path.join(os.path.dirname(__file__), "dummy", filename)
    if not os.path.exists(filepath):
        print(f"Warning: Image file not found: {filepath}")
        return ""
    
    with open(filepath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        
    mime_type = "image/jpeg" if filename.lower().endswith((".jpg", ".jpeg")) else "image/webp"
    return f"data:{mime_type};base64,{encoded_string}"


dummy_products = [
    {
        "name": "Organic Fertilizer 50kg",
        "category": "Fertilizers",
        "description": "High quality organic fertilizer rich in nitrogen. Improves soil structure and water retention.",
        "original_price": 1200.0,
        "our_price": 950.0,
        "seller": "Green Earth Co.",
        "image": "organic_fertilizer.webp", 
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
        "image": "DAP_fertilizer.webp",
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
        "image": "power_tiller_HP.webp",
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
        "image": "heavy duty_spade.jpg",
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
        "image": "knapsack_sprayer.webp",
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
        "image": "premium_wheat_seed.webp",
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
    
    # Process images
    products_to_insert = []
    for p in dummy_products:
        image_filename = p["image"]
        base64_image = get_base64_image(image_filename)
        if base64_image:
            p["image"] = base64_image
        else:
            # Fallback placeholder if local image fails
            p["image"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        products_to_insert.append(p)

    # Insert new products
    result = await db["products"].insert_many(products_to_insert)
    print(f"Inserted {len(result.inserted_ids)} products using local images.")
    
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(seed_products())
