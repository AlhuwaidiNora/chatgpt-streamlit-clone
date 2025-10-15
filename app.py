import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

# Page configuration
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .header-title {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        text-align: center;
    }
    
    .header-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        text-align: center;
        margin-top: 0.5rem;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #ffffff;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Input styling */
    .stChatInput {
        border-radius: 10px;
    }
    
    /* Metric cards */
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🤖 AI Chat Assistant</h1>
        <p class="header-subtitle">Powered by GPT-3.5 Turbo | Professional Conversational AI</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value="",
        help="Enter your OpenAI API key"
    )
    
    # Model selection
    model_name = st.selectbox(
        "Select Model",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        help="Choose the AI model to use"
    )
    
    # Temperature slider
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Higher values make output more random, lower values more deterministic"
    )
    
    st.divider()
    
    # Chat statistics
    st.header("📊 Chat Statistics")
    if "messages" in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Messages", len(st.session_state.messages))
        with col2:
            user_msgs = len([m for m in st.session_state.messages if m["role"] == "user"])
            st.metric("Your Messages", user_msgs)
    
    st.divider()
    
    # Action buttons
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("💾 Export Chat", use_container_width=True):
        if "messages" in st.session_state and st.session_state.messages:
            chat_export = "\n\n".join([
                f"{m['role'].upper()}: {m['content']}" 
                for m in st.session_state.messages
            ])
            st.download_button(
                label="Download Chat",
                data=chat_export,
                file_name="chat_export.txt",
                mime="text/plain"
            )
        else:
            st.warning("No messages to export")

# Initialize session state
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = model_name

if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize LangChain ChatOpenAI
try:
    llm = ChatOpenAI(
        api_key=api_key,
        model_name=model_name,
        streaming=True,
        temperature=temperature
    )
except Exception as e:
    st.error(f"Error initializing AI model: {str(e)}")
    st.stop()

# Main chat interface
chat_container = st.container()

with chat_container:
    # Display welcome message if no messages
    if not st.session_state.messages:
        st.info("👋 Welcome! Start a conversation by typing a message below.")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here...", key="chat_input"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        try:
            # Convert messages to LangChain format
            langchain_messages = []
            for m in st.session_state.messages:
                if m["role"] == "user":
                    langchain_messages.append(HumanMessage(content=m["content"]))
                elif m["role"] == "assistant":
                    langchain_messages.append(AIMessage(content=m["content"]))
                elif m["role"] == "system":
                    langchain_messages.append(SystemMessage(content=m["content"]))
            
            # Stream the response
            response = st.write_stream(llm.stream(langchain_messages))
            
            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "Built with Streamlit & LangChain | Powered by OpenAI"
    "</p>",
    unsafe_allow_html=True
)