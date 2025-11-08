"""
FastAPI routes for README generation API.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Dict
from pathlib import Path

from app.models.request_models import GenerateReadmeRequest
from app.models.response_models import (
    GenerateReadmeResponse,
    JobStatusResponse,
    HealthCheckResponse,
    ErrorResponse
)
from app.agents.orchestrator import orchestrator_agent
from app.services.llm_service import get_llm_service
from app.utils.logger import logger
from app.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Check API health status."""
    gemini_configured = False
    try:
        llm_service = get_llm_service()
        gemini_configured = llm_service.check_api_health()
    except:
        pass
    
    return HealthCheckResponse(
        status="healthy",
        gemini_api_configured=gemini_configured
    )


@router.post("/generate", response_model=GenerateReadmeResponse)
async def generate_readme(
    request: GenerateReadmeRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate README for a Git repository.
    
    - **repo_url**: GitHub/GitLab repository URL
    - **length**: README length (short/medium/detailed)
    - **sections**: Sections to include
    - **include_examples**: Include code examples
    - **diagram_complexity**: Diagram detail level
    - **style**: Documentation style
    """
    try:
        logger.info(f"Received README generation request for {request.repo_url}")
        
        # Create job
        job_id = orchestrator_agent.create_job(request)
        
        # Execute job in background
        background_tasks.add_task(orchestrator_agent.execute_job, job_id)
        
        return GenerateReadmeResponse(
            job_id=job_id,
            status="pending",
            message="README generation started",
            estimated_time_seconds=120
        )
        
    except Exception as e:
        logger.error(f"Error creating README generation job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status of a README generation job.
    
    - **job_id**: Job identifier returned from /generate
    """
    job = orchestrator_agent.get_job_status(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatusResponse(
        job_id=job['job_id'],
        status=job['status'],
        progress=job['progress'],
        message=job['message'],
        created_at=job['created_at'],
        updated_at=job['updated_at'],
        error=job.get('error')
    )


@router.get("/preview/{job_id}")
async def preview_readme(job_id: str):
    """
    Preview the generated README.
    
    - **job_id**: Job identifier
    """
    job = orchestrator_agent.get_job_status(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job['status'] != 'completed':
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed yet. Current status: {job['status']}"
        )
    
    result = job.get('result')
    if not result:
        raise HTTPException(status_code=500, detail="README not found in job result")
    
    return {
        'job_id': job_id,
        'repository_info': result.get('repository_info'),
        'readme_content': result.get('readme_content'),
        'diagrams': result.get('diagrams'),
        'statistics': result.get('statistics')
    }


@router.get("/download/{job_id}")
async def download_readme(job_id: str):
    """
    Download the generated README file.
    
    - **job_id**: Job identifier
    """
    readme_path = orchestrator_agent.get_readme_path(job_id)
    
    if not readme_path or not readme_path.exists():
        raise HTTPException(status_code=404, detail="README file not found")
    
    return FileResponse(
        path=readme_path,
        media_type='text/markdown',
        filename='README.md'
    )


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job and its associated files.
    
    - **job_id**: Job identifier
    """
    job = orchestrator_agent.get_job_status(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete job from memory
    if job_id in orchestrator_agent.jobs:
        del orchestrator_agent.jobs[job_id]
    
    # Delete output files
    job_output_dir = settings.output_dir / job_id
    if job_output_dir.exists():
        import shutil
        shutil.rmtree(job_output_dir)
    
    return {"message": f"Job {job_id} deleted successfully"}


@router.get("/jobs")
async def list_jobs():
    """
    List all jobs.
    """
    jobs = []
    for job_id, job in orchestrator_agent.jobs.items():
        jobs.append({
            'job_id': job_id,
            'status': job['status'],
            'created_at': job['created_at'],
            'repo_url': job['request'].get('repo_url')
        })
    
    return {'jobs': jobs, 'total': len(jobs)}
