"""
API Blueprint Generator Agent - Main Entry Point
Entry point for AgentThink platform deployment.
"""
import sys
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

# Import and run the FastAPI application
from app.main import app

# This module exposes the FastAPI app instance for deployment
# For local development, use: uvicorn app:app --reload
# For production, use: uvicorn app:app --host 0.0.0.0 --port 8000

if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    
    uvicorn.run(
        "app:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=False,
        log_level=settings.log_level.lower()
    )
