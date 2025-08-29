from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
import structlog

from app.core.pocketbase import pb_client

logger = structlog.get_logger()
router = APIRouter()

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    password_confirm: str
    role: str = "athlete"  # athlete, brand, agent
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    token: str
    user: Dict
    expires_in: int

@router.post("/register", response_model=TokenResponse)
async def register_user(user_data: UserRegister):
    """Register a new user account"""
    try:
        if user_data.password != user_data.password_confirm:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        # Create user in PocketBase
        user_record = pb_client.create_user(
            email=user_data.email,
            password=user_data.password,
            role=user_data.role,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        
        if not user_record:
            raise HTTPException(status_code=400, detail="Failed to create user account")
        
        # Authenticate the new user to get token
        auth_result = pb_client.authenticate_user(user_data.email, user_data.password)
        
        if not auth_result:
            raise HTTPException(status_code=400, detail="Failed to authenticate new user")
        
        logger.info("User registered successfully", user_id=user_record["id"], email=user_data.email)
        
        return TokenResponse(
            token=auth_result["token"],
            user=auth_result["user"],
            expires_in=7200  # 2 hours
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration failed", email=user_data.email, error=str(e))
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=TokenResponse)
async def login_user(credentials: UserLogin):
    """Authenticate user and return access token"""
    try:
        auth_result = pb_client.authenticate_user(credentials.email, credentials.password)
        
        if not auth_result:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        logger.info("User login successful", email=credentials.email)
        
        return TokenResponse(
            token=auth_result["token"],
            user=auth_result["user"],
            expires_in=7200  # 2 hours
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", email=credentials.email, error=str(e))
        raise HTTPException(status_code=500, detail="Login failed")

@router.post("/logout")
async def logout_user():
    """Logout current user"""
    try:
        # PocketBase handles token invalidation automatically
        pb_client.client.auth_store.clear()
        
        logger.info("User logout successful")
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error("Logout failed", error=str(e))
        raise HTTPException(status_code=500, detail="Logout failed")

@router.get("/me")
async def get_current_user():
    """Get current authenticated user information"""
    try:
        if not pb_client.client.auth_store.is_valid:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        user = pb_client.client.auth_store.model
        
        # Get additional profile data based on user role
        profile_data = None
        if user.role == "athlete":
            try:
                athlete = pb_client.client.collection("athletes").get_first_list_item(
                    f"user = '{user.id}'"
                )
                profile_data = athlete.to_dict()
            except:
                profile_data = None
        elif user.role == "brand":
            try:
                brand = pb_client.client.collection("brands").get_first_list_item(
                    f"user = '{user.id}'"
                )
                profile_data = brand.to_dict()
            except:
                profile_data = None
        
        return {
            "user": user.to_dict(),
            "profile": profile_data,
            "authenticated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get current user", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get user information")

@router.post("/refresh")
async def refresh_token():
    """Refresh the current access token"""
    try:
        if not pb_client.client.auth_store.is_valid:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        # PocketBase automatically handles token refresh
        auth_data = pb_client.client.collection("users").auth_refresh()
        
        logger.info("Token refresh successful")
        
        return TokenResponse(
            token=auth_data.token,
            user=auth_data.record.to_dict(),
            expires_in=7200
        )
        
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(status_code=401, detail="Token refresh failed")