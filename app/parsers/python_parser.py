"""
Python AST parser for extracting code elements.
"""
import ast
from typing import List, Dict, Optional
from pathlib import Path

from app.parsers.base_parser import BaseParser
from app.utils.logger import logger


class PythonParser(BaseParser):
    """Parser for Python source files using AST."""
    
    def __init__(self, file_path: Path):
        """Initialize Python parser."""
        super().__init__(file_path)
        self.tree = None
        try:
            self.tree = ast.parse(self.content)
        except SyntaxError as e:
            logger.error(f"Syntax error parsing {file_path}: {e}")
    
    def extract_endpoints(self) -> List[Dict[str, any]]:
        """
        Extract API endpoints (FastAPI, Flask routes).
        
        Returns:
            List of endpoint information
        """
        if not self.tree:
            return []
        
        endpoints = []
        
        for node in ast.walk(self.tree):
            # FastAPI route decorators
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    endpoint_info = self._parse_decorator(decorator, node)
                    if endpoint_info:
                        endpoints.append(endpoint_info)
        
        return endpoints
    
    def _parse_decorator(self, decorator: ast.expr, func: ast.FunctionDef) -> Optional[Dict[str, any]]:
        """Parse decorator to extract endpoint information."""
        try:
            # FastAPI: @app.get("/path"), @router.post("/path")
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    method = decorator.func.attr.upper()
                    
                    # Check if it's an HTTP method
                    if method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']:
                        path = None
                        
                        # Extract path from first argument
                        if decorator.args:
                            if isinstance(decorator.args[0], ast.Constant):
                                path = decorator.args[0].value
                        
                        if path:
                            return {
                                'method': method,
                                'path': path,
                                'function_name': func.name,
                                'parameters': self._extract_function_params(func),
                                'docstring': ast.get_docstring(func),
                                'line_number': func.lineno
                            }
            
            # Flask: @app.route("/path", methods=["GET"])
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    if decorator.func.attr == 'route':
                        path = None
                        methods = ['GET']  # Default
                        
                        if decorator.args:
                            if isinstance(decorator.args[0], ast.Constant):
                                path = decorator.args[0].value
                        
                        # Extract methods from kwargs
                        for keyword in decorator.keywords:
                            if keyword.arg == 'methods':
                                if isinstance(keyword.value, ast.List):
                                    methods = [
                                        elt.value for elt in keyword.value.elts
                                        if isinstance(elt, ast.Constant)
                                    ]
                        
                        if path:
                            return {
                                'method': ', '.join(methods),
                                'path': path,
                                'function_name': func.name,
                                'parameters': self._extract_function_params(func),
                                'docstring': ast.get_docstring(func),
                                'line_number': func.lineno
                            }
        
        except Exception as e:
            logger.debug(f"Error parsing decorator: {e}")
        
        return None
    
    def _extract_function_params(self, func: ast.FunctionDef) -> List[Dict[str, any]]:
        """Extract function parameters."""
        params = []
        
        for arg in func.args.args:
            param_info = {
                'name': arg.arg,
                'type': None
            }
            
            # Extract type annotation if present
            if arg.annotation:
                param_info['type'] = ast.unparse(arg.annotation)
            
            params.append(param_info)
        
        return params
    
    def extract_models(self) -> List[Dict[str, any]]:
        """
        Extract Pydantic models or dataclasses.
        
        Returns:
            List of model information
        """
        if not self.tree:
            return []
        
        models = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a Pydantic model
                is_model = False
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        if base.id in ['BaseModel', 'SQLModel']:
                            is_model = True
                            break
                
                if is_model:
                    models.append({
                        'name': node.name,
                        'fields': self._extract_class_fields(node),
                        'docstring': ast.get_docstring(node),
                        'line_number': node.lineno
                    })
        
        return models
    
    def _extract_class_fields(self, cls: ast.ClassDef) -> List[Dict[str, any]]:
        """Extract fields from a class."""
        fields = []
        
        for item in cls.body:
            if isinstance(item, ast.AnnAssign):
                field_info = {
                    'name': item.target.id if isinstance(item.target, ast.Name) else str(item.target),
                    'type': ast.unparse(item.annotation) if item.annotation else None,
                    'default': ast.unparse(item.value) if item.value else None
                }
                fields.append(field_info)
        
        return fields
    
    def extract_functions(self) -> List[Dict[str, any]]:
        """
        Extract function definitions.
        
        Returns:
            List of function information
        """
        if not self.tree:
            return []
        
        functions = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                # Skip methods (functions inside classes)
                parent = None
                for parent_node in ast.walk(self.tree):
                    if isinstance(parent_node, ast.ClassDef):
                        if node in ast.walk(parent_node):
                            parent = parent_node
                            break
                
                if not parent:
                    functions.append({
                        'name': node.name,
                        'parameters': self._extract_function_params(node),
                        'docstring': ast.get_docstring(node),
                        'return_type': ast.unparse(node.returns) if node.returns else None,
                        'line_number': node.lineno,
                        'is_async': isinstance(node, ast.AsyncFunctionDef)
                    })
        
        return functions
    
    def extract_classes(self) -> List[Dict[str, any]]:
        """
        Extract class definitions.
        
        Returns:
            List of class information
        """
        if not self.tree:
            return []
        
        classes = []
        
        for node in self.tree.body:
            if isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'bases': [ast.unparse(base) for base in node.bases],
                    'methods': self._extract_class_methods(node),
                    'attributes': self._extract_class_fields(node),
                    'docstring': ast.get_docstring(node),
                    'line_number': node.lineno
                })
        
        return classes
    
    def _extract_class_methods(self, cls: ast.ClassDef) -> List[Dict[str, any]]:
        """Extract methods from a class."""
        methods = []
        
        for item in cls.body:
            if isinstance(item, ast.FunctionDef):
                methods.append({
                    'name': item.name,
                    'parameters': self._extract_function_params(item),
                    'docstring': ast.get_docstring(item),
                    'line_number': item.lineno
                })
        
        return methods
    
    def extract_imports(self) -> List[str]:
        """
        Extract import statements.
        
        Returns:
            List of imported modules
        """
        if not self.tree:
            return []
        
        imports = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        return list(set(imports))  # Remove duplicates


def parse_python_file(file_path: Path) -> Dict[str, any]:
    """
    Convenience function to parse a Python file.
    
    Args:
        file_path: Path to Python file
    
    Returns:
        Parsed file summary
    """
    parser = PythonParser(file_path)
    return parser.get_summary()
