from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import firebase_admin
from firebase_admin import credentials, auth

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User

# Initialize Firebase Admin SDK (if credentials are available)
if settings.FIREBASE_CREDENTIALS_PATH:
    try:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Firebase initialization failed: {e}")

security = HTTPBearer()

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    try:
        # Verify Firebase ID token
        if settings.FIREBASE_CREDENTIALS_PATH:
            decoded_token = auth.verify_id_token(token.credentials)
            firebase_uid = decoded_token['uid']
        else:
            # Mock authentication for development
            firebase_uid = "mock_user_123"
        
        # Get user from database
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if not user:
            # Create user if doesn't exist (for demo purposes)
            user = User(
                firebase_uid=firebase_uid,
                email="demo@example.com",
                display_name="Demo User",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user"
            )
        
        return user
        
    except Exception as e:
        print(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    return current_user