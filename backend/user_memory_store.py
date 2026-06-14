"""
Specter 2.0 — Per-user conversation memory stored in MongoDB.
Each user has one active session. Sessions auto-expire after SESSION_TTL_HOURS.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bson import ObjectId

from mongodb_config import get_database

logger = logging.getLogger(__name__)

COLLECTION_NAME = "chat_sessions"
SESSION_TTL_HOURS = 24
MAX_HISTORY_MESSAGES = 20


def _sessions():
    return get_database()[COLLECTION_NAME]


async def ensure_indexes():
    col = _sessions()
    await col.create_index("user_id")
    await col.create_index("updated_at", expireAfterSeconds=SESSION_TTL_HOURS * 3600)
    logger.info("chat_sessions indexes created.")


async def get_chat_history(user_id: str) -> List[Dict]:
    doc = await _sessions().find_one({"user_id": user_id})
    if not doc:
        return []
    return doc.get("messages", [])[-MAX_HISTORY_MESSAGES:]


async def append_message(user_id: str, role: str, content: str) -> bool:
    if role not in ("user", "assistant"):
        raise ValueError(f"Invalid role: {role}")

    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow().isoformat()
    }

    result = await _sessions().update_one(
        {"user_id": user_id},
        {
            "$push": {
                "messages": {
                    "$each": [message],
                    "$slice": -MAX_HISTORY_MESSAGES
                }
            },
            "$set": {"updated_at": datetime.utcnow()},
            "$setOnInsert": {
                "user_id": user_id,
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    return result.acknowledged


async def clear_history(user_id: str) -> bool:
    result = await _sessions().update_one(
        {"user_id": user_id},
        {"$set": {"messages": [], "updated_at": datetime.utcnow()}}
    )
    return result.acknowledged


def append_user_memory(user_id: str, memory: str):
    logger.warning("append_user_memory() is deprecated. Use append_message() in an async context.")
    return True
