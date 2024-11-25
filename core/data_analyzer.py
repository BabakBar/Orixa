"""Core data analysis functionality, independent of UI framework."""
from typing import Dict, Any, Optional, List
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

class DataAnalyzer:
    """Handles data analysis operations using LLM."""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.1):
        """Initialize the analyzer with LLM settings."""
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.df: Optional[pd.DataFrame] = None
        self.agent = None
    
    def load_data(self, data: pd.DataFrame) -> None:
        """Load data and initialize the agent."""
        self.df = data
        self.agent = create_pandas_dataframe_agent(
            self.llm,
            self.df,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            allow_dangerous_code=True
        )
    
    def get_data_preview(self, rows: int = 5) -> Dict:
        """Get a preview of the loaded data."""
        if self.df is None:
            raise ValueError("No data loaded")
        return self.df.head(rows).to_dict()
    
    def analyze(self, analysis_type: str) -> str:
        """Perform specified type of analysis."""
        if self.agent is None:
            raise ValueError("No data loaded")
            
        prompts = {
            "overview": "Provide an overview of the data including number of entries and time range with explanations. use df.info()",
            "missing_values": "Check for missing or duplicate values and count unique values for each column with explanations.",
            "correlation": "Analyze the correlation between key metrics in the dataset, such as sales and profit with explanations.",
            "summary": "Summarize key metrics in dataset like total sales and profit, average discount rate, and sales by region. Provide summary statistics for numerical columns with explanations. use df.describe()"
        }
        
        if analysis_type not in prompts:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
            
        response = self.agent.invoke(prompts[analysis_type])
        return response["output"]
    
    def ask_question(self, question: str) -> str:
        """Ask a custom question about the data."""
        if self.agent is None:
            raise ValueError("No data loaded")
            
        response = self.agent.invoke(question)
        return response["output"]
    
    def analyze_variable(self, variable: str) -> Dict[str, Any]:
        """Analyze a specific variable."""
        if self.agent is None:
            raise ValueError("No data loaded")
        if variable not in self.df.columns:
            raise ValueError(f"Variable {variable} not found in dataset")
            
        summary = self.agent.invoke(f"Provide a simple summary statistics for {variable}.")
        trends = self.agent.invoke(
            f"Examine {variable} for any observable trends, seasonality, "
            "and cyclic patterns. Provide insights on these patterns."
        )
        
        return {
            "data": self.df[variable].tolist(),
            "summary": summary["output"],
            "trends": trends["output"]
        }
    
    def get_columns(self) -> List[str]:
        """Get list of available columns."""
        if self.df is None:
            raise ValueError("No data loaded")
        return self.df.columns.tolist()
