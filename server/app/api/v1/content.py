from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.content import Draft
from app.schemas.content import (
    DraftResponse, 
    GenerateDraftsRequest, 
    ApproveDraftRequest, 
    RejectDraftRequest,
    FeedbackCreate
)
from app.services.ai_service import ai_service

router = APIRouter()

@router.post("/generate")
async def generate_drafts(
    request: GenerateDraftsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate content drafts using AI"""
    try:
        # Get user profile for context (mock for now)
        user_profile = {
            "goals": ["grow audience", "thought leadership"],
            "themes": ["AI", "content marketing", "strategy"],
            "voice_profile": {
                "tone": {"formal": 40, "punchy": 70, "contrarian": 30}
            }
        }
        
        # Generate drafts using AI service
        drafts_data = await ai_service.generate_content_drafts(
            user_profile=user_profile,
            prompt=request.prompt,
            count=request.count,
            platform=request.platform
        )
        
        # Save drafts to database
        created_drafts = []
        for draft_data in drafts_data:
            draft = Draft(
                user_id=current_user.id,
                content=draft_data["content"],
                platform=draft_data["platform"],
                variants=draft_data.get("variants"),
                best_time_score=draft_data.get("best_time_score"),
                moderation_status=draft_data.get("moderation_status", "approved"),
                themes=draft_data.get("themes"),
                prompt_used=request.prompt
            )
            db.add(draft)
            created_drafts.append(draft)
        
        db.commit()
        
        # Refresh drafts to get IDs
        for draft in created_drafts:
            db.refresh(draft)
        
        return {
            "success": True,
            "data": [
                DraftResponse.model_validate(draft) for draft in created_drafts
            ]
        }
        
    except Exception as e:
        print(f"Error generating drafts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate drafts"
        )

@router.get("/drafts")
async def get_drafts(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's drafts with optional status filter"""
    try:
        query = db.query(Draft).filter(Draft.user_id == current_user.id)
        
        if status_filter:
            query = query.filter(Draft.status == status_filter)
        
        drafts = query.order_by(Draft.created_at.desc()).all()
        
        return {
            "success": True,
            "data": [DraftResponse.model_validate(draft) for draft in drafts]
        }
        
    except Exception as e:
        print(f"Error fetching drafts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch drafts"
        )

@router.post("/drafts/{draft_id}/approve")
async def approve_draft(
    draft_id: int,
    request: ApproveDraftRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a draft and optionally schedule it"""
    try:
        draft = db.query(Draft).filter(
            Draft.id == draft_id,
            Draft.user_id == current_user.id
        ).first()
        
        if not draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found"
            )
        
        # Update draft status
        if request.schedule_time:
            draft.status = "scheduled"
            draft.scheduled_for = request.schedule_time
        else:
            draft.status = "approved"
        
        db.commit()
        db.refresh(draft)
        
        return {
            "success": True,
            "data": DraftResponse.model_validate(draft)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error approving draft: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve draft"
        )

@router.post("/drafts/{draft_id}/reject")
async def reject_draft(
    draft_id: int,
    request: RejectDraftRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a draft"""
    try:
        draft = db.query(Draft).filter(
            Draft.id == draft_id,
            Draft.user_id == current_user.id
        ).first()
        
        if not draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found"
            )
        
        draft.status = "rejected"
        db.commit()
        db.refresh(draft)
        
        return {
            "success": True,
            "data": DraftResponse.model_validate(draft)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error rejecting draft: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject draft"
        )

@router.get("/drafts/{draft_id}")
async def get_draft(
    draft_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific draft details"""
    try:
        draft = db.query(Draft).filter(
            Draft.id == draft_id,
            Draft.user_id == current_user.id
        ).first()
        
        if not draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found"
            )
        
        return {
            "success": True,
            "data": DraftResponse.model_validate(draft)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching draft: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch draft"
        )