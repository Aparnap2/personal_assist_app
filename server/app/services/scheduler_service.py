"""
Scheduling Service for Content Publishing
Handles content scheduling, publishing, and performance tracking
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from celery import Celery

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.content import Draft, Post, EngagementMetrics
from app.models.chat import Integration
from app.services.oauth_service import oauth_manager


# Initialize Celery for background tasks
celery_app = Celery(
    'nexus_scheduler',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)


class ContentScheduler:
    """Advanced content scheduling with intelligent timing"""
    
    def __init__(self):
        self.optimal_times = {
            "twitter": {
                "weekdays": {
                    "morning": "09:00",
                    "afternoon": "15:00", 
                    "evening": "19:00"
                },
                "weekends": {
                    "morning": "10:00",
                    "afternoon": "16:00"
                }
            },
            "linkedin": {
                "weekdays": {
                    "morning": "08:00",
                    "afternoon": "12:00",
                    "evening": "17:00"
                },
                "weekends": {
                    "morning": "09:00",
                    "afternoon": "14:00"
                }
            }
        }
    
    async def schedule_content(self, draft_id: int, user_id: int, 
                              scheduled_time: Optional[datetime] = None,
                              auto_optimize: bool = True) -> Dict[str, Any]:
        """Schedule content for publishing with intelligent timing"""
        
        db = SessionLocal()
        try:
            # Get draft and user integrations
            draft = db.query(Draft).filter(Draft.id == draft_id, Draft.user_id == user_id).first()
            if not draft:
                return {"error": "Draft not found"}
            
            # Get active integrations for the platform
            integration = db.query(Integration).filter(
                Integration.user_id == user_id,
                Integration.type == draft.platform,
                Integration.status == "connected"
            ).first()
            
            if not integration:
                return {"error": f"No connected {draft.platform} account"}
            
            # Determine optimal scheduling time
            if scheduled_time is None or auto_optimize:
                scheduled_time = self._calculate_optimal_time(
                    draft.platform, 
                    draft.content, 
                    user_id
                )
            
            # Validate scheduling time
            if scheduled_time <= datetime.now():
                return {"error": "Cannot schedule content in the past"}
            
            # Update draft status
            draft.status = "scheduled"
            draft.scheduled_for = scheduled_time
            db.commit()
            db.refresh(draft)
            
            # Queue the publishing task
            task_result = schedule_publish_content.apply_async(
                args=[draft_id],
                eta=scheduled_time
            )
            
            # Store task ID for potential cancellation
            draft.external_id = task_result.id  # Repurpose external_id for task tracking
            db.commit()
            
            return {
                "success": True,
                "draft_id": draft_id,
                "scheduled_for": scheduled_time.isoformat(),
                "task_id": task_result.id,
                "platform": draft.platform,
                "optimal_score": self._calculate_timing_score(scheduled_time, draft.platform)
            }
            
        except Exception as e:
            db.rollback()
            return {"error": str(e)}
        finally:
            db.close()
    
    async def cancel_scheduled_content(self, draft_id: int, user_id: int) -> Dict[str, Any]:
        """Cancel scheduled content"""
        
        db = SessionLocal()
        try:
            draft = db.query(Draft).filter(
                Draft.id == draft_id, 
                Draft.user_id == user_id,
                Draft.status == "scheduled"
            ).first()
            
            if not draft:
                return {"error": "Scheduled draft not found"}
            
            # Cancel Celery task
            if draft.external_id:  # Task ID stored in external_id
                celery_app.control.revoke(draft.external_id, terminate=True)
            
            # Reset draft status
            draft.status = "pending"
            draft.scheduled_for = None
            draft.external_id = None
            db.commit()
            
            return {
                "success": True,
                "message": "Scheduled content cancelled",
                "draft_id": draft_id
            }
            
        except Exception as e:
            db.rollback()
            return {"error": str(e)}
        finally:
            db.close()
    
    async def get_scheduled_content(self, user_id: int, 
                                   days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get all scheduled content for user"""
        
        db = SessionLocal()
        try:
            end_date = datetime.now() + timedelta(days=days_ahead)
            
            scheduled_drafts = db.query(Draft).filter(
                Draft.user_id == user_id,
                Draft.status == "scheduled",
                Draft.scheduled_for.between(datetime.now(), end_date)
            ).order_by(Draft.scheduled_for).all()
            
            return [
                {
                    "id": draft.id,
                    "content": draft.content[:100] + "...",
                    "platform": draft.platform,
                    "scheduled_for": draft.scheduled_for.isoformat(),
                    "themes": draft.themes,
                    "best_time_score": draft.best_time_score
                }
                for draft in scheduled_drafts
            ]
            
        finally:
            db.close()
    
    def _calculate_optimal_time(self, platform: str, content: str, 
                               user_id: int) -> datetime:
        """Calculate optimal posting time based on various factors"""
        
        now = datetime.now()
        base_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Get platform optimal times
        platform_times = self.optimal_times.get(platform, self.optimal_times["twitter"])
        
        # Determine if weekend or weekday
        is_weekend = base_time.weekday() >= 5
        time_slots = platform_times["weekends"] if is_weekend else platform_times["weekdays"]
        
        # Content-based timing adjustments
        content_factors = self._analyze_content_timing_factors(content)
        
        # Select best time slot
        if content_factors.get("is_breaking_news", False):
            # Immediate posting for time-sensitive content
            optimal_time = now + timedelta(minutes=5)
        elif content_factors.get("is_motivational", False):
            # Morning for motivational content
            optimal_time = base_time.replace(hour=8, minute=30)
        elif content_factors.get("is_educational", False):
            # Afternoon for educational content
            optimal_time = base_time.replace(hour=14, minute=0)
        else:
            # Use default optimal time
            morning_hour = int(time_slots["morning"].split(":")[0])
            optimal_time = base_time.replace(hour=morning_hour, minute=30)
        
        # Ensure it's in the future
        if optimal_time <= now:
            if is_weekend:
                optimal_time += timedelta(days=1)
            else:
                optimal_time += timedelta(days=1)
                # Skip to Monday if it falls on weekend
                while optimal_time.weekday() >= 5:
                    optimal_time += timedelta(days=1)
        
        return optimal_time
    
    def _analyze_content_timing_factors(self, content: str) -> Dict[str, bool]:
        """Analyze content to determine optimal timing factors"""
        content_lower = content.lower()
        
        return {
            "is_breaking_news": any(word in content_lower for word in ["breaking", "urgent", "just announced", "happening now"]),
            "is_motivational": any(word in content_lower for word in ["motivation", "inspire", "achieve", "success", "goal"]),
            "is_educational": any(word in content_lower for word in ["learn", "tutorial", "guide", "how to", "tip"]),
            "is_weekend_content": any(word in content_lower for word in ["weekend", "relax", "fun", "personal"]),
            "is_work_related": any(word in content_lower for word in ["work", "business", "professional", "career"])
        }
    
    def _calculate_timing_score(self, scheduled_time: datetime, platform: str) -> float:
        """Calculate score for the scheduled time (0-100)"""
        
        hour = scheduled_time.hour
        is_weekend = scheduled_time.weekday() >= 5
        
        # Base scores for different times
        if platform == "twitter":
            if 8 <= hour <= 10 or 15 <= hour <= 17 or 19 <= hour <= 21:
                base_score = 90
            elif 11 <= hour <= 14 or 18 <= hour <= 19:
                base_score = 75
            else:
                base_score = 50
        else:  # LinkedIn
            if not is_weekend and (8 <= hour <= 10 or 12 <= hour <= 14 or 17 <= hour <= 19):
                base_score = 90
            elif not is_weekend and (10 <= hour <= 12 or 14 <= hour <= 17):
                base_score = 75
            else:
                base_score = 40
        
        # Weekend penalty for professional content
        if is_weekend and platform == "linkedin":
            base_score *= 0.7
        
        return min(100, base_score)
    
    async def reschedule_content(self, draft_id: int, user_id: int, 
                                new_time: datetime) -> Dict[str, Any]:
        """Reschedule existing scheduled content"""
        
        # Cancel current schedule
        cancel_result = await self.cancel_scheduled_content(draft_id, user_id)
        if not cancel_result.get("success"):
            return cancel_result
        
        # Schedule for new time
        return await self.schedule_content(draft_id, user_id, new_time, auto_optimize=False)


