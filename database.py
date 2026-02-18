from motor.motor_asyncio import AsyncIOMotorClient
import os

client = None
db = None

async def connect_to_mongo():
    global client, db
    mongo_url = os.getenv("MONGODB_URL")
    db_name = os.getenv("DB_NAME")
    if not mongo_url or not db_name:
        print("MONGODB_URL or DB_NAME not set in .env")
        return

    try:
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        # Ping the database to check connection
        await client.admin.command('ping')
        print(f"Connected to MongoDB: {db_name}")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("MongoDB connection closed")

def get_db():
    return db
