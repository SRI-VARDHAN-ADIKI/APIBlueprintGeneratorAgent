"""
README generator agent for creating comprehensive documentation.
"""
from pathlib import Path
from typing import Dict, List, Optional
import json

from app.services.llm_service import get_llm_service
from app.services.mermaid_service import mermaid_service
from app.models.request_models import ReadmeLength, DocumentationStyle, ReadmeSection
from app.utils.file_utils import read_file_safe
from app.utils.logger import logger
from app.config import settings


class ReadmeGeneratorAgent:
    """Agent for generating README files."""
    
    def __init__(self):
        """Initialize the README generator agent."""
        self.mermaid_service = mermaid_service
        self.prompts_dir = settings.prompts_dir
    
    def generate_readme(
        self,
        analysis_result: Dict[str, any],
        length: ReadmeLength,
        sections: List[ReadmeSection],
        include_examples: bool,
        style: DocumentationStyle,
        custom_instructions: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Generate README content.
        
        Args:
            analysis_result: Repository analysis results
            length: Desired README length
            sections: Sections to include
            include_examples: Whether to include code examples
            style: Documentation style
            custom_instructions: Custom user instructions
        
        Returns:
            Dictionary with README content and metadata
        """
        logger.info("Starting README generation")
        
        try:
            # Prepare prompt variables
            prompt_vars = self._prepare_prompt_variables(
                analysis_result, length, sections, include_examples, style, custom_instructions
            )
            
            # Load prompt template
            prompt_template = self._load_prompt_template()
            
            # Generate README content
            readme_content = self._generate_content(prompt_template, prompt_vars)
            
            # Generate diagrams
            diagrams = self._generate_diagrams(analysis_result, sections)
            
            # Combine content with diagrams
            final_readme = self._combine_content_and_diagrams(readme_content, diagrams)
            
            # Calculate statistics
            stats = self._calculate_statistics(final_readme)
            
            result = {
                'content': final_readme,
                'diagrams': diagrams,
                'statistics': stats,
                'sections_included': [s.value for s in sections]
            }
            
            logger.info(f"README generated successfully ({stats['line_count']} lines)")
            return result
            
        except Exception as e:
            logger.error(f"Error generating README: {e}")
            raise
    
    def _prepare_prompt_variables(
        self,
        analysis: Dict[str, any],
        length: ReadmeLength,
        sections: List[ReadmeSection],
        include_examples: bool,
        style: DocumentationStyle,
        custom_instructions: Optional[str]
    ) -> Dict[str, str]:
        """Prepare variables for the prompt template."""
        
        repo_info = analysis.get('repository_info', {})
        code_analysis = analysis.get('code_analysis', {})
        
        # Format endpoints summary
        endpoints = code_analysis.get('endpoints', [])
        endpoints_summary = self._format_endpoints_summary(endpoints)
        
        # Get endpoint statistics
        endpoint_stats = code_analysis.get('endpoint_stats', {})
        endpoint_stats_summary = self._format_endpoint_stats(endpoint_stats)
        
        # Format code structure
        code_structure = self._format_code_structure(code_analysis)
        
        # Length descriptions
        length_descriptions = {
            ReadmeLength.SHORT: "100-300 lines, concise and to the point",
            ReadmeLength.MEDIUM: "300-600 lines, balanced detail",
            ReadmeLength.DETAILED: "600-1000+ lines, comprehensive and thorough"
        }
        
        # Style guidelines
        style_guidelines = self._get_style_guidelines(style)
        
        # Length guidelines
        length_guidelines = self._get_length_guidelines(length)
        
        # Section-specific guidelines
        section_guidelines = self._get_section_guidelines(sections)
        
        return {
            'project_name': repo_info.get('name', 'Project'),
            'repo_url': repo_info.get('url', ''),
            'languages': ', '.join(analysis.get('languages', [])),
            'frameworks': ', '.join(analysis.get('frameworks', [])),
            'total_files': str(analysis.get('file_analysis', {}).get('total_files', 0)),
            'endpoint_count': str(len(endpoints)),
            'endpoint_stats': endpoint_stats_summary,
            'endpoints_summary': endpoints_summary,
            'code_structure': code_structure,
            'length': length.value,
            'length_description': length_descriptions.get(length, ''),
            'sections': ', '.join([s.value.replace('_', ' ').title() for s in sections]),
            'include_examples': 'Yes' if include_examples else 'No',
            'style': style.value.replace('_', ' ').title(),
            'custom_instructions': custom_instructions or 'None',
            'style_guidelines': style_guidelines,
            'length_guidelines': length_guidelines,
            'section_guidelines': section_guidelines
        }
    
    def _format_endpoints_summary(self, endpoints: List[Dict[str, any]]) -> str:
        """Format endpoints for prompt."""
        if not endpoints:
            return "No API endpoints detected."
        
        summary = []
        
        # Add total count at the top
        summary.append(f"**Total API Endpoints: {len(endpoints)}**\n")
        
        for i, endpoint in enumerate(endpoints[:20], 1):  # Limit to 20
            method = endpoint.get('method', 'GET')
            path = endpoint.get('path', '/')
            func_name = endpoint.get('function_name', '')
            doc = endpoint.get('docstring', '')
            file_path = endpoint.get('file_path', 'unknown')
            line_num = endpoint.get('line_number', 0)
            
            summary.append(f"{i}. **{method} {path}**")
            summary.append(f"   - Function: `{func_name}`")
            summary.append(f"   - Location: `{file_path}` (line {line_num})")
            if doc:
                summary.append(f"   - Description: {doc.split(chr(10))[0]}")  # First line only
            summary.append("")
        
        if len(endpoints) > 20:
            summary.append(f"\n... and {len(endpoints) - 20} more endpoints")
        
        return '\n'.join(summary)
    
    def _format_endpoint_stats(self, stats: Dict[str, any]) -> str:
        """Format endpoint statistics for prompt."""
        if not stats or stats.get('total', 0) == 0:
            return "No endpoints detected"
        
        lines = []
        lines.append(f"**Total Endpoints: {stats.get('total', 0)}**\n")
        
        # By HTTP method
        by_method = stats.get('by_method', {})
        if by_method:
            lines.append("**By HTTP Method:**")
            for method, count in sorted(by_method.items()):
                lines.append(f"- {method}: {count}")
            lines.append("")
        
        # By file
        by_file = stats.get('by_file', {})
        if by_file:
            lines.append("**By File Location:**")
            for file_path, count in sorted(by_file.items(), key=lambda x: x[1], reverse=True)[:10]:
                lines.append(f"- `{file_path}`: {count} endpoint(s)")
        
        return '\n'.join(lines)
    
    def _format_code_structure(self, code_analysis: Dict[str, any]) -> str:
        """Format code structure information."""
        structure = []
        
        models = code_analysis.get('models', [])
        classes = code_analysis.get('classes', [])
        functions = code_analysis.get('functions', [])
        endpoint_stats = code_analysis.get('endpoint_stats', {})
        
        # Endpoint breakdown
        structure.append(f"- Total Endpoints: {endpoint_stats.get('total', 0)}")
        
        # By HTTP method
        by_method = endpoint_stats.get('by_method', {})
        if by_method:
            for method, count in sorted(by_method.items()):
                structure.append(f"  - {method}: {count}")
        
        structure.append(f"- Data Models: {len(models)}")
        structure.append(f"- Classes: {len(classes)}")
        structure.append(f"- Functions: {len(functions)}")
        
        if models:
            structure.append("\nKey Data Models:")
            for model in models[:5]:
                structure.append(f"  - {model.get('name')}")
        
        return '\n'.join(structure)
    
    def _get_style_guidelines(self, style: DocumentationStyle) -> str:
        """Get style-specific guidelines."""
        guidelines = {
            DocumentationStyle.TECHNICAL: """
- Use precise technical terminology
- Assume reader has development experience
- Focus on implementation details and technical accuracy
- Include detailed API specifications
- Use technical diagrams and architecture details
""",
            DocumentationStyle.BEGINNER_FRIENDLY: """
- Use clear, simple language
- Explain technical concepts when they appear
- Include more context and background information
- Provide step-by-step instructions
- Add helpful notes and tips
- Use analogies where appropriate
""",
            DocumentationStyle.COMPREHENSIVE: """
- Provide maximum detail and coverage
- Include both high-level overview and detailed specifics
- Cover all use cases and scenarios
- Include troubleshooting and FAQ sections
- Provide extensive examples
- Document edge cases and limitations
"""
        }
        return guidelines.get(style, guidelines[DocumentationStyle.TECHNICAL])
    
    def _get_length_guidelines(self, length: ReadmeLength) -> str:
        """Get length-specific guidelines."""
        guidelines = {
            ReadmeLength.SHORT: """
- Target: 100-300 lines
- Focus on essentials only
- Quick start guide approach
- Minimal examples
- Link to external documentation for details
""",
            ReadmeLength.MEDIUM: """
- Target: 300-600 lines
- Balanced coverage of all sections
- Include key examples
- Moderate detail in API documentation
- Cover main use cases
""",
            ReadmeLength.DETAILED: """
- Target: 600-1000+ lines
- Comprehensive coverage of all aspects
- Multiple examples per section
- Detailed API documentation
- Include advanced usage patterns
- Add troubleshooting and FAQ
"""
        }
        return guidelines.get(length, guidelines[ReadmeLength.MEDIUM])
    
    def _get_section_guidelines(self, sections: List[ReadmeSection]) -> str:
        """Generate guidelines for selected sections only."""
        section_instructions = {
            ReadmeSection.OVERVIEW: """
1. **Project Overview** (## Overview):
   - Create a compelling introduction
   - Explain what the project does
   - Highlight the main purpose and value proposition
   - Keep it concise but informative
""",
            ReadmeSection.FEATURES: """
2. **Features** (## Features):
   - List key features as bullet points
   - Extract features from analyzed code and endpoints
   - Use emojis for visual appeal
   - Group related features together
""",
            ReadmeSection.INSTALLATION: """
3. **Installation** (## Installation):
   - Step-by-step installation instructions
   - Include prerequisites
   - Show command-line examples
   - Cover different package managers if applicable
""",
            ReadmeSection.CONFIGURATION: """
4. **Configuration** (## Configuration):
   - Document environment variables
   - Show configuration file examples
   - Explain each configuration option
   - Include default values
""",
            ReadmeSection.API_DOCUMENTATION: """
5. **API Documentation** (## API Documentation):
   - **START with API Statistics:**
     * Total Endpoints: {endpoint_count}
     * Breakdown by HTTP method (GET: X, POST: Y, PUT: Z, DELETE: W)
     * Endpoints by file location
   - **Then document EACH endpoint with:**
     * HTTP method and path
     * File location (filename and line number)
     * Description
     * Request parameters/body
     * Response format
     * Example request/response
   - Group endpoints by file or functionality
   - Use tables for better readability
   - Include a summary table at the beginning with all endpoints
""",
            ReadmeSection.USAGE_EXAMPLES: """
6. **Usage Examples** (## Usage Examples):
   - Provide practical code examples
   - Show common use cases
   - Include request/response examples
   - Add explanatory comments
   - Use proper code formatting
""",
            ReadmeSection.ARCHITECTURE: """
7. **Architecture** (## Architecture):
   - Describe system architecture
   - Explain component interactions
   - Include architecture diagram if relevant
   - Explain technology choices
""",
            ReadmeSection.CONTRIBUTING: """
8. **Contributing** (## Contributing):
   - Guidelines for contributors
   - How to submit issues
   - Pull request process
   - Code style requirements
""",
            ReadmeSection.LICENSE: """
9. **License** (## License):
   - State the project license
   - Include license badge
   - Link to LICENSE file if exists
""",
            ReadmeSection.TROUBLESHOOTING: """
10. **Troubleshooting** (## Troubleshooting):
   - Common issues and solutions
   - Error messages and fixes
   - FAQ items
   - Debug tips
""",
            ReadmeSection.FAQ: """
11. **FAQ** (## FAQ):
   - Frequently asked questions
   - Clear Q&A format
   - Cover common concerns
"""
        }
        
        guidelines = ["**GENERATE ONLY THESE SECTIONS IN THIS ORDER:**\n"]
        for section in sections:
            if section in section_instructions:
                guidelines.append(section_instructions[section])
        
        guidelines.append("\n**DO NOT include any sections not listed above.**")
        
        return '\n'.join(guidelines)
    
    def _load_prompt_template(self) -> str:
        """Load the README generation prompt template."""
        prompt_file = self.prompts_dir / 'readme_generation.txt'
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt template not found: {prompt_file}")
        
        return read_file_safe(prompt_file)
    
    def _generate_content(self, template: str, variables: Dict[str, str]) -> str:
        """Generate README content using LLM."""
        # Get LLM service
        llm_service = get_llm_service()
        
        prompt = template.format(**variables)
        
        # Use higher token limit for README generation
        content = llm_service.generate_text(
            prompt,
            temperature=0.7,
            max_tokens=8000
        )
        
        return content
    
    def _generate_diagrams(
        self,
        analysis: Dict[str, any],
        sections: List[ReadmeSection]
    ) -> List[Dict[str, str]]:
        """Generate Mermaid diagrams."""
        diagrams = []
        
        endpoints = analysis.get('code_analysis', {}).get('endpoints', [])
        models = analysis.get('code_analysis', {}).get('models', [])
        classes = analysis.get('code_analysis', {}).get('classes', [])
        
        # Generate flowchart for main process flow
        if ReadmeSection.USAGE_EXAMPLES in sections or ReadmeSection.API_DOCUMENTATION in sections:
            # Create a generic workflow based on project type
            project_type = analysis.get('repository_info', {}).get('project_type', 'Application')
            
            if 'API' in project_type.upper() and endpoints:
                # API workflow
                flow_steps = [
                    "Client sends HTTP request",
                    "API validates request",
                    "Process business logic",
                    "Query/Update database",
                    "Return response to client"
                ]
            else:
                # Generic application workflow
                flow_steps = [
                    "Initialize application",
                    "Load configuration",
                    "Process input data",
                    "Execute main logic",
                    "Generate output"
                ]
            
            flowchart = self.mermaid_service.generate_flowchart(
                flow_steps,
                title="Application Workflow"
            )
            diagrams.append({
                'type': 'flowchart',
                'title': 'Application Workflow',
                'code': flowchart
            })
        
        # Generate sequence diagram for API endpoints
        if ReadmeSection.API_DOCUMENTATION in sections and endpoints:
            sequence_diagram = self.mermaid_service.generate_sequence_diagram(
                endpoints,
                title="API Request Flow"
            )
            diagrams.append({
                'type': 'sequence',
                'title': 'API Request Flow',
                'code': sequence_diagram
            })
        
        # Generate architecture diagram
        if ReadmeSection.ARCHITECTURE in sections:
            frameworks = analysis.get('frameworks', [])
            arch_diagram = self.mermaid_service.generate_architecture_diagram(
                frameworks,
                title="System Architecture"
            )
            diagrams.append({
                'type': 'architecture',
                'title': 'System Architecture',
                'code': arch_diagram
            })
        
        # Generate ER diagram for data models
        if ReadmeSection.API_DOCUMENTATION in sections and models:
            er_diagram = self.mermaid_service.generate_er_diagram(
                models,
                title="Data Models"
            )
            diagrams.append({
                'type': 'er',
                'title': 'Data Models',
                'code': er_diagram
            })
        
        # Generate class diagram for object-oriented code
        if classes and len(classes) >= 2:  # Only if there are multiple classes
            class_diagram = self.mermaid_service.generate_class_diagram(classes)
            diagrams.append({
                'type': 'class',
                'title': 'Class Structure',
                'code': class_diagram
            })
        
        return diagrams
    
    def _combine_content_and_diagrams(
        self,
        content: str,
        diagrams: List[Dict[str, str]]
    ) -> str:
        """Combine README content with diagrams."""
        if not diagrams:
            return content
        
        # Append diagrams to appropriate sections or at the end
        combined = content
        
        for diagram in diagrams:
            diagram_md = self.mermaid_service.wrap_diagram(
                diagram['code'],
                diagram['title']
            )
            
            # Try to insert diagram in appropriate section
            if diagram['type'] == 'flowchart':
                # Insert flowchart after Usage or Usage Examples section
                if '## Usage Examples' in combined or '## 📝 Usage Examples' in combined:
                    for usage_header in ['## 📝 Usage Examples', '## Usage Examples', '## Usage']:
                        if usage_header in combined:
                            combined = combined.replace(
                                usage_header,
                                f"{usage_header}\n\n{diagram_md}",
                                1
                            )
                            break
                else:
                    # Append at the end if no usage section found
                    combined += f"\n\n{diagram_md}"
            elif diagram['type'] == 'sequence' and ('## API' in combined or '## 📚 API' in combined):
                # Insert after API section header
                for api_header in ['## 📚 API Documentation', '## API Documentation', '## API']:
                    if api_header in combined:
                        combined = combined.replace(
                            api_header,
                            f"{api_header}\n\n{diagram_md}",
                            1
                        )
                        break
            elif diagram['type'] == 'architecture' and ('## Architecture' in combined or '## 🏗️ Architecture' in combined):
                for arch_header in ['## 🏗️ Architecture', '## Architecture']:
                    if arch_header in combined:
                        combined = combined.replace(
                            arch_header,
                            f"{arch_header}\n\n{diagram_md}",
                            1
                        )
                        break
            elif diagram['type'] == 'er' and ('## API' in combined or '## 📚 API' in combined):
                # Insert ER diagram in API section
                for api_header in ['## 📚 API Documentation', '## API Documentation', '## API']:
                    if api_header in combined:
                        combined = combined.replace(
                            api_header,
                            f"{api_header}\n\n{diagram_md}",
                            1
                        )
                        break
            elif diagram['type'] == 'class' and ('## Architecture' in combined or '## Code Structure' in combined):
                # Insert class diagram in Architecture section
                if '## Architecture' in combined:
                    combined = combined.replace(
                        '## Architecture',
                        f"## Architecture\n\n{diagram_md}",
                        1
                    )
                else:
                    combined = combined.replace(
                        '## Code Structure',
                        f"## Code Structure\n\n{diagram_md}",
                        1
                    )
            else:
                # Append at the end
                combined += f"\n\n{diagram_md}"
        
        return combined
    
    def _calculate_statistics(self, content: str) -> Dict[str, int]:
        """Calculate README statistics."""
        lines = content.splitlines()
        words = content.split()
        
        return {
            'line_count': len(lines),
            'word_count': len(words),
            'character_count': len(content)
        }


# Global agent instance
readme_generator_agent = ReadmeGeneratorAgent()
