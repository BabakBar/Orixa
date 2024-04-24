from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from langchain_cohere import ChatCohere


import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

os.environ['COHERE_API_KEY'] = os.getenv("COHERE_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

# Define a prompt template for conversation
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Please respond to the user's query."),
    ("user", "Question:{question}")
])

# Set up the Streamlit interface with a title and input field
st.title('Orixa with Langchain & Cohere')
input_text = st.text_input("Search the topic you want")

# Cohere llm
llm = ChatCohere(model="command-r", temperature=0)
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

if input_text:
    # Send the input text as a HumanMessage and get the response
    messages = [HumanMessage(content=input_text)]
    response = chain.invoke(messages)
    st.write(response)