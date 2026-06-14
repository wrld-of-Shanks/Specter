"""
Lawyer Service — Lawyer profiles, search, and consultation booking.
Stores lawyer data in MongoDB and provides search/filter/booking operations.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bson import ObjectId
from mongodb_config import get_database

logger = logging.getLogger(__name__)

LAWYER_COLLECTION = "lawyers"
CONSULTATION_COLLECTION = "consultations"


def _lawyers():
    return get_database()[LAWYER_COLLECTION]


def _consultations():
    return get_database()[CONSULTATION_COLLECTION]


async def ensure_lawyer_indexes():
    col = _lawyers()
    await col.create_index("email", unique=True, sparse=True)
    await col.create_index([("specialization", 1)])
    await col.create_index([("city", 1)])
    await col.create_index([("experience_years", -1)])
    await col.create_index([("is_verified", 1)])
    con = _consultations()
    await con.create_index("lawyer_id")
    await con.create_index("user_id")
    await con.create_index("created_at")
    logger.info("Lawyer/consultation indexes created.")


async def add_lawyer_profile(profile: Dict) -> str:
    profile["created_at"] = datetime.utcnow()
    profile["updated_at"] = datetime.utcnow()
    profile["is_verified"] = profile.get("is_verified", False)
    profile["rating"] = profile.get("rating", 0.0)
    profile["total_reviews"] = profile.get("total_reviews", 0)
    profile["available"] = profile.get("available", True)
    result = await _lawyers().insert_one(profile)
    return str(result.inserted_id)


async def search_lawyers(
    query: str = "",
    specialization: str = "",
    city: str = "",
    min_experience: int = 0,
    max_fee: float = 0,
    skip: int = 0,
    limit: int = 20,
) -> List[Dict]:
    filters = {"is_verified": True, "available": True}
    if specialization:
        filters["specialization"] = {"$regex": specialization, "$options": "i"}
    if city:
        filters["city"] = {"$regex": city, "$options": "i"}
    if min_experience > 0:
        filters["experience_years"] = {"$gte": min_experience}
    if max_fee > 0:
        filters["consultation_fee"] = {"$lte": max_fee}
    if query:
        filters["$or"] = [
            {"name": {"$regex": query, "$options": "i"}},
            {"bio": {"$regex": query, "$options": "i"}},
            {"specialization": {"$regex": query, "$options": "i"}},
        ]
    cursor = _lawyers().find(filters).sort("rating", -1).skip(skip).limit(limit)
    results = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        results.append(doc)
    return results


async def get_lawyer_by_id(lawyer_id: str) -> Optional[Dict]:
    try:
        doc = await _lawyers().find_one({"_id": ObjectId(lawyer_id)})
        if doc:
            doc["id"] = str(doc.pop("_id"))
        return doc
    except Exception:
        return None


async def book_consultation(
    user_id: str,
    lawyer_id: str,
    preferred_date: str,
    preferred_time: str,
    notes: str = "",
) -> str:
    lawyer = await get_lawyer_by_id(lawyer_id)
    if not lawyer:
        raise ValueError("Lawyer not found")
    booking = {
        "user_id": user_id,
        "lawyer_id": lawyer_id,
        "lawyer_name": lawyer.get("name", ""),
        "preferred_date": preferred_date,
        "preferred_time": preferred_time,
        "notes": notes,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await _consultations().insert_one(booking)
    return str(result.inserted_id)


async def get_user_consultations(user_id: str) -> List[Dict]:
    cursor = _consultations().find({"user_id": user_id}).sort("created_at", -1)
    results = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        results.append(doc)
    return results


async def update_consultation_status(consultation_id: str, status: str) -> bool:
    result = await _consultations().update_one(
        {"_id": ObjectId(consulation_id)},
        {"$set": {"status": status, "updated_at": datetime.utcnow()}},
    )
    return result.modified_count > 0
