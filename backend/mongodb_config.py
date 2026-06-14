import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import asyncio
from typing import Optional

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URI") or os.getenv("MONGODB_URL") or os.getenv("MONGO_URL") or "mongodb://localhost:27017"
DATABASE_NAME = os.getenv("DATABASE_NAME", "specter_legal")

# Global variables for database connections
mongo_client: Optional[AsyncIOMotorClient] = None
database = None

async def connect_to_mongo():
    """Create database connection"""
    global mongo_client, database
    mongo_client = AsyncIOMotorClient(MONGODB_URL)
    database = mongo_client[DATABASE_NAME]
    print(f"Connected to MongoDB: {DATABASE_NAME}")

async def close_mongo_connection():
    """Close database connection"""
    global mongo_client
    if mongo_client:
        mongo_client.close()
        print("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return database

# Collections
def get_users_collection():
    """Get users collection"""
    return database.users

def get_legal_acts_collection():
    """Get legal acts collection"""
    return database.legal_acts

def get_user_sessions_collection():
    """Get user sessions collection"""
    return database.user_sessions

def get_otps_collection():
    """Get OTPs collection"""
    return database.otps

# Initialize collections with indexes
async def create_indexes():
    """Create necessary indexes for better performance"""
    users_collection = get_users_collection()
    legal_acts_collection = get_legal_acts_collection()
    sessions_collection = get_user_sessions_collection()
    otps_collection = get_otps_collection()
    
    # Users collection indexes
    await users_collection.create_index("email", unique=True)
    await users_collection.create_index("created_at")
    
    # Legal acts collection indexes
    await legal_acts_collection.create_index("act")
    await legal_acts_collection.create_index("section")
    await legal_acts_collection.create_index([("title", "text"), ("definition", "text"), ("keywords", "text")])
    
    # Sessions collection indexes
    await sessions_collection.create_index("user_id")
    await sessions_collection.create_index("expires_at")
    
    # OTPs collection indexes
    await otps_collection.create_index("email")
    await otps_collection.create_index("expires_at")
    
    print("Database indexes created successfully")

# Sync version for non-async operations
def get_sync_database():
    """Get synchronous database connection for non-async operations"""
    sync_client = MongoClient(MONGODB_URL)
    return sync_client[DATABASE_NAME]
