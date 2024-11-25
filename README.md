# Orixa: Enhanced Customer Insight

A data analysis tool that leverages AI to provide insights from your data. This prototype version uses Streamlit for rapid development, with plans to migrate to NextJS in the future.

## Features

- Interactive data analysis with LLM integration
- Multiple analysis types:
  * Data Overview
  * Missing/Duplicate Values Analysis
  * Correlation Analysis
  * Data Summarization
- Custom query support
- Variable-specific analysis with visualization
- Additional modules:
  * Competitor Content Analysis
  * Creative Effectiveness
  * Content Generation
  * Audience Insights

## Project Structure

```
orixa/
├── core/               # Core business logic (will transfer to NextJS)
│   └── analyzer.py    # Data analysis engine
├── app.py             # Main Streamlit application
└── requirements.txt   # Project dependencies
```

The project is structured to separate core business logic from the UI, making future migration to NextJS easier.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a .env file with your API keys:
```
OPENAI_API_KEY=your_key_here
LANGCHAIN_API_KEY=your_key_here
LANGCHAIN_PROJECT=your_project_here
LANGCHAIN_TRACING_V2=true
```

## Running the Application

```bash
streamlit run app.py
```

## Usage

1. Upload your CSV data file using the file uploader
2. Preview your data to ensure it loaded correctly
3. Use the analysis options to gain insights:
   - Get a data overview
   - Check for missing values
   - Analyze correlations
   - View summary statistics
4. Ask specific questions about your data using natural language
5. Analyze specific variables with automatic visualization

## Core Components

### Data Analyzer
The core analysis engine in `core/analyzer.py` provides:
- Data loading and preprocessing
- LLM-powered analysis
- Variable-specific insights
- Custom query handling

## Future Development

This prototype is built with Streamlit for rapid development. The core business logic is separated from the UI to facilitate future migration to NextJS. The `core/` directory contains framework-agnostic code that will be reused in the NextJS version.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
