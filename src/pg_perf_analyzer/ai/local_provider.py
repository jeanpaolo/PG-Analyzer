"""Local AI provider using Ollama for offline analysis."""

from typing import Dict, Any, Optional
from .ai_provider import AIProvider

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class LocalAIProvider(AIProvider):
    """AI provider using local Ollama models."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize local AI provider.
        
        Args:
            config: Configuration with keys:
                - model: Model name (default: llama2)
                - host: Ollama host (default: http://localhost:11434)
                - temperature: Generation temperature (default: 0.7)
                - max_tokens: Maximum tokens to generate (default: 2000)
        """
        super().__init__(config)
        self.model = self.config.get('model', 'llama2')
        self.host = self.config.get('host', 'http://localhost:11434')
        self.temperature = self.config.get('temperature', 0.7)
        self.max_tokens = self.config.get('max_tokens', 2000)
        
        if OLLAMA_AVAILABLE:
            self.client = ollama.Client(host=self.host)
        else:
            self.client = None
    
    def get_provider_name(self) -> str:
        return f"Local Ollama ({self.model})"
    
    def is_available(self) -> bool:
        """Check if Ollama is available and the model is accessible."""
        if not OLLAMA_AVAILABLE:
            return False
        
        try:
            # Try to list models to verify connection
            self.client.list()
            return True
        except Exception:
            return False
    
    def analyze(self, analysis_data: Dict[str, Any], analysis_type: str) -> str:
        """
        Analyze database data using local Ollama model.
        
        Args:
            analysis_data: Dictionary containing analysis results
            analysis_type: Type of analysis (structure, security, performance)
            
        Returns:
            Analysis report as string
        """
        if not self.is_available():
            raise RuntimeError(
                "Ollama is not available. Please install Ollama and ensure it's running.\n"
                "Visit https://ollama.ai for installation instructions."
            )
        
        prompt = self._build_prompt(analysis_data, analysis_type)
        
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': self.temperature,
                    'num_predict': self.max_tokens,
                }
            )
            
            return response['response']
        
        except Exception as e:
            raise RuntimeError(f"Failed to generate analysis with Ollama: {e}")
    
    def list_available_models(self) -> list:
        """
        List available Ollama models.
        
        Returns:
            List of model names
        """
        if not self.is_available():
            return []
        
        try:
            models = self.client.list()
            return [model['name'] for model in models.get('models', [])]
        except Exception:
            return []
