from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class DraftBase(BaseModel):
    content: str
    platform: str
    variants: Optional[List[str]] = None
    themes: Optional[List[str]] = None

class DraftCreate(DraftBase):
    prompt_used: Optional[str] = None

class DraftUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    moderation_status: Optional[str] = None

class DraftResponse(DraftBase):
    id: int
    user_id: int
    status: str
    scheduled_for: Optional[datetime]
    best_time_score: Optional[float]
    moderation_status: str
    moderation_flags: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class GenerateDraftsRequest(BaseModel):
    prompt: Optional[str] = None
    count: int = 5
    platform: str = "twitter"

class ApproveDraftRequest(BaseModel):
    schedule_time: Optional[datetime] = None

class RejectDraftRequest(BaseModel):
    reason: Optional[str] = None

class FeedbackCreate(BaseModel):
    type: str  # draft, consultation, general
    rating: int  # 1-5
    comment: Optional[str] = None
    context: Optional[Dict[str, Any]] = None