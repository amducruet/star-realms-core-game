"""
Star Realms Game - FastAPI Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.routes import game_routes

# Create FastAPI app
app = FastAPI(
    title="Star Realms Game API",
    description="Backend API for Star Realms-like card game",
    version="1.0.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(game_routes.router, prefix="/api", tags=["game"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Star Realms Game API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check for monitoring."""
    return {"status": "healthy"}


if __name__ == "__main__":
    print("🚀 Starting Star Realms Game Server...")
    print("📡 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🔌 WebSocket: ws://localhost:8000/api/ws/{game_id}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
