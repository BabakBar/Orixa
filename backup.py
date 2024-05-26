import io
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

# AI model
llm0 = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0
)

# Define a prompt template for conversation
prompt = ChatPromptTemplate.from_messages([
    ("system", "As a top-tier data scientist, your role is to derive insightful analyses and patterns from various datasets. You're specialized in marketing and sales analytics, your role is to extract actionable insights and identify customer behavior patterns from sales and marketing campaign datasets. Use your expertise to provide recommendations and strategies that would benefit marketing or sales managers. Highlight key trends, predictive analytics, and segmentation analysis. Your responses should be clear, insightful, and in professional data science terminology. Address specific queries with detailed data insights, trend analysis, and predictive outcomes when applicable. Always provide comprehensive explanations about the steps you went through to get to the Final Answer. Please output a paragraph summarizing your findings."),
    ("user", "Question: {question}")
])

# Streamlit UI configuration
st.set_page_config(layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    body {
        background-color: #000000;
        color: #FFFFFF;
        font-family: Arial, sans-serif;
    }
    .main-title {
        text-align: center;
        margin-top: 50px;
        font-size: 2.5em;
        color: #FFFFFF;
    }
    .sub-title {
        text-align: center;
        margin-top: 20px;
        font-size: 1.2em;
        color: #BBBBBB;
    }
    .logo {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 150px;
    }
    .card-container {
        display: flex;
        justify-content: center;
        margin-top: 50px;
        gap: 20px;
    }
    .card {
        background-color: #1A1A1A;
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        transition: transform 0.3s;
        width: 300px;
        height: 200px;
    }
    .card:hover {
        transform: scale(1.05);
    }
    .card-title {
        font-size: 1.2em;
        margin-bottom: 10px;
        color: #FFFFFF;
    }
    .card-content {
        font-size: 1em;
        color: #AAAAAA;
    }
    .chat-section {
        margin-top: 50px;
        text-align: center;
    }
    .chat-input-container {
        display: flex;
        justify-content: center;
    }
    .chat-input {
        width: 60%;
        padding: 10px;
        border-radius: 5px;
        border: 2px solid #4CAF50;
        background-color: #1A1A1A;
        color: #FFFFFF;
        font-size: 1em;
    }
    </style>
""", unsafe_allow_html=True)

# Main Title
st.markdown("<div class='main-title'>ENHANCED CUSTOMER INSIGHT</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>THANK YOU FOR CHECKING IN<br>HOW CAN I HELP YOU?</div>", unsafe_allow_html=True)

# Placeholder for logo
st.markdown("<img src='https://via.placeholder.com/150' alt='Logo' class='logo'>", unsafe_allow_html=True)

# Card Layout
st.markdown("<div class='card-container'>", unsafe_allow_html=True)
card_titles = ["COMPETITOR CONTENT ANALYSIS", "CREATIVE EFFECTIVENESS", "GENERATE CONTENT", "AUDIENCE INSIGHTS"]
card_contents = [
    "Find out trends and competitive whitespaces",
    "Expert review on existing creativity",
    "Co-create content relevant for your target audience",
    "Understand your customers, compare segments and uncover audience opportunities"
]

for i in range(4):
    st.markdown(f"""
        <div class='card'>
            <div class='card-title'>{card_titles[i]}</div>
            <div class='card-content'>{card_contents[i]}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Initialize the 'clicked' key in session state if it doesn't exist
if 'clicked' not in st.session_state:
    st.session_state['clicked'] = False

# Define the function to be called on button click which toggles the 'clicked' state
def toggle_clicked():
    st.session_state['clicked'] = not st.session_state['clicked']

# Button to toggle the state
st.button("Let's get started", on_click=toggle_clicked)

# Show the uploader and subsequent analysis UI only after the button has been clicked
if st.session_state['clicked']:
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
        
        # Display analysis options as buttons with consistent styling
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
                    color: white;
                }
            </style>
            """
        st.markdown(btn_style, unsafe_allow_html=True)
        
        # Display analysis options as buttons in a 2x2 grid layout
        row1_col1, row1_col2 = st.columns(2)
        row2_col1, row2_col2 = st.columns(2)

        button_labels = ["Data Overview", "Missing/Duplicate Values", "Correlation Analysis", "Data Summarization"]
        analysis_types = ['overview', 'missing_values', 'correlation', 'summary']
        columns = [row1_col1, row1_col2, row2_col1, row2_col2]

        # Creating buttons in a loop to reduce redundancy
        for i, col in enumerate(columns):
            with col:
                if st.button(button_labels[i]):
                    st.session_state['analysis_type'] = analysis_types[i]

        # Example of conditionally displaying information based on button click
        if 'analysis_type' in st.session_state:
            if st.session_state['analysis_type'] == 'overview':
                st.write("Displaying data overview...")
            elif st.session_state['analysis_type'] == 'missing_values':
                st.write("Analyzing missing or duplicate values...")
            elif st.session_state['analysis_type'] == 'correlation':
                st.write("Performing correlation analysis...")
            elif st.session_state['analysis_type'] == 'summary':
                st.write("Summarizing data...")

        question = st.text_input("Ask a question about your data", placeholder="E.g., What is the average sales quantity?")

        if question:
            with st.spinner("Analyzing..."):
                response = agent.invoke(question)
                st.write(response["output"])
else:
    st.write("Please click 'Let's get started' to upload your CSV file and begin the analysis.")

# Chat Section
st.markdown("<div class='chat-section'>", unsafe_allow_html=True)
st.markdown("<div class='chat-input-container'>", unsafe_allow_html=True)
user_input = st.text_input("Chat with Orixa...", key="chat_input", placeholder="Type your message here...", label_visibility="hidden")
st.markdown("</div>", unsafe_allow_html=True)

# Handle chat input
if user_input:
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    st.session_state['chat_history'].append(("user", user_input))
    with st.spinner("AI is typing..."):
        agent_response = agent.invoke(user_input)["output"]
    st.session_state['chat_history'].append(("ai", agent_response))
