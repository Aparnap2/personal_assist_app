from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.api.v1 import auth, content, chat, integrations, analytics, users
from app.core.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Nexus Personal AI API",
    description="AI-powered personal assistant for content creation and automation",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# API routes
app.include_router(auth.router, prefix="/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/v1/user", tags=["users"])
app.include_router(content.router, prefix="/v1/content", tags=["content"])
app.include_router(chat.router, prefix="/v1/chat", tags=["chat"])
app.include_router(integrations.router, prefix="/v1/integrations", tags=["integrations"])
app.include_router(analytics.router, prefix="/v1/analytics", tags=["analytics"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.DEBUG
    )