"""
Orchestrator agent that coordinates all sub-agents.
"""
import uuid
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
import json

from app.agents.repo_analyzer import repo_analyzer_agent
from app.agents.readme_generator import readme_generator_agent
from app.models.request_models import GenerateReadmeRequest
from app.models.response_models import JobStatus
from app.services.git_service import git_service
from app.utils.logger import logger
from app.config import settings


class OrchestratorAgent:
    """Main orchestrator agent that coordinates the README generation workflow."""
    
    def __init__(self):
        """Initialize orchestrator agent."""
        self.repo_analyzer = repo_analyzer_agent
        self.readme_generator = readme_generator_agent
        self.git_service = git_service
        self.jobs = {}  # In-memory job storage (use database in production)
        self.output_dir = settings.output_dir
    
    def create_job(self, request: GenerateReadmeRequest) -> str:
        """
        Create a new README generation job.
        
        Args:
            request: README generation request
        
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        self.jobs[job_id] = {
            'job_id': job_id,
            'status': JobStatus.PENDING,
            'progress': 0,
            'message': 'Job created',
            'request': request.dict(),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'error': None,
            'result': None
        }
        
        logger.info(f"Created job {job_id} for repository {request.repo_url}")
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, any]]:
        """
        Get the status of a job.
        
        Args:
            job_id: Job identifier
        
        Returns:
            Job status information or None if not found
        """
        return self.jobs.get(job_id)
    
    def execute_job(self, job_id: str) -> Dict[str, any]:
        """
        Execute a README generation job.
        
        Args:
            job_id: Job identifier
        
        Returns:
            Job result
        """
        job = self.jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        try:
            request_data = job['request']
            repo_url = request_data['repo_url']
            
            # Step 1: Clone repository
            self._update_job_status(
                job_id,
                JobStatus.CLONING,
                10,
                "Cloning repository..."
            )
            
            # Validate URL
            if not self.git_service.validate_repository_url(str(repo_url)):
                raise ValueError("Invalid repository URL")
            
            # Step 2: Analyze repository
            self._update_job_status(
                job_id,
                JobStatus.ANALYZING,
                30,
                "Analyzing repository structure..."
            )
            
            analysis_result = self.repo_analyzer.analyze_repository(
                str(repo_url),
                job_id
            )
            
            # Step 3: Parse code
            self._update_job_status(
                job_id,
                JobStatus.PARSING,
                50,
                "Extracting API endpoints and code structure..."
            )
            
            # Analysis already includes parsing, so we can skip this step
            
            # Step 4: Generate README
            self._update_job_status(
                job_id,
                JobStatus.GENERATING,
                70,
                "Generating README with AI..."
            )
            
            readme_result = self.readme_generator.generate_readme(
                analysis_result,
                length=request_data.get('length', 'medium'),
                sections=request_data.get('sections', []),
                include_examples=request_data.get('include_examples', True),
                style=request_data.get('style', 'technical'),
                custom_instructions=request_data.get('custom_instructions')
            )
            
            # Step 5: Save README
            self._update_job_status(
                job_id,
                JobStatus.GENERATING,
                90,
                "Saving README file..."
            )
            
            output_path = self._save_readme(job_id, readme_result['content'])
            
            # Prepare result
            result = {
                'readme_path': str(output_path),
                'readme_content': readme_result['content'],
                'diagrams': readme_result['diagrams'],
                'statistics': readme_result['statistics'],
                'repository_info': {
                    'name': analysis_result['repository_info']['name'],
                    'url': str(repo_url),
                    'languages': analysis_result['languages'],
                    'frameworks': analysis_result['frameworks'],
                    'total_files': analysis_result['file_analysis']['total_files'],
                    'total_lines': analysis_result['file_analysis']['total_lines'],
                    'endpoints_found': len(analysis_result['code_analysis']['endpoints'])
                }
            }
            
            # Step 6: Complete
            self._update_job_status(
                job_id,
                JobStatus.COMPLETED,
                100,
                "README generated successfully!"
            )
            
            job['result'] = result
            
            # Cleanup cloned repository
            self.git_service.cleanup_repository(job_id)
            
            logger.info(f"Job {job_id} completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error executing job {job_id}: {e}")
            self._update_job_status(
                job_id,
                JobStatus.FAILED,
                0,
                f"Job failed: {str(e)}",
                error=str(e)
            )
            
            # Cleanup on failure
            try:
                self.git_service.cleanup_repository(job_id)
            except:
                pass
            
            raise
    
    def _update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: int,
        message: str,
        error: Optional[str] = None
    ):
        """Update job status."""
        if job_id in self.jobs:
            self.jobs[job_id].update({
                'status': status,
                'progress': progress,
                'message': message,
                'updated_at': datetime.utcnow(),
                'error': error
            })
            logger.info(f"Job {job_id}: {message} ({progress}%)")
    
    def _save_readme(self, job_id: str, content: str) -> Path:
        """
        Save README content to file.
        
        Args:
            job_id: Job identifier
            content: README content
        
        Returns:
            Path to saved file
        """
        job_output_dir = self.output_dir / job_id
        job_output_dir.mkdir(parents=True, exist_ok=True)
        
        readme_path = job_output_dir / 'README.md'
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Saved README to {readme_path}")
        return readme_path
    
    def get_readme_content(self, job_id: str) -> Optional[str]:
        """
        Get the generated README content.
        
        Args:
            job_id: Job identifier
        
        Returns:
            README content or None if not found
        """
        job = self.jobs.get(job_id)
        if not job or not job.get('result'):
            return None
        
        return job['result'].get('readme_content')
    
    def get_readme_path(self, job_id: str) -> Optional[Path]:
        """
        Get the path to the generated README file.
        
        Args:
            job_id: Job identifier
        
        Returns:
            Path to README file or None if not found
        """
        readme_path = self.output_dir / job_id / 'README.md'
        if readme_path.exists():
            return readme_path
        return None


# Global orchestrator instance
orchestrator_agent = OrchestratorAgent()
