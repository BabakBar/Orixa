import io
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

#Define a prompt template for conversation
prompt = ChatPromptTemplate.from_messages([
    ("system", "As a top-tier data scientist, your role is to derive insightful analyses and patterns from various datasets. You're specialized in marketing and sales analytics, your role is to extract actionable insights and identify customer behavior patterns from sales and marketing campaign datasets. Use your expertise to provide recommendations and strategies that would benefit marketing or sales managers. Highlight key trends, predictive analytics, and segmentation analysis. Your responses should be clear, insightful, and in professional data science terminology. Address specific queries with detailed data insights, trend analysis, and predictive outcomes when applicable."),
    ("user", "Question: {question}")
])


# Set up the Streamlit interface with a title and input field
st.title('Orixa with Langchain & OpenAI')
st.header("Talk with your data!")

csv_file = st.file_uploader("Upload a CSV file", type="csv")

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
    
    csv_file.seek(0)
    
    agent = create_csv_agent(
        ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0
        ),
        io.StringIO(file_content.decode('utf-8', errors='ignore')),  # Pass the StringIO object
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )

    question = st.text_input("Ask a question about your data")

    if question is not None and question != "":
        with st.spinner(text="Analyzing..."):
            response = agent.invoke(question)
            st.write(response["output"])