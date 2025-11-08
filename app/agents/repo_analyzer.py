"""
Repository analyzer agent for analyzing Git repositories.
"""
from pathlib import Path
from typing import Dict, List, Optional
import json

from app.services.git_service import git_service
from app.services.llm_service import get_llm_service
from app.parsers.python_parser import PythonParser
from app.utils.file_utils import scan_directory, detect_project_language, read_file_safe
from app.utils.logger import logger
from app.config import settings


class RepoAnalyzerAgent:
    """Agent for analyzing repository structure and extracting information."""
    
    def __init__(self):
        """Initialize the repository analyzer agent."""
        self.git_service = git_service
        self.prompts_dir = settings.prompts_dir
    
    def analyze_repository(self, repo_url: str, job_id: str) -> Dict[str, any]:
        """
        Analyze a Git repository.
        
        Args:
            repo_url: Repository URL
            job_id: Unique job identifier
        
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Starting repository analysis for job {job_id}")
        
        try:
            # Clone repository
            repo_info = self.git_service.clone_repository(repo_url, job_id)
            repo_path = Path(repo_info['path'])
            
            # Detect languages
            languages = detect_project_language(repo_path)
            logger.info(f"Detected languages: {languages}")
            
            # Scan files
            file_analysis = self._analyze_files(repo_path, languages)
            
            # Extract endpoints and models
            code_analysis = self._analyze_code_structure(repo_path, languages)
            
            # Get project metadata
            metadata = self._extract_metadata(repo_path)
            
            # Combine all analysis
            analysis_result = {
                'repository_info': repo_info,
                'languages': languages,
                'file_analysis': file_analysis,
                'code_analysis': code_analysis,
                'metadata': metadata,
                'frameworks': self._detect_frameworks(repo_path, languages),
                'project_type': self._determine_project_type(code_analysis, languages)
            }
            
            # Use LLM for intelligent analysis
            enhanced_analysis = self._enhance_with_llm(analysis_result, repo_path)
            analysis_result['enhanced_analysis'] = enhanced_analysis
            
            logger.info(f"Repository analysis completed for job {job_id}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing repository: {e}")
            raise
    
    def _analyze_files(self, repo_path: Path, languages: List[str]) -> Dict[str, any]:
        """Analyze file structure."""
        analysis = {
            'total_files': 0,
            'files_by_language': {},
            'total_lines': 0
        }
        
        language_extensions = {
            'python': ['py'],
            'javascript': ['js', 'jsx'],
            'typescript': ['ts', 'tsx'],
            'java': ['java'],
            'go': ['go'],
            'rust': ['rs']
        }
        
        for language in languages:
            extensions = language_extensions.get(language, [])
            if not extensions:
                continue
            
            files = scan_directory(repo_path, extensions=extensions)
            analysis['files_by_language'][language] = len(files)
            analysis['total_files'] += len(files)
            
            # Count lines
            for file_path in files:
                content = read_file_safe(file_path)
                if content:
                    analysis['total_lines'] += len(content.splitlines())
        
        return analysis
    
    def _analyze_code_structure(self, repo_path: Path, languages: List[str]) -> Dict[str, any]:
        """Analyze code structure and extract elements."""
        analysis = {
            'endpoints': [],
            'models': [],
            'functions': [],
            'classes': []
        }
        
        # Analyze Python files
        if 'python' in languages:
            python_files = scan_directory(repo_path, extensions=['py'])
            
            for file_path in python_files[:50]:  # Limit to 50 files
                try:
                    parser = PythonParser(file_path)
                    
                    endpoints = parser.extract_endpoints()
                    if endpoints:
                        analysis['endpoints'].extend(endpoints)
                    
                    models = parser.extract_models()
                    if models:
                        analysis['models'].extend(models)
                    
                    functions = parser.extract_functions()
                    if functions:
                        analysis['functions'].extend(functions[:5])  # Limit per file
                    
                    classes = parser.extract_classes()
                    if classes:
                        analysis['classes'].extend(classes[:3])  # Limit per file
                        
                except Exception as e:
                    logger.debug(f"Error parsing {file_path}: {e}")
                    continue
        
        # TODO: Add JavaScript/TypeScript parser
        # TODO: Add Java parser
        
        return analysis
    
    def _extract_metadata(self, repo_path: Path) -> Dict[str, any]:
        """Extract project metadata from common files."""
        metadata = {}
        
        # Python metadata
        if (repo_path / 'requirements.txt').exists():
            content = read_file_safe(repo_path / 'requirements.txt')
            if content:
                metadata['python_dependencies'] = [
                    line.strip() for line in content.splitlines()
                    if line.strip() and not line.startswith('#')
                ]
        
        if (repo_path / 'pyproject.toml').exists():
            metadata['has_pyproject'] = True
        
        # JavaScript metadata
        if (repo_path / 'package.json').exists():
            content = read_file_safe(repo_path / 'package.json')
            if content:
                try:
                    package_data = json.loads(content)
                    metadata['package_json'] = {
                        'name': package_data.get('name'),
                        'version': package_data.get('version'),
                        'description': package_data.get('description'),
                        'dependencies': list(package_data.get('dependencies', {}).keys())
                    }
                except json.JSONDecodeError:
                    pass
        
        # README
        readme_files = ['README.md', 'README.rst', 'README.txt', 'README']
        for readme_name in readme_files:
            readme_path = repo_path / readme_name
            if readme_path.exists():
                content = read_file_safe(readme_path)
                if content:
                    metadata['existing_readme_length'] = len(content)
                    metadata['has_readme'] = True
                    break
        
        # License
        if (repo_path / 'LICENSE').exists() or (repo_path / 'LICENSE.txt').exists():
            metadata['has_license'] = True
        
        return metadata
    
    def _detect_frameworks(self, repo_path: Path, languages: List[str]) -> List[str]:
        """Detect frameworks used in the project."""
        frameworks = []
        
        if 'python' in languages:
            # Check Python dependencies
            req_file = repo_path / 'requirements.txt'
            if req_file.exists():
                content = read_file_safe(req_file)
                if content:
                    content_lower = content.lower()
                    if 'fastapi' in content_lower:
                        frameworks.append('FastAPI')
                    if 'flask' in content_lower:
                        frameworks.append('Flask')
                    if 'django' in content_lower:
                        frameworks.append('Django')
                    if 'streamlit' in content_lower:
                        frameworks.append('Streamlit')
                    if 'sqlalchemy' in content_lower:
                        frameworks.append('SQLAlchemy')
        
        if 'javascript' in languages or 'typescript' in languages:
            package_json = repo_path / 'package.json'
            if package_json.exists():
                content = read_file_safe(package_json)
                if content:
                    try:
                        package_data = json.loads(content)
                        deps = {**package_data.get('dependencies', {}), 
                               **package_data.get('devDependencies', {})}
                        
                        if 'react' in deps:
                            frameworks.append('React')
                        if 'vue' in deps:
                            frameworks.append('Vue.js')
                        if 'express' in deps:
                            frameworks.append('Express.js')
                        if 'next' in deps:
                            frameworks.append('Next.js')
                    except json.JSONDecodeError:
                        pass
        
        return frameworks
    
    def _determine_project_type(self, code_analysis: Dict[str, any], languages: List[str]) -> str:
        """Determine the type of project."""
        endpoint_count = len(code_analysis.get('endpoints', []))
        
        if endpoint_count > 0:
            return 'REST API'
        elif 'python' in languages and code_analysis.get('classes'):
            return 'Python Library/Package'
        elif 'javascript' in languages or 'typescript' in languages:
            return 'JavaScript/TypeScript Application'
        else:
            return 'Software Project'
    
    def _enhance_with_llm(self, analysis: Dict[str, any], repo_path: Path) -> Dict[str, any]:
        """Use LLM to provide enhanced analysis."""
        try:
            # Get LLM service
            llm_service = get_llm_service()
            
            # Load analysis prompt
            prompt_file = self.prompts_dir / 'analysis.txt'
            if not prompt_file.exists():
                logger.warning("Analysis prompt file not found")
                return {}
            
            prompt_template = read_file_safe(prompt_file)
            
            # Prepare data for prompt
            files_list = list(scan_directory(repo_path, extensions=['py', 'js', 'ts']))[:20]
            
            prompt = prompt_template.format(
                repo_path=str(repo_path),
                repo_metadata=json.dumps(analysis.get('repository_info', {}), indent=2),
                files_list='\n'.join([f"- {f.name}" for f in files_list]),
                languages=', '.join(analysis.get('languages', []))
            )
            
            # Get LLM analysis
            response = llm_service.generate_text(prompt, temperature=0.3)
            
            # Try to parse JSON response
            try:
                # Extract JSON from response (look for first complete JSON object)
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    enhanced_data = json.loads(json_str)
                    logger.debug(f"Successfully parsed LLM enhancement: {list(enhanced_data.keys())}")
                    return enhanced_data
                else:
                    logger.warning("No JSON object found in LLM response")
                    return {}
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse LLM response as JSON: {e}")
                # Return partial analysis without LLM enhancement
                return {}
            
        except Exception as e:
            logger.error(f"Error in LLM enhancement: {e}")
            return {}


# Global agent instance
repo_analyzer_agent = RepoAnalyzerAgent()
