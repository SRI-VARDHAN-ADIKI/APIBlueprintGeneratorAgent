"""
File utility functions for repository operations.
"""
import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import hashlib


def get_file_hash(file_path: Path) -> str:
    """
    Calculate MD5 hash of a file.
    
    Args:
        file_path: Path to the file
    
    Returns:
        MD5 hash string
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_directory_size(directory: Path) -> int:
    """
    Calculate total size of a directory in bytes.
    
    Args:
        directory: Path to the directory
    
    Returns:
        Total size in bytes
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            file_path = Path(dirpath) / filename
            if file_path.exists():
                total_size += file_path.stat().st_size
    return total_size


def get_file_extension(file_path: Path) -> str:
    """
    Get file extension without the dot.
    
    Args:
        file_path: Path to the file
    
    Returns:
        File extension (lowercase)
    """
    return file_path.suffix.lstrip('.').lower()


def scan_directory(
    directory: Path,
    extensions: Optional[List[str]] = None,
    exclude_dirs: Optional[List[str]] = None
) -> List[Path]:
    """
    Recursively scan directory for files with specific extensions.
    
    Args:
        directory: Directory to scan
        extensions: List of file extensions to include (without dot)
        exclude_dirs: List of directory names to exclude
    
    Returns:
        List of file paths
    """
    if exclude_dirs is None:
        exclude_dirs = [
            '.git', '__pycache__', 'node_modules', '.venv', 'venv',
            'dist', 'build', '.pytest_cache', '.mypy_cache', 'env'
        ]
    
    files = []
    for root, dirs, filenames in os.walk(directory):
        # Remove excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for filename in filenames:
            file_path = Path(root) / filename
            
            if extensions is None:
                files.append(file_path)
            else:
                if get_file_extension(file_path) in extensions:
                    files.append(file_path)
    
    return files


def get_project_structure(directory: Path, max_depth: int = 3) -> Dict:
    """
    Get hierarchical structure of a project directory.
    
    Args:
        directory: Root directory
        max_depth: Maximum depth to traverse
    
    Returns:
        Dictionary representing directory structure
    """
    def _build_tree(path: Path, current_depth: int = 0) -> Dict:
        if current_depth >= max_depth:
            return {}
        
        tree = {
            'name': path.name,
            'type': 'directory' if path.is_dir() else 'file',
            'children': []
        }
        
        if path.is_dir():
            try:
                for item in sorted(path.iterdir()):
                    # Skip hidden files and common excludes
                    if item.name.startswith('.') or item.name in ['__pycache__', 'node_modules']:
                        continue
                    tree['children'].append(_build_tree(item, current_depth + 1))
            except PermissionError:
                pass
        
        return tree
    
    return _build_tree(directory)


def clean_directory(directory: Path, keep_gitignore: bool = True) -> None:
    """
    Remove all contents of a directory.
    
    Args:
        directory: Directory to clean
        keep_gitignore: Whether to keep .gitignore file
    """
    if not directory.exists():
        return
    
    for item in directory.iterdir():
        if keep_gitignore and item.name == '.gitignore':
            continue
        
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def detect_project_language(directory: Path) -> List[str]:
    """
    Detect programming languages used in a project.
    
    Args:
        directory: Project directory
    
    Returns:
        List of detected languages
    """
    language_indicators = {
        'python': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile'],
        'javascript': ['package.json', 'package-lock.json', 'yarn.lock'],
        'typescript': ['tsconfig.json'],
        'java': ['pom.xml', 'build.gradle', 'build.gradle.kts'],
        'go': ['go.mod', 'go.sum'],
        'rust': ['Cargo.toml', 'Cargo.lock'],
        'ruby': ['Gemfile', 'Gemfile.lock'],
        'php': ['composer.json', 'composer.lock'],
    }
    
    detected_languages = set()
    
    # Check for indicator files
    for language, indicators in language_indicators.items():
        for indicator in indicators:
            if (directory / indicator).exists():
                detected_languages.add(language)
    
    # Check file extensions
    extension_map = {
        'py': 'python',
        'js': 'javascript',
        'ts': 'typescript',
        'java': 'java',
        'go': 'go',
        'rs': 'rust',
        'rb': 'ruby',
        'php': 'php',
    }
    
    for file_path in scan_directory(directory):
        ext = get_file_extension(file_path)
        if ext in extension_map:
            detected_languages.add(extension_map[ext])
    
    return sorted(list(detected_languages))


def read_file_safe(file_path: Path, encoding: str = 'utf-8') -> Optional[str]:
    """
    Safely read a file with fallback encoding.
    
    Args:
        file_path: Path to the file
        encoding: Primary encoding to try
    
    Returns:
        File contents or None if unreadable
    """
    encodings = [encoding, 'utf-8', 'latin-1', 'cp1252']
    
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, LookupError):
            continue
    
    return None
