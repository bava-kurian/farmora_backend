from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from database import connect_to_mongo, close_mongo_connection, get_db
from app.routers import harvest, equipment, booking, review, auth

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
        
        # Create unique index for users phone
        await db["users"].create_index("mobile_number", unique=True)
        print("Created unique index on users.mobile_number")
    except Exception as e:
        print(f"Error creating index: {e}")
        
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

app.include_router(harvest.router)
app.include_router(equipment.router)
app.include_router(booking.router)
app.include_router(review.router)
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
