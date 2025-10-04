"""
Streamlit Web Interface for Bangladesh Constitution Chatbot
Provides user-friendly web interface with bilingual support
"""
import os
import sys
import streamlit as st
import json
import warnings
from datetime import datetime, timedelta
import time

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import Config
from src.chatbot import ConstitutionChatbot

# Page configuration
st.set_page_config(
    page_title="Bangladesh Constitution Chatbot",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #374151;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        border-left: 4px solid #1e3a8a;
        background-color: #f8fafc;
    }
    .user-message {
        background-color: #dbeafe;
        border-left-color: #3b82f6;
    }
    .bot-message {
        background-color: #f0f9ff;
        border-left-color: #0ea5e9;
    }
    .stats-card {
        background-color: #f1f5f9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .disclaimer {
        background-color: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_chatbot():
    """Initialize and cache the chatbot instance"""
    try:
        config = Config()
        chatbot = ConstitutionChatbot(config)
        if chatbot.is_ready():
            return chatbot
        else:
            st.warning("⚠️ Chatbot initialization incomplete - some features may not work")
            return chatbot  # Return even if not fully ready, fallbacks will handle it
    except Exception as e:
        st.error(f"Error initializing chatbot: {e}")
        return None


def check_llm_status(chatbot):
    """Check and display current LLM status with fallback info"""
    if not chatbot or not chatbot.rag_system:
        return {"status": "error", "message": "Chatbot not initialized"}
    
    try:
        llm_service = chatbot.rag_system.llm_service
        model_info = llm_service.get_model_info()
        
        # Test connectivity if needed
        connectivity = model_info.get('connectivity_status', {})
        
        return {
            "status": "ready" if model_info['is_loaded'] else "fallback",
            "llm_type": model_info.get('llm_type', 'unknown'),
            "connectivity": connectivity,
            "model_name": model_info.get('model_name', 'unknown'),
            "fallback_available": model_info.get('local_model_available', False)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def display_conversation_history(chatbot):
    """Display conversation history in sidebar"""
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    history = chatbot.get_conversation_history(10)
    
    if history:
        st.sidebar.subheader("📜 Recent Conversations")
        for i, conv in enumerate(reversed(history[-5:]), 1):
            with st.sidebar.expander(f"Q{i}: {conv['query'][:30]}..."):
                st.write(f"**Question:** {conv['query']}")
                st.write(f"**Sources:** {conv['sources']}")
                st.write(f"**Language:** {conv['language']}")
                st.write(f"**Time:** {conv['timestamp'].strftime('%H:%M:%S')}")


def display_system_stats(chatbot):
    """Display system statistics in sidebar"""
    if not chatbot:
        st.sidebar.error("❌ System Not Ready")
        return
        
    stats = chatbot.get_session_stats()
    llm_status = check_llm_status(chatbot)
    
    st.sidebar.subheader("📊 System Status")
    
    # LLM Status with real-time connectivity
    connectivity = llm_status.get('connectivity', {})
    if llm_status["status"] == "ready":
        if connectivity.get('status') == 'success':
            st.sidebar.success(f"✅ {llm_status['llm_type'].title()} Model Active")
        else:
            st.sidebar.warning(f"⚠️ {llm_status['llm_type'].title()} Model (Connectivity Issues)")
    elif llm_status["status"] == "fallback":
        st.sidebar.warning("⚠️ Using Fallback Mode")
        if llm_status.get('fallback_available'):
            st.sidebar.info("🏠 Local model available as backup")
        else:
            st.sidebar.info("📝 Simple responses only")
    else:
        st.sidebar.error("❌ LLM Issues Detected")
    
    # Network status indicator
    if connectivity.get('status') == 'network_error':
        st.sidebar.error("🌐 Network Issues - Using Fallbacks")
    elif connectivity.get('status') == 'success':
        st.sidebar.success("🌐 Network Connected")
    
    # System readiness
    if chatbot.is_ready():
        st.sidebar.success("✅ System Ready")
    else:
        st.sidebar.warning("⚠️ Limited Functionality")
    
    # Stats
    with st.sidebar.expander("📈 Session Statistics"):
        st.write(f"**Queries Processed:** {stats.get('queries_processed', 0)}")
        st.write(f"**Languages Used:** {', '.join(stats.get('languages_detected', [])) if stats.get('languages_detected') else 'None'}")
        st.write(f"**Session Duration:** {stats.get('session_duration_minutes', 0):.1f} minutes")
        st.write(f"**System Status:** {'Active' if chatbot.rag_system else 'Error'}")
        
        # LLM Details
        if llm_status["status"] != "error":
            st.write(f"**Current Model:** {llm_status.get('model_name', 'Unknown')}")
            st.write(f"**Model Type:** {llm_status.get('llm_type', 'Unknown')}")
    
    # Session stats - moved outside expander for better visibility
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Queries", stats.get('queries_processed', 0))
    with col2:
        st.metric("Duration", f"{stats.get('session_duration_minutes', 0):.1f}m")
    
    # System components
    if stats.get('embeddings_loaded'):
        st.sidebar.success("📊 Embeddings: Ready")
    else:
        st.sidebar.error("📊 Embeddings: Not Ready")
    
    if stats.get('vectorstore_loaded'):
        st.sidebar.success("🗃️ Vector Store: Ready")
        if 'vector_store_size' in stats:
            st.sidebar.info(f"Documents: {stats['vector_store_size']}")
    else:
        st.sidebar.error("🗃️ Vector Store: Not Ready")
    
    # Languages detected
    if stats.get('languages_detected'):
        langs = ', '.join(stats.get('languages_detected', []))
        st.sidebar.info(f"🌐 Languages: {langs}")


def display_sample_queries():
    """Display sample queries for users"""
    st.subheader("💡 Sample Questions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**English Examples:**")
        sample_queries_en = [
            "What does Article 27 say about equality?",
            "What are the fundamental rights in Bangladesh Constitution?",
            "What is the role of the Prime Minister?",
            "How can the Constitution be amended?",
            "What does the Constitution say about freedom of speech?"
        ]
        
        for query in sample_queries_en:
            if st.button(query, key=f"en_{query}"):
                st.session_state.sample_query = query
                st.session_state.trigger_query = True
                st.rerun()
    
    with col2:
        st.markdown("**বাংলা উদাহরণ:**")
        sample_queries_bn = [
            "সংবিধানের ২৭ অনুচ্ছেদে সমতার বিষয়ে কী বলা হয়েছে?",
            "বাংলাদেশের সংবিধানে মৌলিক অধিকারগুলো কী কী?",
            "প্রধানমন্ত্রীর ভূমিকা কী?",
            "কীভাবে সংবিধান সংশোধন করা যায়?",
            "বাক স্વাধীনতা সম্পর্কে সংবিধানে কী বলা হয়েছে?"
        ]
        
        for query in sample_queries_bn:
            if st.button(query, key=f"bn_{query}"):
                st.session_state.sample_query = query
                st.session_state.trigger_query = True
                st.rerun()


def main():
    """Main Streamlit app"""
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "sample_query" not in st.session_state:
        st.session_state.sample_query = ""
    if "trigger_query" not in st.session_state:
        st.session_state.trigger_query = False
    
    # Header
    st.markdown('<div class="main-header">🏛️ Bangladesh Constitution Chatbot</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ask questions about the Constitution of the People\'s Republic of Bangladesh</div>', unsafe_allow_html=True)
    
    # Initialize chatbot
    chatbot = initialize_chatbot()
    
    if not chatbot:
        st.error("❌ Chatbot failed to initialize. Please check the system configuration.")
        st.info("Make sure you have:")
        st.write("1. Processed the Constitution data (`python src/data_processor.py --process`)")
        st.write("2. All required dependencies installed")
        st.write("3. Sufficient system resources (16GB RAM recommended)")
        return
    
    # Allow operation even if not fully ready - fallback mode will handle it
    if not chatbot.is_ready():
        st.warning("⚠️ System running in limited mode. Some features may not be available.")
        st.info("The chatbot will use fallback mechanisms to answer your questions.")
    
    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/f/f9/Flag_of_Bangladesh.svg", width=200)
        
        # System status
        display_system_stats(chatbot)
        
        st.markdown("---")
        
        # Settings
        st.subheader("⚙️ Settings")
        use_llm = st.checkbox("Use Advanced LLM", value=True, 
                              help="Enable for better responses (recommended)")
        
        # Test fallback mechanism
        if st.button("🧪 Test Fallback", help="Test the fallback mechanism"):
            test_result = check_llm_status(chatbot)
            st.json(test_result)
        
        # Clear conversation
        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages = []
            chatbot.clear_conversation_history()
            st.success("Conversation cleared!")
        
        st.markdown("---")
        
        # Conversation history
        display_conversation_history(chatbot)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chat interface
        st.subheader("💬 Chat with the Constitution")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant" and "metadata" in message:
                    with st.expander("📋 Details"):
                        st.json(message["metadata"])
        
        # Chat input
        query = st.chat_input("Ask about the Bangladesh Constitution...")
        
        # Handle sample query selection (triggered by button clicks)
        if st.session_state.trigger_query and st.session_state.sample_query:
            query = st.session_state.sample_query
            st.session_state.sample_query = ""
            st.session_state.trigger_query = False
        
        # Process user input
        if query:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": query})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(query)
            
            # Process query and display response
            with st.chat_message("assistant"):
                with st.spinner("🤔 Processing your question..."):
                    try:
                        result = chatbot.process_query(query, use_llm=use_llm)
                        
                        # Check if fallback was used
                        if result.get('fallback_used', False):
                            st.warning("⚠️ Using fallback mode - response quality may be limited")
                        
                        # Check for network issues and suggest solutions
                        if "error" in result and any(keyword in str(result.get('error', '')).lower() for keyword in ['nameresolutionerror', 'getaddrinfo failed', 'max retries exceeded']):
                            st.error("🌐 Network connectivity issues detected")
                            st.info("💡 Try: Check your internet connection, or the system will use offline responses")
                        
                        # Display response
                        st.markdown(result["answer"])
                        
                        # Show additional info if there were issues
                        if "error" in result and result.get("scope") != "error":
                            with st.expander("⚠️ Technical Details"):
                                st.error(f"Issue encountered: {result['error']}")
                                st.info("The system used fallback mechanisms to provide a response.")
                        
                    except Exception as e:
                        st.error(f"❌ Critical error: {str(e)}")
                        st.info("💡 Try asking a simpler question or check your internet connection")
                        result = {
                            "answer": f"I encountered a critical error. Please try again or ask a different question.",
                            "language": "en",
                            "num_sources": 0,
                            "processing_time": 0,
                            "scope": "error"
                        }
                
                # Add response to chat history with metadata
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": result["answer"],
                    "metadata": {
                        "language": result.get("language", "en"),
                        "sources": result.get("num_sources", 0),
                        "processing_time": f"{result.get('processing_time', 0):.2f}s",
                        "scope": result.get("scope", "constitutional"),
                        "fallback_used": result.get("fallback_used", False)
                    }
                })
                
                # Show quick stats
                col_lang, col_sources, col_time = st.columns(3)
                with col_lang:
                    st.metric("Language", result.get("language", "en").upper())
                with col_sources:
                    st.metric("Sources", result.get("num_sources", 0))
                with col_time:
                    st.metric("Time", f"{result.get('processing_time', 0):.2f}s")
    
    with col2:
        # Sample queries
        display_sample_queries()
        
        st.markdown("---")
        
        # Information panel
        st.subheader("ℹ️ About")
        st.info("""
        This chatbot provides information about the **Constitution of the People's Republic of Bangladesh** (1972, with amendments up to the 17th Amendment, 2018).
        
        **Features:**
        - 🔍 Accurate constitutional information
        - 🌐 Bilingual support (English & Bangla)  
        - 📊 Source citations
        - ⚡ Fast CPU-based processing
        """)
        
        # Legal disclaimer
        st.markdown('<div class="disclaimer">', unsafe_allow_html=True)
        st.warning("""
        ⚠️ **Legal Disclaimer:**
        
        This chatbot provides educational information only and does not constitute legal advice. For legal matters, consult qualified legal professionals.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 0.9rem;">
        🏛️ Bangladesh Constitution Chatbot | Built with Streamlit & LangChain | 
        Data: Constitution of Bangladesh (1972-2018)
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()