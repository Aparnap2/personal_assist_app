from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.chat import ChatMessage
from app.services.ai_service import ai_service

router = APIRouter()

class ChatMessageRequest(BaseModel):
    message: str

class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    actions: Optional[List[dict]] = None
    timestamp: str
    
    class Config:
        from_attributes = True

@router.post("/message")
async def send_chat_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to the AI assistant"""
    try:
        # Save user message
        user_message = ChatMessage(
            user_id=current_user.id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        
        # Get recent chat history for context
        recent_messages = db.query(ChatMessage)\
            .filter(ChatMessage.user_id == current_user.id)\
            .order_by(ChatMessage.created_at.desc())\
            .limit(10)\
            .all()
        
        # Format messages for AI
        messages = []
        for msg in reversed(recent_messages[:-1]):  # Exclude the just-added message
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        messages.append({"role": "user", "content": request.message})
        
        # Get user profile for context (mock)
        user_profile = {
            "goals": ["grow audience", "thought leadership"],
            "themes": ["AI", "content marketing", "strategy"]
        }
        
        # Generate AI response
        ai_response = await ai_service.chat_completion(
            messages=messages,
            user_profile=user_profile
        )
        
        # Save AI response
        assistant_message = ChatMessage(
            user_id=current_user.id,
            role="assistant",
            content=ai_response["content"],
            actions=ai_response.get("actions", [])
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)
        
        return {
            "success": True,
            "data": {
                "id": assistant_message.id,
                "role": assistant_message.role,
                "content": assistant_message.content,
                "actions": assistant_message.actions,
                "timestamp": assistant_message.created_at.isoformat()
            }
        }
        
    except Exception as e:
        print(f"Error in chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )

@router.get("/history")
async def get_chat_history(
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat message history"""
    try:
        messages = db.query(ChatMessage)\
            .filter(ChatMessage.user_id == current_user.id)\
            .order_by(ChatMessage.created_at.desc())\
            .limit(limit)\
            .all()
        
        # Reverse to get chronological order
        messages.reverse()
        
        return {
            "success": True,
            "data": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "actions": msg.actions,
                    "timestamp": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }
        
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch chat history"
        )

@router.delete("/history")
async def clear_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear chat message history"""
    try:
        db.query(ChatMessage)\
            .filter(ChatMessage.user_id == current_user.id)\
            .delete()
        db.commit()
        
        return {
            "success": True,
            "message": "Chat history cleared"
        }
        
    except Exception as e:
        print(f"Error clearing chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear chat history"
        )