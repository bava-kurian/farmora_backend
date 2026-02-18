from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from database import connect_to_mongo, close_mongo_connection

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    
    # Create geospatial index
    db = get_db()
    try:
        await db["equipment"].create_index([("location", "2dsphere")])
        print("Created 2dsphere index on equipment.location")
    except Exception as e:
        print(f"Error creating index: {e}")
        
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}
