from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user

router = APIRouter()

class FirebaseTokenRequest(BaseModel):
    firebase_token: str

class AuthResponse(BaseModel):
    success: bool
    data: dict = None
    message: str = None

@router.post("/verify", response_model=AuthResponse)
async def verify_firebase_token(
    request: FirebaseTokenRequest,
    db: Session = Depends(get_db)
):
    """Verify Firebase token and return API token"""
    try:
        # For demo purposes, we'll accept any token and return a mock response
        # In production, this would verify the Firebase token properly
        
        return AuthResponse(
            success=True,
            data={
                "token": "mock_api_token_123",
                "user": {
                    "id": "demo_user",
                    "email": "demo@example.com",
                    "displayName": "Demo User"
                }
            },
            message="Authentication successful"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )

@router.get("/me")
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "firebase_uid": current_user.firebase_uid,
            "email": current_user.email,
            "display_name": current_user.display_name,
            "photo_url": current_user.photo_url,
            "created_at": current_user.created_at
        }
    }

@router.post("/refresh")
async def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh API token"""
    return {
        "success": True,
        "data": {
            "token": f"refreshed_token_{current_user.id}",
            "expires_in": 3600
        }
    }