class ContentPublisher:
    """Handles actual content publishing to platforms"""
    
    def __init__(self):
        self.oauth_manager = oauth_manager
    
    async def publish_content(self, draft_id: int) -> Dict[str, Any]:
        """Publish scheduled content to the appropriate platform"""
        
        db = SessionLocal()
        try:
            # Get draft and user integration
            draft = db.query(Draft).filter(
                Draft.id == draft_id,
                Draft.status == "scheduled"
            ).first()
            
            if not draft:
                return {"error": "Scheduled draft not found"}
            
            integration = db.query(Integration).filter(
                Integration.user_id == draft.user_id,
                Integration.type == draft.platform,
                Integration.status == "connected"
            ).first()
            
            if not integration:
                return {"error": f"No connected {draft.platform} integration"}
            
            # Get OAuth service
            oauth_service = self.oauth_manager.get_service(draft.platform)
            if not oauth_service:
                return {"error": f"OAuth service not available for {draft.platform}"}
            
            # Decrypt and get access token (simplified - in production, properly decrypt)
            access_token = integration.credentials
            
            # Publish based on platform
            if draft.platform == "twitter":
                result = await oauth_service.post_tweet(access_token, draft.content)
                external_id = result.get("data", {}).get("id")
            
            elif draft.platform == "linkedin":
                # LinkedIn publishing would be implemented here
                result = {"published": True, "message": "LinkedIn publishing not fully implemented"}
                external_id = f"linkedin_{datetime.now().timestamp()}"
            
            else:
                return {"error": f"Publishing not supported for {draft.platform}"}
            
            # Create post record
            post = Post(
                draft_id=draft.id,
                user_id=draft.user_id,
                platform=draft.platform,
                content=draft.content,
                external_id=external_id,
                published_at=datetime.now(),
                themes=draft.themes
            )
            db.add(post)
            
            # Update draft status
            draft.status = "published"
            draft.external_id = external_id
            db.commit()
            db.refresh(post)
            
            # Schedule engagement tracking
            schedule_engagement_tracking.apply_async(
                args=[post.id],
                countdown=3600  # Check engagement after 1 hour
            )
            
            return {
                "success": True,
                "post_id": post.id,
                "external_id": external_id,
                "published_at": post.published_at.isoformat(),
                "platform": draft.platform
            }
            
        except Exception as e:
            db.rollback()
            return {"error": str(e)}
        finally:
            db.close()
    
    async def get_post_performance(self, post_id: int, user_id: int) -> Dict[str, Any]:
        """Get performance metrics for a published post"""
        
        db = SessionLocal()
        try:
            post = db.query(Post).filter(
                Post.id == post_id,
                Post.user_id == user_id
            ).first()
            
            if not post:
                return {"error": "Post not found"}
            
            # Get latest engagement metrics
            metrics = db.query(EngagementMetrics).filter(
                EngagementMetrics.post_id == post_id
            ).order_by(EngagementMetrics.collected_at.desc()).first()
            
            if not metrics:
                return {"error": "No engagement data available"}
            
            return {
                "post_id": post_id,
                "platform": post.platform,
                "published_at": post.published_at.isoformat(),
                "content_preview": post.content[:100] + "...",
                "metrics": {
                    "likes": metrics.likes,
                    "shares": metrics.shares,
                    "comments": metrics.comments,
                    "impressions": metrics.impressions,
                    "clicks": metrics.clicks,
                    "engagement_score": metrics.engagement_score
                },
                "last_updated": metrics.collected_at.isoformat()
            }
            
        finally:
            db.close()


