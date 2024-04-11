import requests
import streamlit as st

def get_openai_response(input_text):
    response=requests.post("http://localhost:8000/campaign/invoke",
    json={'input':{'topic':input_text}})

    print(response.json())
    return response.json().get('output', {}).get('content', 'No content')

    ## streamlit framework

st.title('Langchain With OpenAI API')
input_text=st.text_input("Write an abstract on")

if input_text:
    st.write(get_openai_response(input_text))
