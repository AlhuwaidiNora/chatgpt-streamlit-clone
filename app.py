import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from openai import OpenAI  # optional if you use OpenAI directly


# ---------------------------
# API Key
# ---------------------------
api_key = "sk-proj-otDPLZ2dYqI3QZFelL2nT3BlbkFJfTQ2Gj6kEOPoUN8g9dYE"

# ---------------------------
# Page configuration
# ---------------------------
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------
# Custom CSS
# ---------------------------
st.markdown("""
<style>
.main { background-color: #f8f9fa; }
.header-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.header-title { color: white; font-size: 2.5rem; font-weight: bold; margin:0; text-align:center; }
.header-subtitle { color: rgba(255,255,255,0.9); font-size:1.1rem; text-align:center; margin-top:0.5rem; }
.stChatMessage { background-color:white; border-radius:10px; padding:1rem; margin-bottom:1rem; box-shadow:0 2px 4px rgba(0,0,0,0.05); }
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color:white; border:none; border-radius:8px; padding:0.5rem 2rem; font-weight:600;
    transition: all 0.3s ease; box-shadow:0 2px 4px rgba(0,0,0,0.1);
}
.stButton > button:hover { transform: translateY(-2px); box-shadow:0 4px 8px rgba(0,0,0,0.2); }
.stChatInput { border-radius:10px; }
.metric-card { background-color:white; padding:1.5rem; border-radius:10px; box-shadow:0 2px 4px rgba(0,0,0,0.05); margin-bottom:1rem; }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Header
# ---------------------------
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🤖 AI Chat Assistant</h1>
    <p class="header-subtitle">Powered by GPT-3.5 Turbo | Professional Conversational AI</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# Sidebar
# ---------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    model_name = st.selectbox(
        "Select Model",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        help="Choose the AI model to use"
    )
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Higher values make output more random, lower values more deterministic"
    )

# ---------------------------
# Session State
# ---------------------------
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = model_name
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------
# Initialize LangChain ChatOpenAI
# ---------------------------
try:
    llm = ChatOpenAI(
        openai_api_key=api_key,  # use openai_api_key, not api_key
        model_name=model_name,
        temperature=temperature
    )
except Exception as e:
    st.error(f"Error initializing AI model: {str(e)}")
    st.stop()

# ---------------------------
# Main chat interface
# ---------------------------
chat_container = st.container()
with chat_container:
    if not st.session_state.messages:
        st.info("👋 Welcome! Start a conversation by typing a message below.")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ---------------------------
# Chat input
# ---------------------------
if prompt := st.chat_input("Type your message here...", key="chat_input"):
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        try:
            langchain_messages = []
            for m in st.session_state.messages:
                if m["role"] == "user":
                    langchain_messages.append(HumanMessage(content=m["content"]))
                elif m["role"] == "assistant":
                    langchain_messages.append(AIMessage(content=m["content"]))
                elif m["role"] == "system":
                    langchain_messages.append(SystemMessage(content=m["content"]))
            response = llm.generate(messages=langchain_messages).generations[0][0].text
            st.session_state.messages.append({"role":"assistant","content":response})
            st.markdown(response)
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")

# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "Built with Streamlit & LangChain | Powered by OpenAI"
    "</p>",
    unsafe_allow_html=True
)
