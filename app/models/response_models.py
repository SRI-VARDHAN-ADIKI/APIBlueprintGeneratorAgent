"""
Response models for API endpoints.
"""
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job processing status."""
    PENDING = "pending"
    CLONING = "cloning"
    ANALYZING = "analyzing"
    PARSING = "parsing"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GenerateReadmeResponse(BaseModel):
    """Response model for README generation request."""
    
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    message: str = Field(..., description="Status message")
    estimated_time_seconds: Optional[int] = Field(None, description="Estimated completion time")


class JobStatusResponse(BaseModel):
    """Response model for job status check."""
    
    job_id: str = Field(..., description="Job identifier")
    status: JobStatus = Field(..., description="Current job status")
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    message: str = Field(..., description="Current status message")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    error: Optional[str] = Field(None, description="Error message if failed")


class RepositoryInfo(BaseModel):
    """Repository information extracted from analysis."""
    
    name: str
    url: str
    languages: List[str]
    frameworks: List[str]
    total_files: int
    total_lines: int
    endpoints_found: int


class EndpointInfo(BaseModel):
    """API endpoint information."""
    
    method: str
    path: str
    description: Optional[str] = None
    parameters: List[Dict[str, Any]] = Field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    response: Optional[Dict[str, Any]] = None


class DiagramInfo(BaseModel):
    """Diagram information."""
    
    type: str
    title: str
    mermaid_code: str


class ReadmeContent(BaseModel):
    """Generated README content."""
    
    content: str = Field(..., description="Markdown content")
    sections: List[str] = Field(..., description="Included sections")
    word_count: int = Field(..., description="Total word count")
    line_count: int = Field(..., description="Total line count")
    diagrams: List[DiagramInfo] = Field(default_factory=list, description="Generated diagrams")


class PreviewReadmeResponse(BaseModel):
    """Response model for README preview."""
    
    job_id: str
    repository_info: RepositoryInfo
    readme_content: ReadmeContent
    status: JobStatus


class DownloadReadmeResponse(BaseModel):
    """Response model for README download."""
    
    job_id: str
    file_name: str
    file_size_bytes: int
    download_url: str


class HealthCheckResponse(BaseModel):
    """Health check response."""
    
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    gemini_api_configured: bool
