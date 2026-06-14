from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
import os
import random
import string
import smtplib
from email.mime.text import MIMEText
import logging

logger = logging.getLogger(__name__)

try:
    from .mongodb_config import get_users_collection, get_otps_collection, get_user_sessions_collection
    from .tracing import TraceEvents, log_auth_event
except ImportError:
    from mongodb_config import get_users_collection, get_otps_collection, get_user_sessions_collection
    from tracing import TraceEvents, log_auth_event

from dotenv import load_dotenv
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

# Load environment variables
load_dotenv()

# Password hashing context - using bcrypt for compatibility
pwd_context = CryptContext(schemes=["bcrypt", "pbkdf2_sha256"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "your-secret-key-here"))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 10080  # 7 days

# Email Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

# Security
security = HTTPBearer()

# Pydantic Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

# Helper Functions
def verify_password(plain_password, hashed_password):
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Generate password hash"""
    return pwd_context.hash(password)

def generate_otp(length=6):
    """Generate a random OTP"""
    return ''.join(random.choices(string.digits, k=length))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access"):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if token_type == "refresh" and payload.get("type") != "refresh":
            logger.warning("Token type mismatch: expected refresh token")
            return None
        return payload
    except JWTError as e:
        logger.error(f"JWT Verification failed: {e}. Key used starts with: {SECRET_KEY[:4]}...")
        return None

# Database Functions
async def get_user_by_email(email: str):
    """Get user by email"""
    users_collection = get_users_collection()
    return await users_collection.find_one({"email": email})

async def create_user(email: str, password: str, full_name: str):
    """Create a new user"""
    users_collection = get_users_collection()
    user_doc = {
        "email": email,
        "password_hash": get_password_hash(password),
        "full_name": full_name,
        "is_verified": False,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "usage": {
            "questions_asked": 0,
            "documents_uploaded": 0,
            "last_reset": datetime.utcnow()
        }
    }
    result = await users_collection.insert_one(user_doc)
    return str(result.inserted_id)

async def store_otp(email: str, otp: str, otp_type: str):
    """Store OTP in database"""
    otps_collection = get_otps_collection()
    otp_doc = {
        "email": email,
        "otp": otp,
        "type": otp_type,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(minutes=10)
    }
    await otps_collection.insert_one(otp_doc)

async def verify_otp(email: str, otp: str, otp_type: str):
    """Verify OTP"""
    otps_collection = get_otps_collection()
    otp_doc = await otps_collection.find_one({
        "email": email,
        "otp": otp,
        "type": otp_type,
        "expires_at": {"$gt": datetime.utcnow()}
    })
    if otp_doc:
        # Delete the OTP after verification
        await otps_collection.delete_one({"_id": otp_doc["_id"]})
        return True
    return False

async def update_user_verification(email: str):
    """Update user verification status"""
    users_collection = get_users_collection()
    await users_collection.update_one(
        {"email": email},
        {"$set": {"is_verified": True, "updated_at": datetime.utcnow()}}
    )

async def update_user_password(email: str, new_password: str):
    """Update user password"""
    users_collection = get_users_collection()
    await users_collection.update_one(
        {"email": email},
        {"$set": {"password_hash": get_password_hash(new_password), "updated_at": datetime.utcnow()}}
    )

async def invalidate_user_sessions(user_id: str):
    """Invalidate all user sessions"""
    sessions_collection = get_user_sessions_collection()
    await sessions_collection.delete_many({"user_id": user_id})

# Email Functions
def send_otp_email(email: str, otp: str, purpose: str):
    """Send OTP email"""
    if not SMTP_USER or not SMTP_PASS:
        # For development, return the OTP
        return {"sent": False, "otp": otp}
    
    subject = f"SPECTER Legal - {purpose.replace('_', ' ').title()}"
    body = f"Your OTP code is: {otp}\n\nThis code will expire in 10 minutes."
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = email
    
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, email, msg.as_string())
        return {"sent": True}
    except Exception as e:
        print(f"Failed to send email: {e}")
        return {"sent": False, "otp": otp}

# Dependencies
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    email = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Router
auth_router = APIRouter()

# Endpoints
@auth_router.post("/register", response_model=dict)
async def register(user_data: UserRegister):
    """Register a new user"""
    # Check if user already exists
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        # Create user
        user_id = await create_user(user_data.email, user_data.password, user_data.full_name)
        
        # Generate and send OTP for email verification
        otp = generate_otp()
        await store_otp(user_data.email, otp, "email_verification")
        
        # Send OTP email
        email_result = send_otp_email(user_data.email, otp, "email_verification")
        
        if email_result["sent"]:
            return {"message": "Registration successful. Please check your email for verification code."}
        else:
            # For development, show the OTP
            return {"message": f"Registration successful. For development, use OTP: {email_result['otp']}"}
            
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except Exception as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )

@auth_router.post("/verify-email", response_model=dict)
async def verify_email(otp_data: OTPVerify):
    """Verify email with OTP"""
    if await verify_otp(otp_data.email, otp_data.otp, "email_verification"):
        await update_user_verification(otp_data.email)
        return {"message": "Email verified successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

@auth_router.post("/login")
async def login(user_data: UserLogin):
    """User login"""
    user = await get_user_by_email(user_data.email)
    
    if not user or not verify_password(user_data.password, user["password_hash"]):
        await log_auth_event(TraceEvents.AUTH_LOGIN, user_data.email, False, {"reason": "invalid_credentials"})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.get("is_verified", False):
        await log_auth_event(TraceEvents.AUTH_LOGIN, user_data.email, False, {"reason": "email_not_verified"})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please verify your email first"
        )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": user["email"]})
    refresh_token = create_refresh_token(data={"sub": user["email"]})
    
    # Log successful login
    await log_auth_event(TraceEvents.AUTH_LOGIN, user_data.email, True, {
        "user_id": str(user["_id"]),
        "login_time": datetime.utcnow().isoformat()
    })
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "_id": str(user["_id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "is_verified": user.get("is_verified", False),
            "subscription": user.get("subscription", {}),
            "usage": user.get("usage", {})
        }
    }

@auth_router.post("/refresh-token", response_model=Token)
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    payload = verify_token(refresh_token, "refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user = await get_user_by_email(payload.get("sub"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(data={"sub": user["email"]})
    
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@auth_router.post("/forgot-password", response_model=dict)
async def forgot_password(request: PasswordReset):
    """Send password reset OTP"""
    user = await get_user_by_email(request.email)
    if not user:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a reset code has been sent."}
    
    # Generate and send OTP
    otp = generate_otp()
    await store_otp(request.email, otp, "password_reset")
    
    # Send OTP email
    email_result = send_otp_email(request.email, otp, "password_reset")
    
    if email_result["sent"]:
        return {"message": "If the email exists, a reset code has been sent."}
    else:
        # For development, show the OTP
        return {"message": f"Email not configured. For development, use OTP: {email_result['otp']}"}

@auth_router.post("/reset-password", response_model=dict)
async def reset_password(request: PasswordResetConfirm):
    """Reset password with OTP"""
    try:
        if await verify_otp(request.email, request.otp, "password_reset"):
            # Update password
            await update_user_password(request.email, request.new_password)
            
            # Invalidate all sessions for this user
            user = await get_user_by_email(request.email)
            if user:
                await invalidate_user_sessions(str(user["_id"]))
            
            return {"message": "Password reset successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Password reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed. Please try again."
        )

@auth_router.post("/logout", response_model=dict)
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout user"""
    # Invalidate all sessions for this user
    await invalidate_user_sessions(str(current_user["_id"]))
    return {"message": "Logged out successfully"}

@auth_router.get("/profile", response_model=dict)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile"""
    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "is_verified": current_user.get("is_verified", False),
        "is_active": current_user.get("is_active", True),
        "created_at": current_user["created_at"].isoformat()
    }

@auth_router.put("/profile", response_model=dict)
async def update_profile(
    full_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    users_collection = get_users_collection()
    await users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"full_name": full_name, "updated_at": datetime.utcnow()}}
    )
    return {"message": "Profile updated successfully"}

# Development helper endpoint
@auth_router.get("/dev/get-otp/{email}")
async def get_otp_for_development(email: str):
    """Development endpoint to get the latest OTP for an email"""
    otps_collection = get_otps_collection()
    otp_doc = await otps_collection.find_one(
        {"email": email, "expires_at": {"$gt": datetime.utcnow()}},
        sort=[("created_at", -1)]
    )
    
    if otp_doc:
        return {
            "email": email,
            "otp": otp_doc["otp"],
            "type": otp_doc["type"],
            "expires_at": otp_doc["expires_at"].isoformat()
        }
    else:
        return {"message": "No valid OTP found for this email"}
