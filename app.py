"""
Data Analytics Assistant - Streamlit UI
A simple, professional interface for data analysis with AI.
"""

import streamlit as st
import pandas as pd
from io import BytesIO

from src.dataset_handler import load_dataset, DatasetError
from src.dataset_analyzer import DatasetAnalyzer
from src.chat_service import ChatService
from src.config import validate_config


# Page configuration
st.set_page_config(
    page_title="Data Analytics Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background-color: #E8F4FD;
        border-left: 4px solid #1E88E5;
    }
    .assistant-message {
        background-color: #F5F5F5;
        border-left: 4px solid #43A047;
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "df" not in st.session_state:
        st.session_state.df = None
    if "analyzer" not in st.session_state:
        st.session_state.analyzer = None
    if "chat_service" not in st.session_state:
        st.session_state.chat_service = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "api_valid" not in st.session_state:
        try:
            validate_config()
            st.session_state.api_valid = True
        except ValueError:
            st.session_state.api_valid = False


def load_uploaded_file(uploaded_file):
    """Load an uploaded file into a DataFrame."""
    try:
        file_ext = "." + uploaded_file.name.split(".")[-1].lower()
        
        if file_ext == ".csv":
            df = pd.read_csv(uploaded_file)
        elif file_ext in [".xlsx", ".xls"]:
            df = pd.read_excel(uploaded_file)
        elif file_ext == ".json":
            df = pd.read_json(uploaded_file)
        else:
            st.error(f"Unsupported file type: {file_ext}")
            return None
        
        return df
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None


def render_sidebar():
    """Render the sidebar with file upload."""
    with st.sidebar:
        st.markdown("### 📁 Upload Dataset")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["csv", "xlsx", "xls", "json"],
            help="Supported formats: CSV, Excel, JSON"
        )
        
        if uploaded_file is not None:
            if st.button("📤 Load Dataset", type="primary"):
                with st.spinner("Loading dataset..."):
                    df = load_uploaded_file(uploaded_file)
                    if df is not None:
                        st.session_state.df = df
                        st.session_state.analyzer = DatasetAnalyzer(df)
                        if st.session_state.api_valid:
                            st.session_state.chat_service = ChatService(st.session_state.analyzer)
                        st.session_state.messages = []
                        st.success(f"✅ Loaded {len(df):,} rows")
                        st.rerun()
        
        # Show current dataset info
        if st.session_state.df is not None:
            st.markdown("---")
            st.markdown("### 📊 Current Dataset")
            st.info(f"**Rows:** {len(st.session_state.df):,}  \n**Columns:** {len(st.session_state.df.columns)}")
            
            if st.button("🗑️ Clear Dataset"):
                st.session_state.df = None
                st.session_state.analyzer = None
                st.session_state.chat_service = None
                st.session_state.messages = []
                st.rerun()
        
        # API status
        st.markdown("---")
        if st.session_state.api_valid:
            st.success("🔑 API Connected")
        else:
            st.warning("⚠️ API key not configured")


def render_summary():
    """Render the dataset summary section."""
    if st.session_state.analyzer is None:
        return
    
    summary = st.session_state.analyzer.get_summary()
    
    # Metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Rows", f"{summary['row_count']:,}")
    
    with col2:
        st.metric("Total Columns", summary['column_count'])
    
    with col3:
        total_empty = sum(s['total_empty'] for s in summary['empty_data'].values())
        st.metric("Empty Values", f"{total_empty:,}")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Column Info", "📈 Statistics", "🔍 Preview"])
    
    with tab1:
        col_data = []
        for col, dtype in summary['column_types'].items():
            empty_info = summary['empty_data'][col]
            col_data.append({
                "Column": col,
                "Type": dtype,
                "Empty Count": empty_info['total_empty'],
                "Empty %": f"{empty_info['percentage']}%"
            })
        st.dataframe(pd.DataFrame(col_data), use_container_width=True, hide_index=True)
    
    with tab2:
        if summary['basic_stats']:
            stats_df = pd.DataFrame(summary['basic_stats']).T
            st.dataframe(stats_df, use_container_width=True)
        else:
            st.info("No numerical columns found for statistics.")
    
    with tab3:
        st.dataframe(st.session_state.df.head(10), use_container_width=True, hide_index=True)


def render_chat():
    """Render the chat interface."""
    st.markdown("### 💬 Ask Questions About Your Data")
    
    if not st.session_state.api_valid:
        st.warning("Configure your Groq API key in the `.env` file to enable chat.")
        return
    
    if st.session_state.chat_service is None:
        st.info("Upload a dataset to start asking questions.")
        return
    
    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message">🙋 **You:** {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message assistant-message">🤖 **Assistant:** {message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    question = st.chat_input("Ask a question about your dataset...")
    
    if question:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": question})
        
        # Get AI response
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.chat_service.ask(question)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        st.rerun()
    
    # Clear chat button
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            if st.session_state.chat_service:
                st.session_state.chat_service.clear_history()
            st.rerun()


def main():
    """Main application entry point."""
    init_session_state()
    
    # Header
    st.markdown('<p class="main-header">📊 Data Analytics Assistant</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload your dataset, get insights, and ask questions powered by AI</p>', unsafe_allow_html=True)
    
    # Sidebar
    render_sidebar()
    
    # Main content
    if st.session_state.df is not None:
        render_summary()
        st.markdown("---")
        render_chat()
    else:
        # Welcome state
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 15px; margin: 2rem 0;">
            <h2 style="color: #1E3A5F;">👋 Welcome!</h2>
            <p style="color: #666; font-size: 1.1rem;">
                Upload a dataset using the sidebar to get started.<br>
                Supported formats: <strong>CSV</strong>, <strong>Excel</strong>, <strong>JSON</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="padding: 1.5rem; background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 150px;">
                <h4>📤 Upload</h4>
                <p style="color: #666; font-size: 0.9rem;">Drop your CSV, Excel, or JSON file</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="padding: 1.5rem; background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 150px;">
                <h4>📊 Analyze</h4>
                <p style="color: #666; font-size: 0.9rem;">Get instant summary and statistics</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="padding: 1.5rem; background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 150px;">
                <h4>💬 Ask</h4>
                <p style="color: #666; font-size: 0.9rem;">Chat with AI about your data</p>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
