from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from database import connect_to_mongo, close_mongo_connection, get_db
from app.routers import harvest, equipment, booking, review, auth, community, store

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
        # Community Indexes
        await db["community_posts"].create_index("created_at")
        await db["community_posts"].create_index([("upvotes", -1), ("created_at", -1)])
        await db["community_comments"].create_index("post_id")
        await db["community_comments"].create_index("created_at")
        
        await db["post_votes"].create_index([("user_id", 1), ("post_id", 1)], unique=True)
        await db["comment_votes"].create_index([("user_id", 1), ("comment_id", 1)], unique=True)
        
        print("Created community indexes")
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
app.include_router(community.router)
app.include_router(store.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
