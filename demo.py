import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import streamlit as st
from sidebar import render_sidebar
from competitor_analysis import analyze_competitors
from creative_effectiveness import analyze_creativity
from generate_content import generate_content
from audience_insights import analyze_audience
from data_analysis import start_data_analysis
from dotenv import load_dotenv
load_dotenv()

# Set the page configuration to use the full width layout
#st.set_page_config(layout="wide")

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

# AI model
llm0 = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0
)

#Define a prompt template for conversation
prompt = ChatPromptTemplate.from_messages([
    ("system", "As a top-tier data scientist, your role is to derive insightful analyses and patterns from various datasets. You're specialized in marketing and sales analytics, your role is to extract actionable insights and identify customer behavior patterns from sales and marketing campaign datasets. Use your expertise to provide recommendations and strategies that would benefit marketing or sales managers. Highlight key trends, predictive analytics, and segmentation analysis. Your responses should be clear, insightful, and in professional data science terminology. Address specific queries with detailed data insights, trend analysis, and predictive outcomes when applicable. Always provide comprehensive explanations about the steps you went through to get to the Final Answer. Please output a paragraph summurizing you findings"),
    ("user", "Question: {question}")
])


# Streamlit UI
st.title('Orixa: Enhanced Customer Insight 🚀')
st.markdown("""
    Orixa leverages the power of AI to turn your data into insights. 
""")

#render sidebar
render_sidebar()


# Initialize the 'clicked' key in session state if it doesn't exist
if 'clicked' not in st.session_state:
    st.session_state['clicked'] = False

def set_clicked(index):
    st.session_state['clicked'] = index

# Custom CSS for button styling
btn_style = """
    <style>
        .card-btn-container {
            display: flex;
            justify-content: space-around;
            align-items: center;
            gap: 20px;
            margin: 20px 0;
            width: 100%;
        }
        .card-btn {
            display: inline-block;
            width: 200px;
            height: 150px;
            border: 2px solid #8A2BE2;
            border-radius: 10px;
            background-color: #FFFFFF;
            color: black;
            padding: 20px;
            font-size: 16px;
            text-align: center;
            transition: all 0.3s;
            box-shadow: 2px 5px #888888;
            text-decoration: none;
            cursor: pointer;
        }
        
        .card-btn:hover {
            color: white;
            background-color: #4CAF50;
        }
        
        .card-btn.clicked {
            background-color: #4CAF50;
            color: white;
        }
    </style>
    """
st.markdown(btn_style, unsafe_allow_html=True)

# Card titles and contents
card_titles = ["Competetitor Content Analysis", "Creative Effectiveness", "Generate Content", "Audience Insights"]
card_functions = [analyze_competitors, analyze_creativity, generate_content, analyze_audience]
card_contents = [
    "Find out trends and competitive whitespaces",
    "Expert review on existing creativity",
    "Co-create content relevant for your target audience",
    "Understand your customers, compare segments and uncover audience opportunities"
]

# Initialize session state for clicked buttons
if 'clicked' not in st.session_state:
    st.session_state['clicked'] = None

def set_clicked(index):  # noqa: F811
    st.session_state['clicked'] = index

# Display cards as buttons in a 2x2 grid layout
cols = st.columns(2)

for i, title in enumerate(card_titles):
    col = cols[i % 2]
    with col:
        if st.button(title, key=f'button_{i}'):
            set_clicked(i)

# Add the Start Data Analysis button separately
if st.button("Start Data Analysis"):
    set_clicked(len(card_titles))  # Use a special index to indicate data analysis

# Check the clicked state and call the corresponding function
if st.session_state['clicked'] is not None:
    if st.session_state['clicked'] < len(card_titles):
        function_to_call = card_functions[st.session_state['clicked']]
        result = function_to_call()
        if result is not None:
            st.write(result)
    elif st.session_state['clicked'] == len(card_titles):
        start_data_analysis()
else:
    st.write("Please click 'Start Data Analysis' to upload your CSV file and begin the analysis.")