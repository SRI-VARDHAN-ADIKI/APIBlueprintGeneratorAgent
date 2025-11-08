"""
Main entry point for the README Generator Agent FastAPI application.
Run this file from the project root directory.
"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.utils.logger import logger
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    logger.info("Starting README Generator Agent API")
    logger.info(f"API will be available at http://{settings.fastapi_host}:{settings.fastapi_port}")
    logger.info(f"Documentation at http://{settings.fastapi_host}:{settings.fastapi_port}/docs")
    
    yield
    
    # Shutdown
    logger.info("Shutting down README Generator Agent API")


# Create FastAPI app
app = FastAPI(
    title="README Generator Agent API",
    description="AI-powered README and API Blueprint Generator",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["README Generation"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "README Generator Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    # For development: reload only app/ and ui/ directories
    # This prevents reload on temp/ and outputs/ changes
    uvicorn.run(
        "main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=True,
        reload_dirs=["app", "ui"],  # Only watch these directories
        log_level=settings.log_level.lower()
    )
