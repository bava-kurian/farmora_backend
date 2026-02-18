from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from database import connect_to_mongo, close_mongo_connection

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}
