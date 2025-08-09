from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.content import Draft, Post, EngagementMetrics

router = APIRouter()

@router.get("")
async def get_analytics(
    range: str = Query("week", regex="^(week|month|quarter)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user analytics data"""
    try:
        # Calculate date range
        now = datetime.utcnow()
        if range == "week":
            start_date = now - timedelta(days=7)
        elif range == "month":
            start_date = now - timedelta(days=30)
        else:  # quarter
            start_date = now - timedelta(days=90)
        
        # Get draft counts
        drafts_generated = db.query(func.count(Draft.id))\
            .filter(
                Draft.user_id == current_user.id,
                Draft.created_at >= start_date
            ).scalar() or 0
        
        drafts_approved = db.query(func.count(Draft.id))\
            .filter(
                Draft.user_id == current_user.id,
                Draft.status == "approved",
                Draft.created_at >= start_date
            ).scalar() or 0
        
        posts_published = db.query(func.count(Post.id))\
            .filter(
                Post.user_id == current_user.id,
                Post.published_at >= start_date
            ).scalar() or 0
        
        # Calculate approval rate
        approval_rate = (drafts_approved / drafts_generated * 100) if drafts_generated > 0 else 0
        
        # Mock data for engagement and time saved
        engagement_growth = 12.5  # Would calculate from actual metrics
        time_saved = drafts_generated * 15  # Estimate 15 minutes per draft
        
        # Get top themes (mock data)
        top_themes = [
            {"theme": "AI Strategy", "posts": 8, "engagement": 156},
            {"theme": "Content Marketing", "posts": 6, "engagement": 142},
            {"theme": "Industry Insights", "posts": 4, "engagement": 98}
        ]
        
        # Get best performing content (mock data)
        best_performing_content = [
            {
                "id": 1,
                "content": "5 AI trends that will shape 2024...",
                "platform": "twitter",
                "publishedAt": "2024-01-15T10:30:00Z",
                "engagement": {
                    "likes": 87,
                    "shares": 23,
                    "comments": 12,
                    "impressions": 1200,
                    "score": 95
                }
            }
        ]
        
        return {
            "success": True,
            "data": {
                "userId": current_user.id,
                "timeRange": range,
                "draftsGenerated": drafts_generated,
                "draftsApproved": drafts_approved,
                "postsPublished": posts_published,
                "engagementGrowth": engagement_growth,
                "timeSaved": time_saved,
                "approvalRate": round(approval_rate, 1),
                "topThemes": top_themes,
                "bestPerformingContent": best_performing_content
            }
        }
        
    except Exception as e:
        print(f"Error fetching analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch analytics"
        )

@router.get("/engagement-trends")
async def get_engagement_trends(
    days: int = Query(30, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get engagement trends over time"""
    try:
        # Mock engagement trend data
        trends = []
        base_date = datetime.utcnow() - timedelta(days=days)
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            trends.append({
                "date": date.strftime("%Y-%m-%d"),
                "impressions": 1000 + (i * 50) + (i % 7 * 200),
                "engagement": 60 + (i % 10 * 8),
                "posts": 1 if i % 3 == 0 else 0
            })
        
        return {
            "success": True,
            "data": trends
        }
        
    except Exception as e:
        print(f"Error fetching engagement trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch engagement trends"
        )

@router.get("/recommendations")
async def get_ai_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered recommendations"""
    try:
        # Mock AI recommendations
        recommendations = [
            {
                "type": "posting_time",
                "title": "Optimal posting time",
                "description": "Your audience is most active on Tuesdays at 10:30 AM. Consider scheduling more content at this time.",
                "confidence": 0.85,
                "action": "schedule_posts"
            },
            {
                "type": "content_theme",
                "title": "Content theme opportunity", 
                "description": "\"Industry insights\" posts perform 23% better. Try creating more content around this theme.",
                "confidence": 0.78,
                "action": "generate_content"
            },
            {
                "type": "improvement",
                "title": "Great improvement",
                "description": "Your approval rate increased by 12% this week. Keep up the excellent work!",
                "confidence": 1.0,
                "action": None
            }
        ]
        
        return {
            "success": True,
            "data": recommendations
        }
        
    except Exception as e:
        print(f"Error fetching recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch recommendations"
        )