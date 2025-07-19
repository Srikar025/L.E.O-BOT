import streamlit as st
import requests
import json
from typing import Dict, List, Optional

# Page configuration
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Available models configuration
AVAILABLE_MODELS = {
    "Llama 2 7B Chat": "meta-llama/Llama-2-7b-chat-hf",
    "Llama 2 13B Chat": "meta-llama/Llama-2-13b-chat-hf",
    "Mistral 7B Instruct": "mistralai/Mistral-7B-Instruct-v0.1",
    "CodeLlama 7B Instruct": "codellama/CodeLlama-7b-Instruct-hf",
    "Zephyr 7B Beta": "HuggingFaceH4/zephyr-7b-beta",
    "Falcon 7B Instruct": "tiiuae/falcon-7b-instruct"
}

def get_api_key() -> Optional[str]:
    """Get Hugging Face API key from Streamlit secrets"""
    try:
        return st.secrets["HUGGINGFACE_API_KEY"]
    except KeyError:
        st.error("⚠️ Hugging Face API key not found in secrets. Please add it in Streamlit Cloud settings.")
        st.info("Go to your Streamlit Cloud app settings and add HUGGINGFACE_API_KEY to secrets.")
        return None

def query_huggingface_api(model_id: str, messages: List[Dict], api_key: str, max_tokens: int = 500, temperature: float = 0.7) -> Optional[str]:
    """Query Hugging Face Inference API"""
    
    # Format messages for the API
    if len(messages) > 1:
        # For chat models, format as conversation
        prompt = ""
        for msg in messages:
            if msg["role"] == "user":
                prompt += f"User: {msg['content']}\n"
            elif msg["role"] == "assistant":
                prompt += f"Assistant: {msg['content']}\n"
        prompt += "Assistant:"
    else:
        prompt = messages[-1]["content"]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "do_sample": True,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model_id}",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "").strip()
            elif isinstance(result, dict):
                return result.get("generated_text", "").strip()
        elif response.status_code == 503:
            return "⏳ Model is loading. Please try again in a moment."
        else:
            return f"❌ Error: {response.status_code} - {response.text}"
            
    except requests.exceptions.Timeout:
        return "⏰ Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"🔌 Connection error: {str(e)}"
    except Exception as e:
        return f"💥 Unexpected error: {str(e)}"

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = list(AVAILABLE_MODELS.keys())[0]

def main():
    """Main Streamlit application"""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("🤖 AI Chatbot")
    st.markdown("Chat with various AI models powered by Hugging Face")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model selection
        selected_model_name = st.selectbox(
            "Choose AI Model",
            list(AVAILABLE_MODELS.keys()),
            index=list(AVAILABLE_MODELS.keys()).index(st.session_state.selected_model)
        )
        st.session_state.selected_model = selected_model_name
        selected_model_id = AVAILABLE_MODELS[selected_model_name]
        
        # Model parameters
        st.subheader("Parameters")
        max_tokens = st.slider("Max Tokens", min_value=50, max_value=1000, value=500, step=50)
        temperature = st.slider("Temperature", min_value=0.1, max_value=2.0, value=0.7, step=0.1)
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        # Model info
        st.subheader("📊 Model Info")
        st.info(f"**Selected:** {selected_model_name}")
        st.code(selected_model_id, language="text")
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        st.stop()
    
    # Chat interface
    st.subheader("💬 Chat")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner(f"Thinking with {selected_model_name}..."):
                    # Query the API
                    response = query_huggingface_api(
                        selected_model_id,
                        st.session_state.messages,
                        api_key,
                        max_tokens,
                        temperature
                    )
                
                if response:
                    st.markdown(response)
                    # Add assistant response to chat
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    error_msg = "Sorry, I couldn't generate a response. Please try again."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Messages", len(st.session_state.messages))
    with col2:
        st.metric("Current Model", selected_model_name.split()[0])
    with col3:
        if st.session_state.messages:
            last_role = st.session_state.messages[-1]["role"]
            st.metric("Last Speaker", last_role.title())

if __name__ == "__main__":
    main()
