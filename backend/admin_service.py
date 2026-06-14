"""
Admin Service — Platform analytics, popular queries, DAU tracking.
Provides admin-only endpoints for monitoring platform health and usage.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from mongodb_config import get_database

logger = logging.getLogger(__name__)


def _admin_db():
    return get_database()


async def get_platform_stats() -> Dict:
    db = _admin_db()
    total_users = await db.users.count_documents({})
    active_today = await db.user_sessions.count_documents({
        "updated_at": {"$gte": datetime.utcnow() - timedelta(days=1)}
    })
    active_week = await db.user_sessions.count_documents({
        "updated_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
    })
    total_chats = await db.chat_sessions.count_documents({})
    total_consultations = await db.consultations.count_documents({}) if "consultations" in await db.list_collection_names() else 0
    return {
        "total_users": total_users,
        "active_today": active_today,
        "active_week": active_week,
        "total_chat_sessions": total_chats,
        "total_consultations": total_consultations,
    }


async def get_popular_queries(limit: int = 20) -> List[Dict]:
    db = _admin_db()
    pipeline = [
        {"$match": {"messages.role": "user"}},
        {"$unwind": "$messages"},
        {"$match": {"messages.role": "user"}},
        {"$group": {"_id": "$messages.content", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
    ]
    results = []
    async for doc in db.chat_sessions.aggregate(pipeline):
        results.append({"query": doc["_id"][:200], "count": doc["count"]})
    return results


async def get_dau_stats(days: int = 30) -> List[Dict]:
    db = _admin_db()
    cutoff = datetime.utcnow() - timedelta(days=days)
    pipeline = [
        {"$match": {"updated_at": {"$gte": cutoff}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$updated_at"}},
            "active_users": {"$addToSet": "$user_id"},
        }},
        {"$sort": {"_id": 1}},
    ]
    results = []
    async for doc in db.chat_sessions.aggregate(pipeline):
        results.append({
            "date": doc["_id"],
            "dau": len(doc["active_users"]),
        })
    return results


async def get_subscription_stats() -> Dict:
    db = _admin_db()
    pipeline = [
        {"$group": {
            "_id": "$subscription.plan",
            "count": {"$sum": 1},
        }}
    ]
    plan_counts = {}
    async for doc in db.users.aggregate(pipeline):
        plan_counts[doc["_id"] or "free"] = doc["count"]
    return {
        "plans": plan_counts,
        "total_paid": sum(v for k, v in plan_counts.items() if k != "free"),
    }


async def get_revenue_stats() -> Dict:
    db = _admin_db()
    pipeline = [
        {"$match": {"subscription.status": "active"}},
        {"$group": {
            "_id": "$subscription.plan",
            "count": {"$sum": 1},
        }}
    ]
    plan_revenue_map = {"basic": 299, "pro": 999, "enterprise": 4999}
    total_monthly = 0
    breakdown = {}
    async for doc in db.users.aggregate(pipeline):
        plan = doc["_id"]
        count = doc["count"]
        price = plan_revenue_map.get(plan, 0)
        monthly = price * count
        breakdown[plan] = {"subscribers": count, "monthly_revenue": monthly}
        total_monthly += monthly
    return {"breakdown": breakdown, "total_monthly_revenue_mrr": total_monthly}
