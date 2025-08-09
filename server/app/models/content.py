from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Draft(Base):
    __tablename__ = "drafts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    platform = Column(String, nullable=False)  # twitter, linkedin
    status = Column(String, default="pending")  # pending, approved, rejected, scheduled, published
    variants = Column(JSON, nullable=True)
    scheduled_for = Column(DateTime, nullable=True)
    best_time_score = Column(Float, nullable=True)
    moderation_status = Column(String, default="pending")  # pending, approved, flagged
    moderation_flags = Column(JSON, nullable=True)
    themes = Column(JSON, nullable=True)
    prompt_used = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="drafts")
    post = relationship("Post", back_populates="draft", uselist=False)

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(Integer, ForeignKey("drafts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    external_id = Column(String, nullable=True)  # Platform-specific post ID
    published_at = Column(DateTime(timezone=True), nullable=False)
    engagement_data = Column(JSON, nullable=True)
    themes = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    draft = relationship("Draft", back_populates="post")

class EngagementMetrics(Base):
    __tablename__ = "engagement_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    engagement_score = Column(Float, default=0.0)
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    
class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # draft, consultation, general
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    context = Column(JSON, nullable=True)  # Related data
    created_at = Column(DateTime(timezone=True), server_default=func.now())