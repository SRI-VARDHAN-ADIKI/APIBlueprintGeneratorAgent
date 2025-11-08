"""
Request models for API endpoints.
"""
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, validator


class ReadmeLength(str, Enum):
    """README length options."""
    SHORT = "short"
    MEDIUM = "medium"
    DETAILED = "detailed"


class DocumentationStyle(str, Enum):
    """Documentation style options."""
    TECHNICAL = "technical"
    BEGINNER_FRIENDLY = "beginner_friendly"
    COMPREHENSIVE = "comprehensive"


class DiagramComplexity(str, Enum):
    """Diagram complexity options."""
    SIMPLE = "simple"
    DETAILED = "detailed"


class ReadmeSection(str, Enum):
    """Available README sections."""
    OVERVIEW = "overview"
    FEATURES = "features"
    INSTALLATION = "installation"
    CONFIGURATION = "configuration"
    API_DOCUMENTATION = "api_documentation"
    USAGE_EXAMPLES = "usage_examples"
    ARCHITECTURE = "architecture"
    CONTRIBUTING = "contributing"
    LICENSE = "license"
    TROUBLESHOOTING = "troubleshooting"
    FAQ = "faq"


class GenerateReadmeRequest(BaseModel):
    """Request model for README generation."""
    
    repo_url: HttpUrl = Field(
        ...,
        description="GitHub repository URL",
        example="https://github.com/user/repository"
    )
    
    length: ReadmeLength = Field(
        default=ReadmeLength.MEDIUM,
        description="Desired README length"
    )
    
    sections: List[ReadmeSection] = Field(
        default=[
            ReadmeSection.OVERVIEW,
            ReadmeSection.INSTALLATION,
            ReadmeSection.API_DOCUMENTATION,
            ReadmeSection.USAGE_EXAMPLES
        ],
        description="Sections to include in README"
    )
    
    include_examples: bool = Field(
        default=True,
        description="Include code examples in README"
    )
    
    diagram_complexity: DiagramComplexity = Field(
        default=DiagramComplexity.DETAILED,
        description="Complexity level of generated diagrams"
    )
    
    style: DocumentationStyle = Field(
        default=DocumentationStyle.TECHNICAL,
        description="Documentation writing style"
    )
    
    custom_instructions: Optional[str] = Field(
        default=None,
        description="Additional custom instructions for README generation"
    )
    
    @validator('repo_url')
    def validate_github_url(cls, v):
        """Validate that the URL is a GitHub repository."""
        url_str = str(v)
        if not ('github.com' in url_str or 'gitlab.com' in url_str or 'bitbucket.org' in url_str):
            raise ValueError('URL must be a valid GitHub, GitLab, or Bitbucket repository')
        return v
    
    @validator('sections')
    def validate_sections(cls, v):
        """Ensure at least one section is selected."""
        if not v or len(v) == 0:
            raise ValueError('At least one section must be selected')
        return v


class PreviewReadmeRequest(BaseModel):
    """Request model for README preview."""
    
    job_id: str = Field(
        ...,
        description="Job ID of the generated README"
    )


class DownloadReadmeRequest(BaseModel):
    """Request model for README download."""
    
    job_id: str = Field(
        ...,
        description="Job ID of the generated README"
    )
    
    include_diagrams: bool = Field(
        default=True,
        description="Include diagram files in download"
    )
