import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

logger = logging.getLogger("uvicorn.error")

class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None
    is_connected: bool = False

db_manager = Database()

async def connect_to_mongo():
    """Establishes connection to MongoDB Atlas / Local MongoDB instance."""
    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URI}...")
    try:
        db_manager.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000
        )
        # Verify connection
        await db_manager.client.admin.command('ping')
        db_manager.db = db_manager.client[settings.MONGODB_DB_NAME]
        db_manager.is_connected = True
        logger.info(f"Successfully connected to MongoDB Database: '{settings.MONGODB_DB_NAME}'")
    except Exception as e:
        db_manager.is_connected = False
        logger.warning(f"MongoDB connection failed: {e}. Running in standby / unseeded mode until database is connected.")

async def close_mongo_connection():
    """Closes MongoDB connection pool gracefully."""
    if db_manager.client is not None:
        logger.info("Closing MongoDB connection...")
        db_manager.client.close()
        db_manager.is_connected = False
        logger.info("MongoDB connection closed.")

def get_database() -> AsyncIOMotorDatabase:
    """Returns the current MongoDB database instance."""
    return db_manager.db

def get_collection(name: str):
    """Helper to return a specific collection."""
    if db_manager.db is not None:
        return db_manager.db[name]
    return None

# Canonical collection names
COLLECTIONS = {
    "users": "users",
    "departments": "departments",
    "leadership": "leadership",
    "faculty": "faculty",
    "venues": "venues",
    "rooms": "rooms",
    "resources": "resources",
    "events": "events",
    "event_requests": "event_requests",
    "approvals": "approvals",
    "guests": "guests",
    "clubs": "clubs",
    "tasks": "tasks",
    "conflicts": "conflicts",
    "notifications": "notifications",
    "audit_logs": "audit_logs",
}
