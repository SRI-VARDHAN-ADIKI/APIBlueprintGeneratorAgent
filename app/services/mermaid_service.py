"""
Mermaid diagram generation service.
"""
from typing import List, Dict, Optional
from app.utils.logger import logger


class MermaidService:
    """Service for generating Mermaid diagrams."""
    
    def generate_sequence_diagram(
        self,
        endpoints: List[Dict[str, any]],
        title: str = "API Sequence Diagram"
    ) -> str:
        """
        Generate a Mermaid sequence diagram for API endpoints.
        
        Args:
            endpoints: List of endpoint information
            title: Diagram title
        
        Returns:
            Mermaid diagram code
        """
        try:
            mermaid_code = f"sequenceDiagram\n"
            mermaid_code += f"    title {title}\n"
            mermaid_code += "    participant Client\n"
            mermaid_code += "    participant API\n"
            mermaid_code += "    participant Database\n\n"
            
            for endpoint in endpoints[:10]:  # Limit to 10 endpoints for clarity
                method = endpoint.get('method', 'GET')
                path = endpoint.get('path', '/unknown')
                description = endpoint.get('description', 'Process request')
                
                mermaid_code += f"    Client->>+API: {method} {path}\n"
                mermaid_code += f"    Note right of API: {description}\n"
                
                # Add database interaction for write operations
                if method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                    mermaid_code += f"    API->>+Database: Store/Update Data\n"
                    mermaid_code += f"    Database-->>-API: Confirmation\n"
                elif method == 'GET':
                    mermaid_code += f"    API->>+Database: Query Data\n"
                    mermaid_code += f"    Database-->>-API: Return Data\n"
                
                mermaid_code += f"    API-->>-Client: Response\n\n"
            
            return mermaid_code
            
        except Exception as e:
            logger.error(f"Error generating sequence diagram: {e}")
            return ""
    
    def generate_architecture_diagram(
        self,
        components: List[str],
        title: str = "System Architecture"
    ) -> str:
        """
        Generate a Mermaid architecture diagram.
        
        Args:
            components: List of system components
            title: Diagram title
        
        Returns:
            Mermaid diagram code
        """
        try:
            mermaid_code = "graph TB\n"
            mermaid_code += f"    title[{title}]\n\n"
            
            # Define common components
            if 'api' in str(components).lower() or 'fastapi' in str(components).lower():
                mermaid_code += "    Client[Client Application]\n"
                mermaid_code += "    API[API Server]\n"
                mermaid_code += "    Client -->|HTTP Requests| API\n\n"
            
            if 'database' in str(components).lower() or 'db' in str(components).lower():
                mermaid_code += "    DB[(Database)]\n"
                mermaid_code += "    API -->|Queries| DB\n\n"
            
            if 'auth' in str(components).lower():
                mermaid_code += "    Auth[Authentication Service]\n"
                mermaid_code += "    API -->|Validate| Auth\n\n"
            
            if 'cache' in str(components).lower() or 'redis' in str(components).lower():
                mermaid_code += "    Cache[Cache Layer]\n"
                mermaid_code += "    API -->|Cache| Cache\n\n"
            
            return mermaid_code
            
        except Exception as e:
            logger.error(f"Error generating architecture diagram: {e}")
            return ""
    
    def generate_er_diagram(
        self,
        models: List[Dict[str, any]],
        title: str = "Data Model"
    ) -> str:
        """
        Generate a Mermaid ER diagram for data models.
        
        Args:
            models: List of data models with fields
            title: Diagram title
        
        Returns:
            Mermaid diagram code
        """
        try:
            mermaid_code = "erDiagram\n"
            
            for model in models[:5]:  # Limit to 5 models
                model_name = model.get('name', 'Entity')
                fields = model.get('fields', [])
                
                mermaid_code += f"    {model_name} {{\n"
                for field in fields[:10]:  # Limit fields
                    field_name = field.get('name', 'field')
                    field_type = field.get('type', 'string')
                    mermaid_code += f"        {field_type} {field_name}\n"
                mermaid_code += "    }\n\n"
            
            return mermaid_code
            
        except Exception as e:
            logger.error(f"Error generating ER diagram: {e}")
            return ""
    
    def generate_flowchart(
        self,
        steps: List[str],
        title: str = "Process Flow"
    ) -> str:
        """
        Generate a Mermaid flowchart.
        
        Args:
            steps: List of process steps
            title: Diagram title
        
        Returns:
            Mermaid diagram code
        """
        try:
            mermaid_code = "flowchart TD\n"
            mermaid_code += f"    Start([{title}])\n"
            
            for i, step in enumerate(steps, 1):
                step_id = f"Step{i}"
                mermaid_code += f"    {step_id}[{step}]\n"
                
                if i == 1:
                    mermaid_code += f"    Start --> {step_id}\n"
                else:
                    prev_step = f"Step{i-1}"
                    mermaid_code += f"    {prev_step} --> {step_id}\n"
            
            last_step = f"Step{len(steps)}"
            mermaid_code += f"    {last_step} --> End([Complete])\n"
            
            return mermaid_code
            
        except Exception as e:
            logger.error(f"Error generating flowchart: {e}")
            return ""
    
    def generate_class_diagram(
        self,
        classes: List[Dict[str, any]]
    ) -> str:
        """
        Generate a Mermaid class diagram.
        
        Args:
            classes: List of class information
        
        Returns:
            Mermaid diagram code
        """
        try:
            mermaid_code = "classDiagram\n"
            
            for cls in classes[:5]:  # Limit to 5 classes
                class_name = cls.get('name', 'Class')
                methods = cls.get('methods', [])
                attributes = cls.get('attributes', [])
                
                mermaid_code += f"    class {class_name} {{\n"
                
                # Add attributes
                for attr in attributes[:5]:
                    attr_name = attr.get('name', 'attr')
                    attr_type = attr.get('type', 'any')
                    mermaid_code += f"        +{attr_type} {attr_name}\n"
                
                # Add methods
                for method in methods[:5]:
                    method_name = method.get('name', 'method')
                    mermaid_code += f"        +{method_name}()\n"
                
                mermaid_code += "    }\n\n"
            
            return mermaid_code
            
        except Exception as e:
            logger.error(f"Error generating class diagram: {e}")
            return ""
    
    def wrap_diagram(self, diagram_code: str, title: str) -> str:
        """
        Wrap Mermaid diagram code in markdown code block.
        
        Args:
            diagram_code: Mermaid diagram code
            title: Diagram title
        
        Returns:
            Markdown formatted diagram
        """
        return f"### {title}\n\n```mermaid\n{diagram_code}```\n\n"


# Global service instance
mermaid_service = MermaidService()
