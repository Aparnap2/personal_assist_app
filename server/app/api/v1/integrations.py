from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.chat import Integration
from app.services.oauth_service import oauth_manager

router = APIRouter()

class ConnectIntegrationRequest(BaseModel):
    type: str  # twitter, linkedin, notion
    auth_code: str
    state: Optional[str] = None
    code_verifier: Optional[str] = None

class InitiateOAuthRequest(BaseModel):
    type: str  # twitter, notion

@router.post("/oauth/initiate")
async def initiate_oauth_flow(
    request: InitiateOAuthRequest,
    current_user: User = Depends(get_current_user)
):
    """Initiate OAuth flow for integration"""
    try:
        auth_data = await oauth_manager.initiate_oauth_flow(request.type)
        
        return {
            "success": True,
            "data": auth_data
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error initiating OAuth: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate OAuth flow"
        )

@router.post("/oauth/complete")
async def complete_oauth_flow(
    request: ConnectIntegrationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete OAuth flow and store integration"""
    try:
        # Complete OAuth flow
        token_data = await oauth_manager.complete_oauth_flow(
            request.type,
            request.auth_code,
            request.state,
            request.code_verifier
        )
        
        # Test integration
        test_result = await oauth_manager.test_integration(
            request.type,
            token_data["access_token"]
        )
        
        if not test_result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Integration test failed"
            )
        
        # Store integration
        existing = db.query(Integration).filter(
            Integration.user_id == current_user.id,
            Integration.type == request.type
        ).first()
        
        if existing:
            existing.status = "connected"
            existing.connected_at = func.now()
            existing.credentials = token_data["access_token"]  # In production: encrypt this
            existing.permissions = test_result.get("capabilities", [])
            integration = existing
        else:
            integration = Integration(
                user_id=current_user.id,
                type=request.type,
                status="connected",
                connected_at=func.now(),
                credentials=token_data["access_token"],  # In production: encrypt this
                permissions=test_result.get("capabilities", [])
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
                "connected_at": integration.connected_at.isoformat(),
                "permissions": integration.permissions,
                "user_info": test_result.get("user_info", {}),
                "capabilities": test_result.get("capabilities", [])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error completing OAuth: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete integration"
        )

@router.post("/connect")
async def connect_integration(
    request: ConnectIntegrationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Legacy endpoint - redirect to OAuth complete"""
    return await complete_oauth_flow(request, current_user, db)

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