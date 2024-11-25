"""Streamlit application for data analysis."""
import io
import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from core.analyzer import DataAnalyzer

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(layout="wide")

def render_sidebar():
    """Render the sidebar with navigation."""
    with st.sidebar:
        st.title("Guide")
        st.write("""
        Welcome to Orixa, your intelligent assistant for
        data analysis. Follow these steps to gain insights
        from your data:
        """)
        
        st.markdown("""
        1. Upload your CSV data file.
        2. Preview your data to ensure correctness.
        3. Use the analysis options to start gaining insights.
        4. Ask specific questions about your data.
        """)
        
        st.markdown("---")
        st.markdown("Made by Orixa")

# Custom CSS for dark theme styling
def apply_custom_style():
    st.markdown("""
        <style>
        /* Main container */
        .main {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #FAFAFA;
            padding: 0.5rem 0;
        }
        
        /* Module buttons */
        .module-button {
            background-color: transparent;
            border: 2px solid #4CAF50;
            color: #FAFAFA;
            padding: 15px;
            border-radius: 10px;
            margin: 5px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .module-button:hover {
            background-color: rgba(76, 175, 80, 0.1);
        }
        
        /* Analysis buttons */
        .stButton > button {
            width: 100%;
            background-color: transparent;
            border: 2px solid #4CAF50;
            color: #FAFAFA;
            padding: 10px 24px;
            margin: 5px 0;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .stButton > button:hover {
            background-color: rgba(76, 175, 80, 0.1);
        }
        
        /* Analysis results */
        .analysis-result {
            background-color: #1E1E1E;
            border: 1px solid #333;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
            color: #FAFAFA;
        }
        
        /* Text input */
        .stTextInput > div > div > input {
            background-color: #1E1E1E;
            color: #FAFAFA;
            border: 1px solid #333;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: #1E1E1E;
            color: #FAFAFA;
        }
        
        /* Dataframe */
        .dataframe {
            background-color: #1E1E1E;
            color: #FAFAFA;
        }
        
        /* Remove padding */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        
        /* Section spacing */
        .section-container {
            margin-bottom: 2rem;
        }
        
        /* Spinner */
        .stSpinner > div {
            border-top-color: #4CAF50 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Initialize the analyzer in session state
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = DataAnalyzer()

def main():
    # Apply custom styling
    apply_custom_style()
    
    # Page header
    st.title('Orixa: Enhanced Customer Insight 🚀')
    st.markdown("Orixa leverages the power of AI to turn your data into insights.")
    
    # Render sidebar
    render_sidebar()
    
    # Module selection
    st.markdown("### Choose Module")
    
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    with col1:
        st.markdown('<div class="module-button">Competitor Content Analysis</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="module-button">Creative Effectiveness</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="module-button">Generate Content</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="module-button">Audience Insights</div>', unsafe_allow_html=True)
    
    # Data Analysis Section
    st.markdown("### Data Analysis")
    
    # File upload
    if "df" not in st.session_state:
        csv_file = st.file_uploader("Upload a CSV file to begin", type="csv")
        if csv_file is not None:
            try:
                # Try different encodings
                encodings = ['utf-8', 'ISO-8859-1', 'cp1252']
                df = None
                for encoding in encodings:
                    try:
                        csv_file.seek(0)
                        file_content = csv_file.getvalue()
                        df = pd.read_csv(io.StringIO(file_content.decode(encoding)))
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is None:
                    st.error("Could not read the file with any supported encoding")
                    return
                
                st.session_state.analyzer.load_data(df)
                st.session_state.df = df
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
                return
    
    # Analysis interface
    if hasattr(st.session_state, 'df'):
        with st.expander("🔎 Data Preview"):
            st.dataframe(st.session_state.df.head())
        
        # Analysis Options
        st.markdown("### Analysis Options")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Data Overview"):
                with st.spinner("Analyzing..."):
                    result = st.session_state.analyzer.analyze("overview")
                    st.markdown(f'<div class="analysis-result">{result}</div>', unsafe_allow_html=True)
            
            if st.button("Correlation Analysis"):
                with st.spinner("Analyzing..."):
                    result = st.session_state.analyzer.analyze("correlation")
                    st.markdown(f'<div class="analysis-result">{result}</div>', unsafe_allow_html=True)
        
        with col2:
            if st.button("Missing Values"):
                with st.spinner("Analyzing..."):
                    result = st.session_state.analyzer.analyze("missing_values")
                    st.markdown(f'<div class="analysis-result">{result}</div>', unsafe_allow_html=True)
            
            if st.button("Data Summary"):
                with st.spinner("Analyzing..."):
                    result = st.session_state.analyzer.analyze("summary")
                    st.markdown(f'<div class="analysis-result">{result}</div>', unsafe_allow_html=True)
        
        # Questions
        st.markdown("### Ask Questions")
        question = st.text_input("Ask a question about your data:", placeholder="E.g., What is the average sales quantity?")
        if question:
            with st.spinner("Analyzing..."):
                result = st.session_state.analyzer.ask(question)
                st.markdown(f'<div class="analysis-result">{result}</div>', unsafe_allow_html=True)
        
        # Variable Analysis
        st.markdown("### Variable Analysis")
        variable = st.selectbox("Select a variable to analyze:", st.session_state.df.columns)
        if st.button("Analyze Variable"):
            with st.spinner("Analyzing..."):
                result = st.session_state.analyzer.analyze_variable(variable)
                
                # Show line chart
                st.line_chart(result["data"])
                
                # Show analysis results
                st.markdown("#### Summary Statistics")
                st.markdown(f'<div class="analysis-result">{result["summary"]}</div>', unsafe_allow_html=True)
                st.markdown("#### Trend Analysis")
                st.markdown(f'<div class="analysis-result">{result["trends"]}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
