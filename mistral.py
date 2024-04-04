from langchain_mistralai.chat_models import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage

import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY")

# prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Please respond to the user's query."),
    ("user", "Question:{question}")
])

# title and input field
st.title('Chatbot with Langchain & Mistral')
input_text = st.text_input("Type your question here")

# Mistral model
mistral_llm = ChatMistralAI(mistral_api_key=os.getenv("MISTRAL_API_KEY"))
output_parser = StrOutputParser()
chain = prompt | mistral_llm | output_parser

if input_text:
    # Send the input text as a HumanMessage and get the response
    messages = [HumanMessage(content=input_text)]
    response = chain.invoke(messages)
    st.write(response)
