"""Core data analysis functionality."""
import os
from typing import Optional, Dict, Any
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set environment variables for LangChain
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

class DataAnalyzer:
    """Handles data analysis with LLM integration."""
    
    def __init__(self):
        """Initialize the analyzer with LLM."""
        self.df: Optional[pd.DataFrame] = None
        self.agent = None
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1
        )
    
    def load_data(self, df: pd.DataFrame) -> None:
        """Load data and initialize agent."""
        self.df = df
        self.agent = create_pandas_dataframe_agent(
            self.llm,
            self.df,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            allow_dangerous_code=True
        )
    
    def analyze(self, analysis_type: str) -> str:
        """Run predefined analysis types."""
        if not self.agent:
            raise ValueError("No data loaded")
            
        prompts = {
            "overview": (
                "Provide an overview of the data including number of entries and "
                "time range with explanations. use df.info()"
            ),
            "missing_values": (
                "Check for missing or duplicate values and count unique values "
                "for each column with explanations."
            ),
            "correlation": (
                "Analyze the correlation between key metrics in the dataset, "
                "such as sales and profit with explanations."
            ),
            "summary": (
                "Summarize key metrics in dataset like total sales and profit, "
                "average discount rate, and sales by region. Provide summary "
                "statistics for numerical columns with explanations. use df.describe()"
            )
        }
        
        if analysis_type not in prompts:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
            
        response = self.agent.invoke(prompts[analysis_type])
        return response["output"]
    
    def ask(self, question: str) -> str:
        """Ask a custom question about the data."""
        if not self.agent:
            raise ValueError("No data loaded")
            
        response = self.agent.invoke(question)
        return response["output"]
    
    def analyze_variable(self, variable: str) -> Dict[str, Any]:
        """Analyze a specific variable."""
        if not self.agent or variable not in self.df.columns:
            raise ValueError("Invalid variable or no data loaded")
            
        # Get summary statistics
        summary = self.agent.invoke(
            f"Provide a simple summary statistics for {variable}."
        )
        
        # Analyze trends
        trends = self.agent.invoke(
            f"Examine {variable} for any observable trends, seasonality, "
            "and cyclic patterns. Provide insights on these patterns."
        )
        
        return {
            "data": self.df[variable].tolist(),
            "summary": summary["output"],
            "trends": trends["output"]
        }
