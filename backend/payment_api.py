from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

try:
    from .auth_mongo import get_current_user
    from .payment_razorpay import (
        create_payment_order, 
        verify_payment_signature, 
        process_successful_payment,
        SUBSCRIPTION_PLANS
    )
    from .mongodb_config import get_users_collection
except ImportError:
    from auth_mongo import get_current_user
    from payment_razorpay import (
        create_payment_order, 
        verify_payment_signature, 
        process_successful_payment,
        SUBSCRIPTION_PLANS
    )
    from mongodb_config import get_users_collection

payment_router = APIRouter()

class OrderRequest(BaseModel):
    plan: str

class PaymentVerificationRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

@payment_router.get("/plans")
async def get_plans():
    """Get available subscription plans"""
    return SUBSCRIPTION_PLANS

@payment_router.post("/create-order")
async def create_order(request: OrderRequest, current_user: dict = Depends(get_current_user)):
    """Create a payment order"""
    try:
        user_id = str(current_user["_id"])
        user_email = current_user["email"]
        user_name = current_user["full_name"]
        
        order_details = create_payment_order(
            plan=request.plan,
            user_id=user_id,
            user_email=user_email,
            user_name=user_name
        )
        return order_details
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error creating order: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@payment_router.post("/verify")
async def verify_payment(request: PaymentVerificationRequest, current_user: dict = Depends(get_current_user)):
    """Verify payment and update subscription"""
    try:
        is_valid = verify_payment_signature(
            order_id=request.razorpay_order_id,
            payment_id=request.razorpay_payment_id,
            signature=request.razorpay_signature
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid payment signature")
        
        # Process payment and get subscription details
        user_id = str(current_user["_id"])
        subscription = process_successful_payment(
            order_id=request.razorpay_order_id,
            payment_id=request.razorpay_payment_id,
            user_id=user_id
        )
        
        # Update user in database
        users_collection = get_users_collection()
        await users_collection.update_one(
            {"_id": current_user["_id"]},
            {
                "$set": {
                    "subscription": {
                        "plan": subscription.plan,
                        "status": subscription.status,
                        "expires_at": subscription.expires_at,
                        "payment_id": subscription.payment_id,
                        "order_id": subscription.order_id,
                        "updated_at": datetime.utcnow()
                    }
                }
            }
        )
        
        return {"status": "success", "message": "Subscription activated successfully", "subscription": subscription}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
