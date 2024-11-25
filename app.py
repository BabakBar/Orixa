"""Streamlit application for Google Analytics 4 data analysis."""
import io
import streamlit as st
import pandas as pd
from core.analyzer import DataAnalyzer
from core.models import AVAILABLE_MODELS
from core.config import Config

# Setup environment
Config.setup_environment()

# Get available models
AVAILABLE_MODEL_STATUS = Config.get_available_models()

# Configure page
st.set_page_config(layout="wide")

def render_sidebar():
    """Render the sidebar with GA4 guidance and model selection."""
    with st.sidebar:
        st.title("GA4 Analysis Guide")
        
        # Model Selection
        st.markdown("### 🤖 Model Selection")
        
        # Filter available models
        available_models = {
            name: model.name
            for name, model in AVAILABLE_MODELS.items()
            if AVAILABLE_MODEL_STATUS.get(model.display_name, False)
        }
        
        if not available_models:
            st.error("⚠️ No AI models available. Please check your API keys.")
            st.stop()
        
        model_options = {
            AVAILABLE_MODELS[model_name].display_name: model_name 
            for model_name in available_models
        }
        
        selected_display_name = st.selectbox(
            "Choose AI Model:",
            options=list(model_options.keys()),
            index=0
        )
        
        selected_model = model_options[selected_display_name]
        
        # Update model if changed
        if 'current_model' not in st.session_state or st.session_state.current_model != selected_model:
            st.session_state.current_model = selected_model
            if 'analyzer' in st.session_state:
                st.session_state.analyzer.switch_model(selected_model)
                st.rerun()
        
        # Show model info
        model_config = AVAILABLE_MODELS[selected_model]
        st.markdown("#### Model Details")
        st.markdown(f"""
        - Provider: {model_config.provider.title()}
        - Model: {model_config.model_id}
        """)
        
        st.markdown("---")
        
        st.markdown("### 📊 Quick Start")
        st.markdown("""
        1. Choose your preferred AI model above
        2. Upload your GA4 data
        3. Click 'Analyze Data'
        4. Get instant insights
        """)
        
        st.markdown("### ❓ Need Help?")
        st.markdown("""
        You can ask specific questions about your data using the
        question box below the analysis.
        
        Try different AI models to compare insights!
        """)

def main():
    # Page header
    st.title('Orixa: GA4 Data Analysis Platform 🚀')
    st.markdown("Get instant insights from your Google Analytics 4 data.")
    
    # Initialize session state
    if 'current_model' not in st.session_state:
        # Get first available model
        available_model = next(
            (name for name, available in AVAILABLE_MODEL_STATUS.items() if available),
            None
        )
        if not available_model:
            st.error("⚠️ No AI models available. Please configure at least one API key.")
            st.stop()
            
        st.session_state.current_model = next(
            name for name, model in AVAILABLE_MODELS.items()
            if model.display_name == available_model
        )
    
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = DataAnalyzer(st.session_state.current_model)
        st.session_state.analysis_complete = False
    
    # Render sidebar
    render_sidebar()
    
    # Data Upload Section
    uploaded_file = st.file_uploader("Upload your GA4 data (CSV)", type="csv")
    
    if uploaded_file is not None:
        try:
            # Create a loading placeholder
            with st.status("Processing data...", expanded=True) as status:
                # Read CSV file
                df = pd.read_csv(uploaded_file)
                status.update(label="Loading data...", state="running")
                
                try:
                    # Load and process data
                    st.session_state.analyzer.load_data(df)
                    st.session_state.df = df
                    status.update(label="✅ Data loaded successfully!", state="complete")
                    st.session_state.analysis_complete = True
                    
                except ValueError as e:
                    status.update(label=f"❌ Error: {str(e)}", state="error")
                    st.stop()
                    
        except Exception as e:
            st.error("❌ Error reading file. Please ensure you've uploaded a valid GA4 data export.")
            st.stop()
    
    # Only show analysis section if data is loaded and processed
    if hasattr(st.session_state, 'analysis_complete') and st.session_state.analysis_complete:
        st.markdown("---")
        
        # Show current model
        current_model = AVAILABLE_MODELS[st.session_state.current_model]
        st.info(f"🤖 Currently using: {current_model.display_name}")
        
        # Analysis section with tabs
        tab1, tab2 = st.tabs(["📊 Key Insights", "❓ Ask Questions"])
        
        with tab1:
            if st.button("Analyze Data", type="primary"):
                with st.spinner(f"Generating insights using {current_model.display_name}..."):
                    try:
                        result = st.session_state.analyzer.analyze("overview")
                        
                        # Display results in a clean format
                        st.markdown("### 📈 Analysis Results")
                        st.markdown(result)
                        
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {str(e)}")
        
        with tab2:
            st.markdown("### Ask Specific Questions")
            st.markdown("""
            Examples:
            - What are the top converting pages?
            - Which traffic sources have the highest engagement?
            - What's the most common user journey?
            """)
            
            question = st.text_input("Your question:")
            if question:
                with st.spinner(f"Finding answers using {current_model.display_name}..."):
                    try:
                        result = st.session_state.analyzer.ask(question)
                        st.markdown("### 💡 Answer")
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"❌ Error processing question: {str(e)}")

if __name__ == "__main__":
    main()
