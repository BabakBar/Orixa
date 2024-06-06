import io
import os
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
#from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain.agents.agent_types import AgentType
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

# AI model
llm0 = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0
)

def start_data_analysis():
    if 'analysis_type' not in st.session_state:
        st.session_state['analysis_type'] = None

    csv_file = st.file_uploader("Upload a CSV file to begin", type="csv")

    if csv_file is not None:
        csv_file.seek(0)
        file_content = csv_file.getvalue()
        try:
            df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
        except UnicodeDecodeError:
            df = pd.read_csv(io.StringIO(file_content.decode('ISO-8859-1')))
        except Exception as e:
            st.error(f"An error occurred while processing the CSV file: {e}")
            st.stop()

        with st.expander("🔎 Dataframe Preview"):
            st.write(df.head(5))

        agent = create_pandas_dataframe_agent(
            llm0,
            df,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
        )
        
        st.write("Choose an analysis option:")
        btn_style = """
            <style>
                div.stButton > button {
                    width: 100%;
                    border: 2px solid #4CAF50;
                    border-radius: 10px;
                    background-color: #FFFFFF;
                    color: black;
                    padding: 10px 24px;
                    margin: 0 5px 10px 5px;
                    font-size: 16px;
                    text-align: center;
                    transition: all 0.3s;
                    box-shadow: 2px 5px #888888; 
                }
                
                div.stButton > button:hover {
                    color: dark gray;
                }
            </style>
            """
        st.markdown(btn_style, unsafe_allow_html=True)
        
        row1_col1, row1_col2 = st.columns(2)
        row2_col1, row2_col2 = st.columns(2)

        button_labels = ["Data Overview", "Missing/Duplicate Values", "Correlation Analysis", "Data Summarization"]
        analysis_types = ['overview', 'missing_values', 'correlation', 'summary']
        columns = [row1_col1, row1_col2, row2_col1, row2_col2]

        for i, col in enumerate(columns):
            with col:
                if st.button(button_labels[i]):
                    st.session_state['analysis_type'] = analysis_types[i]
        
        # Function to handle data overview
        def data_overview(df):
            st.write("Displaying data overview...")
            st.write(df.describe())

        # Function to handle missing/duplicate values analysis
        def check_missing_duplicate_values(df):
            st.write("Analyzing missing or duplicate values...")
            st.write(f"Missing Values:\n{df.isnull().sum()}")
            st.write(f"Duplicate Rows:\n{df.duplicated().sum()}")

        # Function to handle correlation analysis
        def correlation_analysis(df):
            st.write("Performing correlation analysis...")
            st.write(df.corr())

        # Function to handle data summarization
        def data_summarization(df):
            st.write("Summarizing data...")
            st.write(df.describe(include='all'))

        # Dispatching analysis based on user selection
        if st.session_state['analysis_type'] is not None:
            if st.session_state['analysis_type'] == 'overview':
                data_overview(df)
            elif st.session_state['analysis_type'] == 'missing_values':
                check_missing_duplicate_values(df)
            elif st.session_state['analysis_type'] == 'correlation':
                correlation_analysis(df)
            elif st.session_state['analysis_type'] == 'summary':
                data_summarization(df)


        question = st.text_input("Ask a question about your data", placeholder="E.g., What is the average sales quantity?")

        if question:
            with st.spinner("Analyzing..."):
                response = agent.invoke(question)
                st.write(response["output"])