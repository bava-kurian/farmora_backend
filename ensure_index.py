from pymongo import MongoClient
import os

from dotenv import load_dotenv

load_dotenv()

# Use the correct URI from the backend .env
MONGO_URI = os.getenv("MONGODB_URL", "mongodb+srv://bavakurian3_db_user:uXgQ41bpSdfninqO@cluster0.tcsl1x0.mongodb.net/")
DB_NAME = os.getenv("DB_NAME", "Farmora-Uber")

def ensure_index():
    print(f"Connecting to MongoDB: {MONGO_URI}")
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db["equipment"]
    
    # Create 2dsphere index on 'location' field
    # 2dsphere is required for $near queries
    try:
        index_name = collection.create_index([("location", "2dsphere")])
        print(f"Index created successfully: {index_name}")
    except Exception as e:
        print(f"Error creating index: {e}")

if __name__ == "__main__":
    ensure_index()
