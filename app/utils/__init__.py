"""Utility package initialization."""
from .logger import logger, setup_logger
from .file_utils import (
    get_file_hash,
    get_directory_size,
    get_file_extension,
    scan_directory,
    get_project_structure,
    clean_directory,
    detect_project_language,
    read_file_safe
)

__all__ = [
    'logger',
    'setup_logger',
    'get_file_hash',
    'get_directory_size',
    'get_file_extension',
    'scan_directory',
    'get_project_structure',
    'clean_directory',
    'detect_project_language',
    'read_file_safe'
]
