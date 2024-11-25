"""Configuration management for the application."""
import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration management."""
    
    @staticmethod
    def get_api_key(provider: str) -> Optional[str]:
        """
        Get API key for specified provider.
        
        Args:
            provider: The provider name (openai, anthropic, or google)
            
        Returns:
            API key if available, None otherwise
        """
        key_mapping = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY"
        }
        
        env_var = key_mapping.get(provider)
        if not env_var:
            return None
            
        return os.getenv(env_var)
    
    @staticmethod
    def validate_api_keys() -> Dict[str, bool]:
        """
        Check which API keys are available.
        
        Returns:
            Dictionary of provider names and their availability status
        """
        providers = ["openai", "anthropic", "google"]
        return {
            provider: bool(Config.get_api_key(provider))
            for provider in providers
        }
    
    @staticmethod
    def setup_environment() -> None:
        """Setup required environment variables."""
        # Set up LangChain environment
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
        os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "default")
        
        # Set up provider API keys
        api_keys = Config.validate_api_keys()
        
        # Set OpenAI API key if available
        if api_keys["openai"]:
            os.environ["OPENAI_API_KEY"] = Config.get_api_key("openai")
        
        # Set Anthropic API key if available
        if api_keys["anthropic"]:
            os.environ["ANTHROPIC_API_KEY"] = Config.get_api_key("anthropic")
        
        # Set Google API key if available
        if api_keys["google"]:
            os.environ["GOOGLE_API_KEY"] = Config.get_api_key("google")
    
    @staticmethod
    def get_available_models() -> Dict[str, bool]:
        """
        Get available models based on API keys.
        
        Returns:
            Dictionary of model names and their availability
        """
        api_keys = Config.validate_api_keys()
        
        return {
            "OpenAI GPT-4": api_keys["openai"],
            "Anthropic Claude": api_keys["anthropic"],
            "Google Gemini": api_keys["google"]
        }
