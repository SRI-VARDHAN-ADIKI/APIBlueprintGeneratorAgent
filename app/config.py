"""
Application configuration using Pydantic Settings.
"""
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    
    # Server Configuration
    fastapi_host: str = Field(default="0.0.0.0", env="FASTAPI_HOST")
    fastapi_port: int = Field(default=8000, env="FASTAPI_PORT")
    streamlit_port: int = Field(default=8501, env="STREAMLIT_PORT")
    
    # Paths
    temp_dir: Path = Field(default=Path("./temp"), env="TEMP_DIR")
    output_dir: Path = Field(default=Path("./outputs"), env="OUTPUT_DIR")
    prompts_dir: Path = Field(default=Path("./prompts"), env="PROMPTS_DIR")
    
    # Limits
    max_repo_size_mb: int = Field(default=500, env="MAX_REPO_SIZE_MB")
    max_file_size_mb: int = Field(default=10, env="MAX_FILE_SIZE_MB")
    clone_timeout_seconds: int = Field(default=300, env="CLONE_TIMEOUT_SECONDS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default="app.log", env="LOG_FILE")
    
    # LLM Configuration
    gemini_model: str = Field(default="gemini-2.0-flash-exp", env="GEMINI_MODEL")
    temperature: float = Field(default=0.7, env="TEMPERATURE")
    max_tokens: int = Field(default=8000, env="MAX_TOKENS")
    
    # Processing
    max_concurrent_jobs: int = Field(default=5, env="MAX_CONCURRENT_JOBS")
    job_timeout_seconds: int = Field(default=600, env="JOB_TIMEOUT_SECONDS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