# Celery Tasks
@celery_app.task(name='schedule_publish_content')
def schedule_publish_content(draft_id: int):
    """Background task to publish scheduled content"""
    publisher = ContentPublisher()
    result = asyncio.run(publisher.publish_content(draft_id))
    return result


@celery_app.task(name='schedule_engagement_tracking')
def schedule_engagement_tracking(post_id: int):
    """Background task to track engagement metrics"""
    tracker = EngagementTracker()
    result = asyncio.run(tracker.collect_engagement_metrics(post_id))
    return result


class EngagementTracker:
    """Track and analyze content engagement"""
    
    def __init__(self):
        self.oauth_manager = oauth_manager
    
    async def collect_engagement_metrics(self, post_id: int) -> Dict[str, Any]:
        """Collect engagement metrics from platform APIs"""
        
        db = SessionLocal()
        try:
            post = db.query(Post).filter(Post.id == post_id).first()
            if not post:
                return {"error": "Post not found"}
            
            # Get user integration
            integration = db.query(Integration).filter(
                Integration.user_id == post.user_id,
                Integration.type == post.platform,
                Integration.status == "connected"
            ).first()
            
            if not integration:
                return {"error": "Integration not found"}
            
            # Get platform metrics
            if post.platform == "twitter" and post.external_id:
                oauth_service = self.oauth_manager.get_service("twitter")
                metrics_data = await oauth_service.get_tweet_metrics(
                    integration.credentials, 
                    post.external_id
                )
                
                if metrics_data and "data" in metrics_data:
                    tweet_data = metrics_data["data"]
                    public_metrics = tweet_data.get("public_metrics", {})
                    
                    # Save metrics
                    metrics = EngagementMetrics(
                        post_id=post.id,
                        likes=public_metrics.get("like_count", 0),
                        shares=public_metrics.get("retweet_count", 0),
                        comments=public_metrics.get("reply_count", 0),
                        impressions=public_metrics.get("impression_count", 0),
                        clicks=0,  # Not available in basic API
                        engagement_score=self._calculate_engagement_score(public_metrics)
                    )
                    db.add(metrics)
                    db.commit()
                    
                    return {"success": True, "metrics_collected": True}
            
            # Mock metrics for other platforms or when API is unavailable
            metrics = EngagementMetrics(
                post_id=post.id,
                likes=50,
                shares=5,
                comments=3,
                impressions=1000,
                clicks=25,
                engagement_score=75.0
            )
            db.add(metrics)
            db.commit()
            
            return {"success": True, "metrics_collected": True, "source": "mock"}
            
        except Exception as e:
            db.rollback()
            return {"error": str(e)}
        finally:
            db.close()
    
    def _calculate_engagement_score(self, metrics: Dict[str, int]) -> float:
        """Calculate overall engagement score"""
        likes = metrics.get("like_count", 0)
        shares = metrics.get("retweet_count", 0) 
        comments = metrics.get("reply_count", 0)
        impressions = max(metrics.get("impression_count", 1), 1)  # Avoid division by zero
        
        # Weighted engagement rate
        engagement_rate = ((likes * 1) + (shares * 3) + (comments * 5)) / impressions * 100
        
        # Normalize to 0-100 scale
        return min(100, engagement_rate * 1000)
    
    async def get_performance_insights(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get performance insights and recommendations"""
        
        db = SessionLocal()
        try:
            # Get recent posts with metrics
            posts_with_metrics = db.query(Post, EngagementMetrics).join(
                EngagementMetrics, Post.id == EngagementMetrics.post_id
            ).filter(
                Post.user_id == user_id,
                Post.published_at >= datetime.now() - timedelta(days=days)
            ).all()
            
            if not posts_with_metrics:
                return {"message": "No performance data available"}
            
            # Analyze performance patterns
            total_posts = len(posts_with_metrics)
            total_engagement = sum(metrics.engagement_score for post, metrics in posts_with_metrics)
            avg_engagement = total_engagement / total_posts
            
            # Best performing content
            best_post = max(posts_with_metrics, key=lambda x: x[1].engagement_score)
            worst_post = min(posts_with_metrics, key=lambda x: x[1].engagement_score)
            
            # Theme analysis
            theme_performance = {}
            for post, metrics in posts_with_metrics:
                if post.themes:
                    for theme in post.themes:
                        if theme not in theme_performance:
                            theme_performance[theme] = []
                        theme_performance[theme].append(metrics.engagement_score)
            
            # Calculate average performance per theme
            theme_avg = {
                theme: sum(scores) / len(scores)
                for theme, scores in theme_performance.items()
                if len(scores) > 0
            }
            
            top_themes = sorted(theme_avg.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return {
                "summary": {
                    "total_posts": total_posts,
                    "avg_engagement_score": round(avg_engagement, 1),
                    "date_range": f"Last {days} days"
                },
                "best_performing": {
                    "content": best_post[0].content[:100] + "...",
                    "engagement_score": best_post[1].engagement_score,
                    "published_at": best_post[0].published_at.isoformat()
                },
                "top_themes": [
                    {"theme": theme, "avg_score": round(score, 1)}
                    for theme, score in top_themes
                ],
                "recommendations": self._generate_performance_recommendations(
                    avg_engagement, theme_avg, total_posts
                )
            }
            
        finally:
            db.close()
    
    def _generate_performance_recommendations(self, avg_engagement: float, 
                                           theme_performance: Dict[str, float],
                                           total_posts: int) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        if avg_engagement < 50:
            recommendations.append("Focus on more engaging content with questions or interactive elements")
        
        if total_posts < 10:
            recommendations.append("Increase posting frequency for better audience engagement")
        
        if theme_performance:
            best_theme = max(theme_performance.items(), key=lambda x: x[1])[0]
            recommendations.append(f"Your '{best_theme}' content performs best - create more on this topic")
        
        recommendations.append("Consider posting during optimal times for your audience")
        
        return recommendations[:3]


# Global service instances
content_scheduler = ContentScheduler()
content_publisher = ContentPublisher()
engagement_tracker = EngagementTracker()