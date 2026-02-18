import asyncio
from database import connect_to_mongo, get_db, close_mongo_connection
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

async def cleanup_posts():
    await connect_to_mongo()
    db = get_db()
    
    print("Cleaning up posts with String IDs...")
    try:
        # Find posts where _id is a string type (type 2)
        # Type 2 is string, Type 7 is ObjectId in Mongo
        result = await db["community_posts"].delete_many({"_id": {"$type": "string"}})
        print(f"Deleted {result.deleted_count} posts with String IDs.")
        
        # Also clean up related comments/votes if needed, but for now just posts
        # (Comments might also have string IDs if they used PyObjectId)
        result_comments = await db["community_comments"].delete_many({"_id": {"$type": "string"}})
        print(f"Deleted {result_comments.deleted_count} comments with String IDs.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(cleanup_posts())
