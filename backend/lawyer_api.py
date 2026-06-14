"""
Lawyer Marketplace API — Search, profile, and consultation booking.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from lawyer_service import (
    search_lawyers,
    get_lawyer_by_id,
    book_consultation,
    get_user_consultations,
    add_lawyer_profile,
)
import logging

logger = logging.getLogger(__name__)
lawyer_router = APIRouter()


class LawyerProfileRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    specialization: str
    city: str
    experience_years: int
    consultation_fee: float
    bio: str
    languages: list[str] = []


class ConsultationBookRequest(BaseModel):
    lawyer_id: str
    preferred_date: str
    preferred_time: str
    notes: str = ""


@lawyer_router.get("/lawyers/search")
async def search_lawyers_endpoint(
    q: str = Query("", description="Search query"),
    specialization: str = Query("", description="Filter by specialization"),
    city: str = Query("", description="Filter by city"),
    min_experience: int = Query(0, description="Minimum years of experience"),
    max_fee: float = Query(0, description="Maximum consultation fee"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    results = await search_lawyers(
        query=q,
        specialization=specialization,
        city=city,
        min_experience=min_experience,
        max_fee=max_fee,
        skip=skip,
        limit=limit,
    )
    return {"lawyers": results, "count": len(results)}


@lawyer_router.get("/lawyers/{lawyer_id}")
async def get_lawyer_endpoint(lawyer_id: str):
    lawyer = await get_lawyer_by_id(lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    return lawyer


@lawyer_router.post("/lawyers/register")
async def register_lawyer(request: LawyerProfileRequest):
    try:
        profile = request.dict()
        lawyer_id = await add_lawyer_profile(profile)
        return {"success": True, "lawyer_id": lawyer_id}
    except Exception as e:
        logger.error(f"Lawyer registration failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to register lawyer profile")


@lawyer_router.post("/consultations/book")
async def book_consultation_endpoint(
    request: ConsultationBookRequest,
    req: Request,
):
    from auth_mongo import get_current_user
    from fastapi.security import HTTPAuthorizationCredentials

    auth_header = req.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    token = auth_header.replace("Bearer ", "")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    user = await get_current_user(credentials)
    user_id = str(user["_id"])

    try:
        booking_id = await book_consultation(
            user_id=user_id,
            lawyer_id=request.lawyer_id,
            preferred_date=request.preferred_date,
            preferred_time=request.preferred_time,
            notes=request.notes,
        )
        return {"success": True, "booking_id": booking_id, "status": "pending"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Booking failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to book consultation")


@lawyer_router.get("/consultations/my")
async def my_consultations(req: Request):
    from auth_mongo import get_current_user
    from fastapi.security import HTTPAuthorizationCredentials

    auth_header = req.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    token = auth_header.replace("Bearer ", "")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    user = await get_current_user(credentials)
    user_id = str(user["_id"])

    consultations = await get_user_consultations(user_id)
    return {"consultations": consultations, "count": len(consultations)}
