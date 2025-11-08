"""
LLM service for Gemini AI integration.
"""
from typing import Optional, Dict, List
import google.generativeai as genai

from app.config import settings
from app.utils.logger import logger


class LLMService:
    """Service for LLM operations using Gemini."""
    
    def __init__(self):
        """Initialize LLM service."""
        self._llm = None
        self._initialized = False
        logger.info("LLM service created (lazy initialization)")
    
    def _ensure_initialized(self):
        """Ensure the LLM is initialized."""
        if not self._initialized:
            # Configure Gemini API
            genai.configure(api_key=settings.gemini_api_key)
            
            # Initialize the generative model
            self._model = genai.GenerativeModel(settings.gemini_model)
            
            self._initialized = True
            logger.info(f"Initialized LLM service with model: {settings.gemini_model}")
    
    def generate_text(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text using Gemini.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (overrides default)
            max_tokens: Maximum tokens (overrides default)
        
        Returns:
            Generated text
        """
        self._ensure_initialized()
        
        try:
            # Configure generation settings
            generation_config = {
                'temperature': temperature or settings.temperature,
                'max_output_tokens': max_tokens or settings.max_tokens,
            }
            
            # Generate content
            response = self._model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise
    
    def generate_with_template(
        self,
        template: str,
        variables: Dict[str, any],
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate text using a prompt template.
        
        Args:
            template: Prompt template string with {variable} placeholders
            variables: Variables to fill in template
            temperature: Sampling temperature
        
        Returns:
            Generated text
        """
        try:
            # Fill in template variables
            prompt = template.format(**variables)
            
            # Generate text
            return self.generate_text(prompt, temperature=temperature)
            
        except Exception as e:
            logger.error(f"Error generating with template: {e}")
            raise
    
    def generate_structured_output(
        self,
        prompt: str,
        schema: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Generate structured output based on a schema.
        
        Args:
            prompt: Input prompt
            schema: Expected output schema
        
        Returns:
            Structured output dictionary
        """
        try:
            # Add schema information to prompt
            schema_prompt = f"{prompt}\n\nPlease provide the output in the following JSON format:\n{schema}"
            
            response = self.generate_text(schema_prompt)
            
            # Try to parse as JSON
            import json
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # If not valid JSON, return as text
                logger.warning("LLM response is not valid JSON")
                return {"content": response}
            
        except Exception as e:
            logger.error(f"Error generating structured output: {e}")
            raise
    
    def summarize_code(
        self,
        code: str,
        language: str,
        max_length: int = 200
    ) -> str:
        """
        Generate a summary of code.
        
        Args:
            code: Source code
            language: Programming language
            max_length: Maximum summary length in words
        
        Returns:
            Code summary
        """
        prompt = f"""
Summarize the following {language} code in {max_length} words or less.
Focus on what the code does, its main functionality, and purpose.

Code:
```{language}
{code}
```

Summary:
"""
        return self.generate_text(prompt, temperature=0.3)
    
    def extract_api_description(
        self,
        endpoint_data: Dict[str, any]
    ) -> str:
        """
        Generate description for an API endpoint.
        
        Args:
            endpoint_data: Endpoint information
        
        Returns:
            Endpoint description
        """
        prompt = f"""
Generate a clear, concise description for the following API endpoint:

Method: {endpoint_data.get('method', 'Unknown')}
Path: {endpoint_data.get('path', 'Unknown')}
Function Name: {endpoint_data.get('function_name', 'Unknown')}
Parameters: {endpoint_data.get('parameters', [])}

Provide a 1-2 sentence description of what this endpoint does.
Description:
"""
        return self.generate_text(prompt, temperature=0.5)
    
    def check_api_health(self) -> bool:
        """
        Check if the Gemini API is accessible.
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            response = self.generate_text("Hello, respond with 'OK'", max_tokens=10)
            return len(response) > 0
        except Exception as e:
            logger.error(f"API health check failed: {e}")
            return False


# Global service instance (lazy initialization)
llm_service = None

def get_llm_service() -> LLMService:
    """Get or create the global LLM service instance."""
    global llm_service
    if llm_service is None:
        llm_service = LLMService()
    return llm_service
