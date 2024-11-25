"""Configuration settings."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")

# LLM Settings
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.1

# Analysis Types
ANALYSIS_TYPES = {
    "overview": "Data Overview",
    "missing_values": "Missing/Duplicate Values",
    "correlation": "Correlation Analysis",
    "summary": "Data Summarization"
}
