import asyncio
from database import connect_to_mongo, get_db, close_mongo_connection
from bson import ObjectId
import sys
from dotenv import load_dotenv

load_dotenv()

async def list_posts():
    await connect_to_mongo()
    db = get_db()
    
    print("Listing all posts in 'community_posts':")
    try:
        cursor = db["community_posts"].find({})
        posts = await cursor.to_list(length=100)
        
        for p in posts:
            pid = p.get("_id")
            print(f"ID: {pid} (Type: {type(pid)}) - Title: {p.get('title')}")
            
            if isinstance(pid, ObjectId):
                print("SUCCESS: ID is ObjectId")
            else:
                print("FAILURE: ID is NOT ObjectId")
                
            # Check strictly if it matches the problematic ID if provided
            if str(pid) == "69962bb0365c43bf0e373d67":
                print(f"FOUND MATCH for 69962bb0365c43bf0e373d67!")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(list_posts())
