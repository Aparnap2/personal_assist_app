from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserProfile

router = APIRouter()

class UserProfileRequest(BaseModel):
    goals: Optional[List[str]] = None
    themes: Optional[List[str]] = None
    voice_profile: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None

class VoiceAnalysisRequest(BaseModel):
    samples: List[str]

@router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile"""
    try:
        profile = db.query(UserProfile)\
            .filter(UserProfile.user_id == current_user.id)\
            .first()
        
        if not profile:
            # Create default profile
            profile = UserProfile(
                user_id=current_user.id,
                goals=[],
                themes=[],
                voice_profile={},
                preferences={
                    "notifications": {
                        "drafts": True,
                        "approvals": True,
                        "analytics": True,
                        "engagement": True
                    },
                    "posting": {
                        "autoApprove": False,
                        "bestTimeOnly": True,
                        "requireModeration": True
                    },
                    "consultation": {
                        "proactive": True,
                        "frequency": "daily"
                    }
                }
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        
        return {
            "success": True,
            "data": {
                "userId": current_user.id,
                "goals": profile.goals or [],
                "themes": profile.themes or [],
                "voiceProfile": profile.voice_profile or {},
                "preferences": profile.preferences or {},
                "integrations": [],  # Would fetch from integrations table
                "createdAt": profile.created_at.isoformat(),
                "updatedAt": profile.updated_at.isoformat() if profile.updated_at else None
            }
        }
        
    except Exception as e:
        print(f"Error fetching user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile"
        )

@router.put("/profile")
async def update_user_profile(
    request: UserProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    try:
        profile = db.query(UserProfile)\
            .filter(UserProfile.user_id == current_user.id)\
            .first()
        
        if not profile:
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)
        
        # Update fields if provided
        if request.goals is not None:
            profile.goals = request.goals
        if request.themes is not None:
            profile.themes = request.themes
        if request.voice_profile is not None:
            profile.voice_profile = request.voice_profile
        if request.preferences is not None:
            profile.preferences = request.preferences
        
        db.commit()
        db.refresh(profile)
        
        return {
            "success": True,
            "data": {
                "userId": current_user.id,
                "goals": profile.goals or [],
                "themes": profile.themes or [],
                "voiceProfile": profile.voice_profile or {},
                "preferences": profile.preferences or {},
                "updatedAt": profile.updated_at.isoformat()
            }
        }
        
    except Exception as e:
        print(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )

@router.post("/voice/analyze")
async def analyze_voice_samples(
    request: VoiceAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze voice samples to create voice profile"""
    try:
        from app.services.ai_service import ai_service
        
        # Analyze voice samples
        voice_analysis = await ai_service.analyze_voice_samples(request.samples)
        
        if "error" in voice_analysis:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=voice_analysis["error"]
            )
        
        # Update user profile with voice analysis
        profile = db.query(UserProfile)\
            .filter(UserProfile.user_id == current_user.id)\
            .first()
        
        if not profile:
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)
        
        # Create voice profile structure
        voice_profile = {
            "id": f"voice_{current_user.id}",
            "samples": request.samples,
            "tone": voice_analysis.get("tone", {}),
            "style": voice_analysis.get("style", {}),
            "summary": voice_analysis.get("summary", ""),
            "createdAt": profile.created_at.isoformat() if profile.created_at else None,
            "updatedAt": profile.updated_at.isoformat() if profile.updated_at else None
        }
        
        profile.voice_profile = voice_profile
        db.commit()
        db.refresh(profile)
        
        return {
            "success": True,
            "data": voice_analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error analyzing voice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze voice samples"
        )