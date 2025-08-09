from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.chat import Integration

router = APIRouter()

class ConnectIntegrationRequest(BaseModel):
    type: str  # twitter, linkedin, notion
    auth_code: str

@router.post("/connect")
async def connect_integration(
    request: ConnectIntegrationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Connect a new integration"""
    try:
        # Check if integration already exists
        existing = db.query(Integration)\
            .filter(
                Integration.user_id == current_user.id,
                Integration.type == request.type
            ).first()
        
        if existing:
            existing.status = "connected"
            existing.connected_at = func.now()
            integration = existing
        else:
            integration = Integration(
                user_id=current_user.id,
                type=request.type,
                status="connected",
                connected_at=func.now(),
                credentials="encrypted_credentials",  # Would encrypt actual credentials
                permissions=["read", "write"]
            )
            db.add(integration)
        
        db.commit()
        db.refresh(integration)
        
        return {
            "success": True,
            "data": {
                "id": integration.id,
                "type": integration.type,
                "status": integration.status,
                "connectedAt": integration.connected_at.isoformat()
            }
        }
        
    except Exception as e:
        print(f"Error connecting integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect integration"
        )

@router.get("")
async def get_integrations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's integrations"""
    try:
        integrations = db.query(Integration)\
            .filter(Integration.user_id == current_user.id)\
            .all()
        
        return {
            "success": True,
            "data": [
                {
                    "id": integration.id,
                    "type": integration.type,
                    "status": integration.status,
                    "permissions": integration.permissions,
                    "connectedAt": integration.connected_at.isoformat() if integration.connected_at else None,
                    "lastSyncAt": integration.last_sync_at.isoformat() if integration.last_sync_at else None
                }
                for integration in integrations
            ]
        }
        
    except Exception as e:
        print(f"Error fetching integrations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch integrations"
        )

@router.delete("/{integration_id}")
async def disconnect_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect an integration"""
    try:
        integration = db.query(Integration)\
            .filter(
                Integration.id == integration_id,
                Integration.user_id == current_user.id
            ).first()
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )
        
        integration.status = "disconnected"
        integration.credentials = None
        db.commit()
        
        return {
            "success": True,
            "message": "Integration disconnected"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error disconnecting integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disconnect integration"
        )