import razorpay
import os
import hmac
import hashlib
from typing import Dict, Optional
from pydantic import BaseModel
from fastapi import HTTPException
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Razorpay Configuration
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', 'rzp_test_your_key_id')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', 'your_key_secret')

# Verify credentials are loaded
if RAZORPAY_KEY_ID == 'rzp_test_your_key_id' or RAZORPAY_KEY_SECRET == 'your_key_secret':
    print("⚠️  WARNING: Using default Razorpay credentials. Please update your .env file.")

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Subscription Plans
SUBSCRIPTION_PLANS = {
    'lite': {
        'name': 'SPECTER Lite',
        'amount': 29900,  # ₹299 in paise
        'currency': 'INR',
        'description': '50 Questions, 25 Solutions, 3 Uploads',
        'duration_days': 30
    },
    'specter': {
        'name': 'SPECTER Pro',
        'amount': 49900,  # ₹499 in paise
        'currency': 'INR',
        'description': 'Unlimited Questions, Solutions & Uploads',
        'duration_days': 30
    }
}

# Pydantic Models
class PaymentRequest(BaseModel):
    plan: str
    user_id: str
    user_email: str
    user_name: str

class PaymentVerification(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    user_id: str

class SubscriptionStatus(BaseModel):
    user_id: str
    plan: str
    status: str
    expires_at: datetime
    payment_id: Optional[str] = None
    order_id: Optional[str] = None

def create_payment_order(plan: str, user_id: str, user_email: str, user_name: str) -> Dict:
    """
    Create a Razorpay order for subscription payment
    """
    if plan not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Invalid subscription plan")
    
    plan_details = SUBSCRIPTION_PLANS[plan]
    
    # Create order data
    # Receipt must be max 40 chars - use short hash of user_id + timestamp
    timestamp = int(datetime.now().timestamp())
    receipt_hash = hashlib.md5(f"{user_id}{timestamp}".encode()).hexdigest()[:8]
    
    order_data = {
        'amount': plan_details['amount'],
        'currency': plan_details['currency'],
        'receipt': f"{plan}_{receipt_hash}_{timestamp}",
        'notes': {
            'user_id': user_id,
            'plan': plan,
            'user_email': user_email,
            'user_name': user_name
        }
    }
    
    
    try:
        # Create order with Razorpay
        print(f"Creating Razorpay order with data: {order_data}")
        print(f"Using Key ID: {RAZORPAY_KEY_ID[:10]}...")
        order = razorpay_client.order.create(data=order_data)
        print(f"Order created successfully: {order['id']}")
        
        return {
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency'],
            'key_id': RAZORPAY_KEY_ID,
            'plan_name': plan_details['name'],
            'description': plan_details['description']
        }
    
    except Exception as e:
        print(f"Razorpay order creation failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create payment order: {str(e)}")

def verify_payment_signature(order_id: str, payment_id: str, signature: str) -> bool:
    """
    Verify Razorpay payment signature
    """
    try:
        # Create signature verification string
        message = f"{order_id}|{payment_id}"
        
        # Generate expected signature
        expected_signature = hmac.new(
            RAZORPAY_KEY_SECRET.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    except Exception as e:
        print(f"Signature verification error: {e}")
        return False

def get_payment_details(payment_id: str) -> Dict:
    """
    Fetch payment details from Razorpay
    """
    try:
        payment = razorpay_client.payment.fetch(payment_id)
        return payment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch payment details: {str(e)}")

def process_successful_payment(order_id: str, payment_id: str, user_id: str) -> SubscriptionStatus:
    """
    Process successful payment and update user subscription
    """
    try:
        # Fetch order details to get plan information
        order = razorpay_client.order.fetch(order_id)
        plan = order['notes']['plan']
        
        # Calculate expiry date
        plan_details = SUBSCRIPTION_PLANS[plan]
        expires_at = datetime.now() + timedelta(days=plan_details['duration_days'])
        
        # Create subscription status
        subscription = SubscriptionStatus(
            user_id=user_id,
            plan=plan,
            status='active',
            expires_at=expires_at,
            payment_id=payment_id,
            order_id=order_id
        )
        
        return subscription
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process payment: {str(e)}")

def get_subscription_limits(plan: str) -> Dict:
    """
    Get usage limits for a subscription plan
    """
    limits = {
        'free': {'questions': 3, 'solutions': 1, 'uploads': 1},
        'lite': {'questions': 50, 'solutions': 25, 'uploads': 3},
        'specter': {'questions': -1, 'solutions': -1, 'uploads': -1}  # -1 means unlimited
    }
    
    return limits.get(plan, limits['free'])

def is_subscription_active(subscription: SubscriptionStatus) -> bool:
    """
    Check if subscription is still active
    """
    return (
        subscription.status == 'active' and 
        subscription.expires_at > datetime.now()
    )