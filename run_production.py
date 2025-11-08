"""
Production entry point for README Generator Agent.
This version disables auto-reload for stability.
"""
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.config import settings

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("README Generator Agent - Production Mode")
    print("=" * 60)
    print(f"Server: http://{settings.fastapi_host}:{settings.fastapi_port}")
    print(f"API Docs: http://{settings.fastapi_host}:{settings.fastapi_port}/docs")
    print("Auto-reload: DISABLED (production mode)")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=False,  # Disabled for production
        workers=1,
        log_level=settings.log_level.lower()
    )
