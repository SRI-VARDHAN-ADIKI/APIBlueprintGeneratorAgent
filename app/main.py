"""
Main entry point for the README Generator Agent FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.utils.logger import logger
from app.config import settings

# Create FastAPI app
app = FastAPI(
    title="README Generator Agent API",
    description="AI-powered README and API Blueprint Generator",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting README Generator Agent API")
    logger.info(f"API will be available at http://{settings.fastapi_host}:{settings.fastapi_port}")
    logger.info(f"Documentation at http://{settings.fastapi_host}:{settings.fastapi_port}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down README Generator Agent API")


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
    
    uvicorn.run(
        "main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
