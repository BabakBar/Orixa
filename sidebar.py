import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.write("Guide")
        st.caption("""
        Welcome to Orixa, your intelligent assistant for data analysis. Follow these steps to gain insights from your data:

        1. Upload your CSV data file.
        2. Preview your data to ensure correctness.
        3. Use the analysis options to start gaining insights.
        4. Ask specific questions about your data.
        """)
            
        st.divider()
        st.caption("<p style='text-align: center;'>Made by <a href='https://orixainsights.com/' target='_blank'><strong>Orixa</strong></a></p>", unsafe_allow_html=True)
        
        with st.expander("What are the steps of EDA?"):
            st.markdown("""
            - **Data Cleaning:** Examining the data for missing values, inconsistencies, handling missing data, and identifying outliers.
            - **Data Profiling:** Review data types, count of unique values, and statistics to understand distributions.
            - **Data Exploring:** Use summary statistics and visualization tools to understand the data and find patterns.
            - **Correlation Analysis:** Check for relationships between variables, using statistics and visualizations.
            - **Data Visualization:** Create various plots to understand the data's story and insights.
            """, unsafe_allow_html=True)
