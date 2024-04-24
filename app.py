import io
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
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

#Define a prompt template for conversation
prompt = ChatPromptTemplate.from_messages([
    ("system", "As a top-tier data scientist, your role is to derive insightful analyses and patterns from various datasets. You're specialized in marketing and sales analytics, your role is to extract actionable insights and identify customer behavior patterns from sales and marketing campaign datasets. Use your expertise to provide recommendations and strategies that would benefit marketing or sales managers. Highlight key trends, predictive analytics, and segmentation analysis. Your responses should be clear, insightful, and in professional data science terminology. Address specific queries with detailed data insights, trend analysis, and predictive outcomes when applicable. Always provide comprehensive explanations about the steps you went through to get to the Final Answer. Please output a paragraph summurizing you findings"),
    ("user", "Question: {question}")
])


# Streamlit UI
st.title('Orixa: AI-Driven Data Insights 🚀')
st.markdown("""
    ## Talk with your data!
    Orixa leverages the power of AI to turn your data into insights. 
""")

with st.sidebar:
    st.write("Guide")
    st.caption(
    """
    Welcome to Orixa, your intelligent assistant for data analysis. Follow these steps to gain insights from your data:

    1. Upload your CSV data file.
    2. Preview your data to ensure correctness.
    3. Ask any question related to your data in the input box.
    4. Get instant answers an d insights powered by AI.
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
            #io.StringIO(file_content.decode('utf-8', errors='ignore')),
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
        )

        question = st.text_input("Ask a question about your data", placeholder="E.g., What is the average sales quantity?")

        if question:
            with st.spinner("Analyzing..."):
                response = agent.invoke(question)
                #st.success("Analysis complete!")
                st.write(response["output"])
                         
else:
    st.write("Please click 'Let's get started' to upload your CSV file and begin the analysis.")