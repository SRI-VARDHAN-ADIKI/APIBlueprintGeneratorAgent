"""
Base parser interface for code analysis.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from pathlib import Path


class BaseParser(ABC):
    """Abstract base class for code parsers."""
    
    def __init__(self, file_path: Path):
        """
        Initialize parser.
        
        Args:
            file_path: Path to the file to parse
        """
        self.file_path = file_path
        self.content = self._read_file()
    
    def _read_file(self) -> str:
        """
        Read file content.
        
        Returns:
            File content as string
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(self.file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    @abstractmethod
    def extract_endpoints(self) -> List[Dict[str, any]]:
        """
        Extract API endpoints from the file.
        
        Returns:
            List of endpoint information dictionaries
        """
        pass
    
    @abstractmethod
    def extract_models(self) -> List[Dict[str, any]]:
        """
        Extract data models/schemas from the file.
        
        Returns:
            List of model information dictionaries
        """
        pass
    
    @abstractmethod
    def extract_functions(self) -> List[Dict[str, any]]:
        """
        Extract function definitions from the file.
        
        Returns:
            List of function information dictionaries
        """
        pass
    
    @abstractmethod
    def extract_classes(self) -> List[Dict[str, any]]:
        """
        Extract class definitions from the file.
        
        Returns:
            List of class information dictionaries
        """
        pass
    
    @abstractmethod
    def extract_imports(self) -> List[str]:
        """
        Extract import statements from the file.
        
        Returns:
            List of imported modules/packages
        """
        pass
    
    def get_summary(self) -> Dict[str, any]:
        """
        Get a summary of the file.
        
        Returns:
            Dictionary with file summary
        """
        return {
            'file_path': str(self.file_path),
            'file_name': self.file_path.name,
            'line_count': len(self.content.splitlines()),
            'character_count': len(self.content),
            'endpoints': self.extract_endpoints(),
            'models': self.extract_models(),
            'functions': self.extract_functions(),
            'classes': self.extract_classes(),
            'imports': self.extract_imports()
        }
