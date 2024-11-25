"""Main Streamlit application."""
import io
import streamlit as st
import pandas as pd
from core.data_analyzer import DataAnalyzer
from core.config import ANALYSIS_TYPES

# Initialize the analyzer
@st.cache_resource
def get_analyzer():
    return DataAnalyzer()

def main():
    st.title('Orixa: Enhanced Customer Insight 🚀')
    st.markdown("Orixa leverages the power of AI to turn your data into insights.")
    
    analyzer = get_analyzer()
    
    # File upload
    if "df" not in st.session_state:
        csv_file = st.file_uploader("Upload a CSV file to begin", type="csv")
        if csv_file is not None:
            try:
                df = pd.read_csv(csv_file)
                st.session_state["df"] = df
                analyzer.load_data(df)
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
                return
    
    # Main analysis interface
    if "df" in st.session_state:
        with st.expander("🔎 Data Preview"):
            st.dataframe(st.session_state["df"].head())
        
        st.write("Choose an analysis option or ask a question")
        
        # Analysis buttons
        cols = st.columns(2)
        for i, (key, label) in enumerate(ANALYSIS_TYPES.items()):
            col = cols[i % 2]
            with col:
                if st.button(label):
                    with st.spinner("Analyzing..."):
                        result = analyzer.analyze(key)
                        st.write(result)
        
        # Custom question input
        question = st.text_input(
            "Ask a question about your data",
            placeholder="E.g., What is the average sales quantity?"
        )
        if question:
            with st.spinner("Analyzing..."):
                result = analyzer.ask_question(question)
                st.write(result)
        
        # Variable analysis
        st.write("---")
        st.subheader("Variable Analysis")
        variable = st.selectbox("Select a variable to analyze:", analyzer.get_columns())
        if st.button("Analyze Variable"):
            with st.spinner("Analyzing..."):
                result = analyzer.analyze_variable(variable)
                
                # Display line chart
                st.line_chart(result["data"])
                
                # Display analysis
                st.write("#### Summary Statistics")
                st.write(result["summary"])
                st.write("#### Trend Analysis")
                st.write(result["trends"])

if __name__ == "__main__":
    main()
