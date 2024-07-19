
# import streamlit as st

# def analyze_audience():
#     st.write("Expert review on existing creativity.")
    
import io
import os
import pymongo
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
import streamlit as st
from typing import List, Dict
from langchain.document_loaders import PyPDFLoader, UnstructuredPowerPointLoader
from langchain.document_loaders.image import UnstructuredImageLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

# AI model
llm0 = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)


def start_data_analysis():
    if "analysis_type" not in st.session_state:
        st.session_state["analysis_type"] = None

    # Check if dataframe is already in session state
    if "df" not in st.session_state:
        csv_file = st.file_uploader("Upload a CSV file to begin", type="csv")

        if csv_file is not None:
            csv_file.seek(0)
            file_content = csv_file.getvalue()
            try:
                df = pd.read_csv(io.StringIO(file_content.decode("utf-8")))
            except UnicodeDecodeError:
                df = pd.read_csv(io.StringIO(file_content.decode("ISO-8859-1")))
            except Exception as e:
                st.error(f"An error occurred while processing the CSV file: {e}")
                st.stop()

            st.session_state["df"] = df
    else:
        df = st.session_state["df"]

    if "df" in st.session_state:
        df = st.session_state["df"]
        with st.expander("🔎 Dataframe Preview"):
            st.write(df.head(5))

        agent = create_pandas_dataframe_agent(
            llm0,
            df,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
        )

        st.write("Choose an analysis option to start or directly ask your questions")
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

        button_labels = [
            "Data Overview",
            "Missing/Duplicate Values",
            "Correlation Analysis",
            "Data Summarization",
        ]
        analysis_types = ["overview", "missing_values", "correlation", "summary"]
        columns = [row1_col1, row1_col2, row2_col1, row2_col2]

        for i, col in enumerate(columns):
            with col:
                if st.button(button_labels[i]):
                    st.session_state["analysis_type"] = analysis_types[i]

        # Function to handle analysis and explanations
        @st.cache_data
        def perform_analysis(df, analysis_type):
            if analysis_type == "overview":
                response = agent.invoke(
                    "Provide an overview of the data including number of entries and time range with explanations. use df.info()"
                )
            elif analysis_type == "missing_values":
                response = agent.invoke(
                    "Check for missing or duplicate values and count unique values for each column with explanations."
                )
            elif analysis_type == "correlation":
                response = agent.invoke(
                    "Analyze the correlation between key metrics in the dataset, such as sales and profit with explanations."
                )
            elif analysis_type == "summary":
                response = agent.invoke(
                    "Summarize key metrics in dataset like total sales and profit, average discount rate, and sales by region. Provide summary statistics for numerical columns with explanations. use  df.describe()"
                )
            return response["output"]

        # Dispatching analysis based on user selection
        if st.session_state["analysis_type"] is not None:
            with st.spinner("Analyzing..."):
                analysis_result = perform_analysis(
                    df, st.session_state["analysis_type"]
                )
                st.write(analysis_result)
        
        question = st.text_input(
            "Ask a question about your data",
            placeholder="E.g., What is the average sales quantity?",
        )

        if question:
            with st.spinner("Analyzing..."):
                response = agent.invoke(question)
                st.write(response["output"])
        
        # Variable selection dropdown
        user_question_variable = st.selectbox('Select a variable for Visualization:', df.columns)
        if user_question_variable:
            if st.button("Analyze Variable"):
                function_question_variable(_agent=agent, df=df, user_question_variable=user_question_variable)

def function_question_variable(_agent, df, user_question_variable):
    st.line_chart(df, y=[user_question_variable])
    
    summary_statistics = _agent.invoke(f"Provide a simple summary statistics for {user_question_variable}.")
    st.write("#### Summary Statistics")
    st.write(summary_statistics["output"])
    
    # Analyze trends, seasonality, and cyclic patterns
    trends = _agent.invoke(f"Examine {user_question_variable} for any observable trends, seasonality, and cyclic patterns. Provide insights on these patterns.")
    st.write("#### Trend Analysis")
    st.write(trends["output"])
