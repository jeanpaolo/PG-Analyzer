"""Cloud AI provider for OpenAI, Anthropic, and other cloud services."""

from typing import Dict, Any, Optional
from .ai_provider import AIProvider

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class CloudAIProvider(AIProvider):
    """AI provider using cloud-based models (OpenAI, Gemini, etc.)."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize cloud AI provider.
        
        Args:
            config: Configuration with keys:
                - provider: Provider name (openai, gemini, anthropic)
                - api_key: API key for the provider
                - model: Model name (default varies by provider)
                - temperature: Generation temperature (default: 0.7)
                - max_tokens: Maximum tokens to generate (default: 2000)
                - base_url: Custom API base URL (optional)
        """
        super().__init__(config)
        self.provider = self.config.get('provider', 'openai').lower()
        self.api_key = self.config.get('api_key')
        self.temperature = self.config.get('temperature', 0.7)
        self.max_tokens = self.config.get('max_tokens', 2000)
        self.base_url = self.config.get('base_url')
        
        # Set default models based on provider
        default_models = {
            'openai': 'gpt-4.1-mini',
            'gemini': 'gemini-2.5-flash',
            'anthropic': 'claude-3-sonnet-20240229'
        }
        self.model = self.config.get('model', default_models.get(self.provider, 'gpt-4.1-mini'))
        
        self.client = None
        if OPENAI_AVAILABLE and self.api_key:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate client based on provider."""
        if self.provider in ['openai', 'gemini']:
            # OpenAI-compatible API (including Gemini via OpenAI format)
            client_kwargs = {'api_key': self.api_key}
            if self.base_url:
                client_kwargs['base_url'] = self.base_url
            self.client = OpenAI(**client_kwargs)
        else:
            # For other providers, use OpenAI-compatible format
            client_kwargs = {'api_key': self.api_key}
            if self.base_url:
                client_kwargs['base_url'] = self.base_url
            self.client = OpenAI(**client_kwargs)
    
    def get_provider_name(self) -> str:
        return f"Cloud AI ({self.provider}/{self.model})"
    
    def is_available(self) -> bool:
        """Check if the cloud provider is properly configured."""
        if not OPENAI_AVAILABLE:
            return False
        
        if not self.api_key:
            return False
        
        if not self.client:
            return False
        
        return True
    
    def analyze(self, analysis_data: Dict[str, Any], analysis_type: str) -> str:
        """
        Analyze database data using cloud AI model.
        
        Args:
            analysis_data: Dictionary containing analysis results
            analysis_type: Type of analysis (structure, security, performance)
            
        Returns:
            Analysis report as string
        """
        if not self.is_available():
            raise RuntimeError(
                f"Cloud AI provider '{self.provider}' is not properly configured. "
                "Please ensure API key is set and openai package is installed."
            )
        
        prompt = self._build_prompt(analysis_data, analysis_type)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert PostgreSQL database administrator and consultant with deep knowledge of database optimization, security, and best practices."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            raise RuntimeError(f"Failed to generate analysis with {self.provider}: {e}")
    
    @staticmethod
    def get_supported_providers() -> list:
        """
        Get list of supported cloud providers.
        
        Returns:
            List of provider names
        """
        return ['openai', 'gemini', 'anthropic']
