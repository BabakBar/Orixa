from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
import pandas as pd

import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

# Define a prompt template for conversation
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a professional data scientist. Please respond to the user's query about the dataset."),
    ("user", "Question:{question}")
])

# Set up the Streamlit interface with a title and input field
st.title('Orixa with Langchain & OpenAI')
st.header("Talk with your data!")

csv_file = st.file_uploader("Upload a CSV file", type="csv")
input_text = st.text_input("Ask questions about your data")

if csv_file is not None:
    agent = create_csv_agent(
        ChatOpenAI(
            model="gpt-3.5-turbo"
        ),
        csv_file,
        verbose = True,
        
    )
# ZERO_SHOT_REACT_DESCRIPTION: A zero-shot agent that performs a reasoning step before taking action.
# openai llm
llm = ChatOpenAI(model="gpt-3.5-turbo")
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

if input_text:
    response = chain.invoke({'question': input_text})
    st.write(response)