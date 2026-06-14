"""
Usage tracking service for subscription limits enforcement
"""
from datetime import datetime
from typing import Dict, Optional
from fastapi import HTTPException, status

try:
    from .mongodb_config import get_users_collection
    from .payment_razorpay import get_subscription_limits
except ImportError:
    from mongodb_config import get_users_collection
    from payment_razorpay import get_subscription_limits


async def initialize_user_usage(user_id: str):
    """Initialize usage tracking for a user"""
    users_collection = get_users_collection()
    await users_collection.update_one(
        {"_id": user_id},
        {
            "$set": {
                "usage": {
                    "questions_asked": 0,
                    "documents_uploaded": 0,
                    "last_reset": datetime.utcnow()
                }
            }
        }
    )


async def get_user_usage(user: Dict) -> Dict:
    """Get current usage for a user"""
    usage = user.get("usage", {
        "questions_asked": 0,
        "documents_uploaded": 0,
        "last_reset": datetime.utcnow()
    })
    return usage


async def get_user_limits(user: Dict) -> Dict:
    """Get usage limits based on user's subscription plan"""
    subscription = user.get("subscription", {})
    plan = subscription.get("plan", "free")
    status_val = subscription.get("status", "inactive")
    
    # If subscription is not active, use free plan
    if status_val != "active":
        plan = "free"
    
    return get_subscription_limits(plan)


async def check_question_limit(user: Dict) -> bool:
    """Check if user can ask another question"""
    usage = await get_user_usage(user)
    limits = await get_user_limits(user)
    
    questions_limit = limits.get("questions", 0)
    questions_asked = usage.get("questions_asked", 0)
    
    # -1 means unlimited
    if questions_limit == -1:
        return True
    
    return questions_asked < questions_limit


async def check_upload_limit(user: Dict) -> bool:
    """Check if user can upload another document"""
    usage = await get_user_usage(user)
    limits = await get_user_limits(user)
    
    uploads_limit = limits.get("uploads", 0)
    documents_uploaded = usage.get("documents_uploaded", 0)
    
    # -1 means unlimited
    if uploads_limit == -1:
        return True
    
    return documents_uploaded < uploads_limit


async def increment_question_count(user_id: str):
    """Increment the question count for a user"""
    users_collection = get_users_collection()
    await users_collection.update_one(
        {"_id": user_id},
        {
            "$inc": {"usage.questions_asked": 1},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )


async def increment_upload_count(user_id: str):
    """Increment the document upload count for a user"""
    users_collection = get_users_collection()
    await users_collection.update_one(
        {"_id": user_id},
        {
            "$inc": {"usage.documents_uploaded": 1},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )


async def get_usage_stats(user: Dict) -> Dict:
    """Get usage statistics with limits for frontend display"""
    usage = await get_user_usage(user)
    limits = await get_user_limits(user)
    
    return {
        "questions": {
            "used": usage.get("questions_asked", 0),
            "limit": limits.get("questions", 0),
            "remaining": limits.get("questions", 0) - usage.get("questions_asked", 0) if limits.get("questions", 0) != -1 else -1
        },
        "uploads": {
            "used": usage.get("documents_uploaded", 0),
            "limit": limits.get("uploads", 0),
            "remaining": limits.get("uploads", 0) - usage.get("documents_uploaded", 0) if limits.get("uploads", 0) != -1 else -1
        }
    }


async def enforce_question_limit(user: Dict):
    """Enforce question limit - raise exception if limit exceeded"""
    can_ask = await check_question_limit(user)
    if not can_ask:
        limits = await get_user_limits(user)
        usage = await get_user_usage(user)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Question limit reached ({usage.get('questions_asked', 0)}/{limits.get('questions', 0)}). Please upgrade your subscription."
        )


async def enforce_upload_limit(user: Dict):
    """Enforce upload limit - raise exception if limit exceeded"""
    can_upload = await check_upload_limit(user)
    if not can_upload:
        limits = await get_user_limits(user)
        usage = await get_user_usage(user)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Upload limit reached ({usage.get('documents_uploaded', 0)}/{limits.get('uploads', 0)}). Please upgrade your subscription."
        )
