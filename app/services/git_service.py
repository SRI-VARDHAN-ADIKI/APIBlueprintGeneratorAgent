"""
Git service for repository operations.
"""
import os
import shutil
from pathlib import Path
from typing import Optional, Dict
from urllib.parse import urlparse
import git
from git import Repo

from app.config import settings
from app.utils.logger import logger
from app.utils.file_utils import get_directory_size


class GitService:
    """Service for Git repository operations."""
    
    def __init__(self):
        """Initialize Git service."""
        self.temp_dir = settings.temp_dir
        self.max_size_bytes = settings.max_repo_size_mb * 1024 * 1024
        self.timeout = settings.clone_timeout_seconds
    
    def _get_repo_name_from_url(self, url: str) -> str:
        """
        Extract repository name from URL.
        
        Args:
            url: Repository URL
        
        Returns:
            Repository name
        """
        parsed = urlparse(url)
        path = parsed.path.rstrip('.git').strip('/')
        return path.split('/')[-1]
    
    def _get_clone_path(self, url: str, job_id: str) -> Path:
        """
        Get the path where repository should be cloned.
        
        Args:
            url: Repository URL
            job_id: Unique job identifier
        
        Returns:
            Path for cloning
        """
        repo_name = self._get_repo_name_from_url(url)
        return self.temp_dir / job_id / repo_name
    
    def clone_repository(self, url: str, job_id: str) -> Dict[str, any]:
        """
        Clone a Git repository.
        
        Args:
            url: Repository URL
            job_id: Unique job identifier
        
        Returns:
            Dictionary with repository information
        
        Raises:
            ValueError: If repository is too large
            Exception: If cloning fails
        """
        clone_path = self._get_clone_path(url, job_id)
        
        try:
            logger.info(f"Cloning repository {url} to {clone_path}")
            
            # Create parent directory
            clone_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Clone with depth 1 for faster cloning
            repo = Repo.clone_from(
                url,
                clone_path,
                depth=1,
                single_branch=True
            )
            
            # Check repository size
            repo_size = get_directory_size(clone_path)
            if repo_size > self.max_size_bytes:
                self.cleanup_repository(job_id)
                raise ValueError(
                    f"Repository size ({repo_size / 1024 / 1024:.2f}MB) exceeds "
                    f"maximum allowed size ({settings.max_repo_size_mb}MB)"
                )
            
            # Get repository metadata
            repo_info = {
                'name': self._get_repo_name_from_url(url),
                'url': url,
                'path': str(clone_path),
                'size_bytes': repo_size,
                'size_mb': round(repo_size / 1024 / 1024, 2),
                'branch': repo.active_branch.name if not repo.head.is_detached else 'detached',
                'commit_hash': repo.head.commit.hexsha[:8],
                'commit_message': repo.head.commit.message.strip(),
                'author': str(repo.head.commit.author)
            }
            
            logger.info(f"Successfully cloned repository: {repo_info['name']}")
            return repo_info
            
        except git.GitCommandError as e:
            logger.error(f"Git command error while cloning {url}: {e}")
            self.cleanup_repository(job_id)
            raise Exception(f"Failed to clone repository: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error cloning repository {url}: {e}")
            self.cleanup_repository(job_id)
            raise
    
    def get_repository_path(self, job_id: str) -> Optional[Path]:
        """
        Get the path to a cloned repository.
        
        Args:
            job_id: Job identifier
        
        Returns:
            Path to repository or None if not found
        """
        job_dir = self.temp_dir / job_id
        if not job_dir.exists():
            return None
        
        # Find the repository directory
        subdirs = [d for d in job_dir.iterdir() if d.is_dir()]
        if subdirs:
            return subdirs[0]
        
        return None
    
    def cleanup_repository(self, job_id: str) -> None:
        """
        Clean up cloned repository.
        
        Args:
            job_id: Job identifier
        """
        job_dir = self.temp_dir / job_id
        if job_dir.exists():
            try:
                # On Windows, we need to handle read-only files in .git directory
                def handle_remove_readonly(func, path, exc):
                    """Error handler for Windows readonly files."""
                    import stat
                    if not os.access(path, os.W_OK):
                        os.chmod(path, stat.S_IWUSR)
                        func(path)
                    else:
                        raise
                
                shutil.rmtree(job_dir, onerror=handle_remove_readonly)
                logger.info(f"Cleaned up repository for job {job_id}")
            except Exception as e:
                logger.error(f"Error cleaning up repository for job {job_id}: {e}")
    
    def validate_repository_url(self, url: str) -> bool:
        """
        Validate if URL is a valid Git repository URL.
        
        Args:
            url: Repository URL
        
        Returns:
            True if valid, False otherwise
        """
        try:
            parsed = urlparse(url)
            
            # Check if it's a valid URL
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Check if it's a known Git hosting platform
            valid_hosts = ['github.com', 'gitlab.com', 'bitbucket.org']
            if not any(host in parsed.netloc for host in valid_hosts):
                logger.warning(f"URL {url} is not from a recognized Git hosting platform")
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating URL {url}: {e}")
            return False
    
    def get_file_count(self, repo_path: Path) -> int:
        """
        Get the total number of files in repository (excluding .git).
        
        Args:
            repo_path: Path to repository
        
        Returns:
            Number of files
        """
        count = 0
        for root, dirs, files in os.walk(repo_path):
            # Exclude .git directory
            if '.git' in root:
                continue
            count += len(files)
        return count


# Global service instance
git_service = GitService()
