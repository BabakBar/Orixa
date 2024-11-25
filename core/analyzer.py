"""Core data analysis functionality for Google Analytics data."""
import os
from typing import Optional, Dict, Any
import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from .preprocessor import GA4Preprocessor
from .models import AVAILABLE_MODELS, get_default_model, get_available_models
from .config import Config

class DataAnalyzer:
    """Handles Google Analytics data analysis with LLM integration."""
    
    def __init__(self, model_name: Optional[str] = None):
        """Initialize the analyzer with specified LLM model."""
        self.df: Optional[pd.DataFrame] = None
        self.raw_df: Optional[pd.DataFrame] = None
        self.agent = None
        
        # Get available models
        available_models = get_available_models()
        if not available_models:
            raise ValueError(
                "No AI models available. Please configure at least one API key "
                "(OpenAI, Anthropic, or Google)"
            )
        
        # Set initial model
        if model_name is None:
            self.model_config = get_default_model()
            if self.model_config is None:
                raise ValueError("No AI models available")
        else:
            if model_name not in AVAILABLE_MODELS:
                raise ValueError(f"Unknown model: {model_name}")
            self.model_config = AVAILABLE_MODELS[model_name]
            if not self.model_config.is_available:
                raise ValueError(
                    f"Model {self.model_config.display_name} is not available. "
                    "Please configure the API key."
                )
        
        self.current_model_name = self.model_config.name
        try:
            self.llm = self.model_config.create_instance()
        except Exception as e:
            raise ValueError(f"Error initializing {self.model_config.display_name}: {str(e)}")
    
    def switch_model(self, model_name: str) -> None:
        """Switch to a different LLM model."""
        if model_name not in AVAILABLE_MODELS:
            raise ValueError(f"Unknown model: {model_name}")
            
        model_config = AVAILABLE_MODELS[model_name]
        if not model_config.is_available:
            raise ValueError(
                f"Model {model_config.display_name} is not available. "
                "Please configure the API key."
            )
        
        try:
            self.current_model_name = model_name
            self.model_config = model_config
            self.llm = self.model_config.create_instance()
            
            # Recreate agent if data is loaded
            if self.df is not None:
                if self.model_config.supports_functions:
                    self.agent = create_pandas_dataframe_agent(
                        self.llm,
                        self.df,
                        verbose=True,
                        agent_type=AgentType.OPENAI_FUNCTIONS,
                        allow_dangerous_code=True
                    )
                else:
                    # For models that don't support function calling (like Claude),
                    # we'll use direct prompting
                    self.agent = self.llm
        except Exception as e:
            raise ValueError(f"Error switching to {model_config.display_name}: {str(e)}")
    
    def validate_ga4_data(self, df: pd.DataFrame) -> bool:
        """Validate that the DataFrame contains minimum required GA4 fields."""
        required_fields = [
            'event_date',
            'event_name',
            'event_timestamp'
        ]
        
        return all(field in df.columns for field in required_fields)
    
    def load_data(self, df: pd.DataFrame) -> None:
        """Load and preprocess GA4 data."""
        if not self.validate_ga4_data(df):
            raise ValueError(
                "Invalid GA4 data format. Please ensure your export includes: "
                "event_date, event_name, and event_timestamp"
            )
        
        try:
            self.raw_df = df
            self.df = GA4Preprocessor.preprocess_ga4_data(df)
            
            if self.model_config.supports_functions:
                self.agent = create_pandas_dataframe_agent(
                    self.llm,
                    self.df,
                    verbose=True,
                    agent_type=AgentType.OPENAI_FUNCTIONS,
                    allow_dangerous_code=True
                )
            else:
                self.agent = self.llm
        except Exception as e:
            raise ValueError(f"Error processing data: {str(e)}")
    
    def get_data_summary(self) -> str:
        """Get a basic summary of the data for non-function models."""
        if self.df is None:
            return ""
            
        total_events = len(self.df)
        date_range = f"{self.df['event_date'].min()} to {self.df['event_date'].max()}"
        event_types = self.df['event_name'].value_counts().to_dict()
        
        summary = (
            f"Data Summary:\n"
            f"- Total Events: {total_events}\n"
            f"- Date Range: {date_range}\n"
            f"- Event Types: {event_types}\n"
        )
        return summary
    
    def analyze(self, analysis_type: str) -> str:
        """Run predefined GA4 analysis types."""
        if not self.agent:
            raise ValueError("No data loaded. Please upload your GA4 data first.")
            
        base_prompt = """
            Analyze this Google Analytics 4 data and provide insights in the following format:

            ### 📊 Overview
            {One-sentence summary of data period and total events}

            ### 🎯 Key Metrics
            - Total Events: {number}
            - Date Range: {date range}
            - Unique Users: {number if available}

            ### 📈 Event Analysis
            {List top event types with percentages}

            ### 🌐 Top Pages
            {List most viewed pages with view counts}

            ### 💡 Key Insights
            - {Key insight 1}
            - {Key insight 2}
            - {Key insight 3}

            ### 📱 Device & Location
            {Brief device and location summary}

            Keep the response concise and marketing-friendly.
            Focus on actionable insights.
        """
        
        try:
            if self.model_config.supports_functions:
                response = self.agent.invoke(base_prompt)
                return response["output"]
            else:
                # For non-function models, provide data summary in prompt
                enhanced_prompt = f"""
                    {base_prompt}
                    
                    Here's the data summary to analyze:
                    {self.get_data_summary()}
                """
                response = self.agent.invoke(enhanced_prompt)
                return response.content
                
        except Exception as e:
            raise ValueError(f"Error during analysis: {str(e)}")
    
    def ask(self, question: str) -> str:
        """Ask a custom question about GA4 data."""
        if not self.agent:
            raise ValueError("No data loaded. Please upload your GA4 data first.")
            
        base_prompt = f"""
        Analyze the GA4 data to answer: "{question}"
        
        Format your response like this:
        
        ### 💡 Answer
        {{Clear, concise answer}}
        
        ### 📊 Supporting Data
        {{Key metrics and numbers}}
        
        ### 🎯 Recommendation
        {{Brief, actionable recommendation}}
        
        Keep the response marketing-friendly and focused on business insights.
        Be concise and clear.
        """
        
        try:
            if self.model_config.supports_functions:
                response = self.agent.invoke(base_prompt)
                return response["output"]
            else:
                # For non-function models, provide data summary in prompt
                enhanced_prompt = f"""
                    {base_prompt}
                    
                    Here's the data summary to help answer the question:
                    {self.get_data_summary()}
                """
                response = self.agent.invoke(enhanced_prompt)
                return response.content
                
        except Exception as e:
            raise ValueError(f"Error processing question: {str(e)}")
    
    @property
    def current_model(self) -> str:
        """Get the current model name."""
        return self.current_model_name
