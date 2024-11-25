"""LLM models configuration for the application."""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from .config import Config

@dataclass
class ModelConfig:
    """Configuration for a LLM model."""
    name: str
    display_name: str
    provider: str
    model_id: str
    temperature: float
    
    def create_instance(self) -> Optional[Any]:
        """
        Create an instance of the LLM model.
        
        Returns:
            LLM instance if API key is available, None otherwise
        
        Raises:
            ValueError: If provider is unknown
        """
        # Check if API key is available
        api_key = Config.get_api_key(self.provider)
        if not api_key:
            raise ValueError(f"API key not configured for {self.display_name}")
        
        # Create appropriate model instance
        try:
            if self.provider == "openai":
                return ChatOpenAI(
                    model=self.model_id,
                    temperature=self.temperature,
                    openai_api_key=api_key
                )
            elif self.provider == "anthropic":
                return ChatAnthropic(
                    model=self.model_id,
                    temperature=self.temperature,
                    anthropic_api_key=api_key,
                    max_tokens=8192  # Add token limit
                )
            elif self.provider == "google":
                return ChatGoogleGenerativeAI(
                    model=self.model_id,
                    temperature=self.temperature,
                    google_api_key=api_key,
                    convert_system_message_to_human=True  # Handle system messages
                )
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
        except Exception as e:
            raise ValueError(f"Error initializing {self.display_name}: {str(e)}")
    
    @property
    def is_available(self) -> bool:
        """Check if the model is available (has API key configured)."""
        return bool(Config.get_api_key(self.provider))
    
    @property
    def supports_functions(self) -> bool:
        """Check if the model supports function calling."""
        return self.provider in ["openai", "google"]

# Available models configuration
AVAILABLE_MODELS: Dict[str, ModelConfig] = {
    "openai": ModelConfig(
        name="openai",
        display_name="OpenAI GPT-4",
        provider="openai",
        model_id="gpt-4o-mini",
        temperature=0.1
    ),
    "anthropic": ModelConfig(
        name="anthropic",
        display_name="Anthropic Claude",
        provider="anthropic",
        model_id="claude-3-5-haiku-20241022",
        temperature=0.1
    ),
    "google": ModelConfig(
        name="google",
        display_name="Google Gemini",
        provider="google",
        model_id="gemini-1.5-flash",
        temperature=0.1
    )
}

def get_available_models() -> Dict[str, ModelConfig]:
    """
    Get dictionary of available models (those with configured API keys).
    
    Returns:
        Dictionary of model names and their configurations
    """
    return {
        name: config
        for name, config in AVAILABLE_MODELS.items()
        if config.is_available
    }

def get_default_model() -> Optional[ModelConfig]:
    """
    Get the first available model configuration.
    
    Returns:
        ModelConfig if any model is available, None otherwise
    """
    available = get_available_models()
    return next(iter(available.values())) if available else None
