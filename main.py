import streamlit as st
import requests
import json
from typing import List, Dict
import time

# Configuration
st.set_page_config(
    page_title="Marcus Assistant - AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .message-header {
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #333;
    }
    .message-content {
        color: #666;
        line-height: 1.6;
    }
    .stTextInput > div > div > input {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Alternative models that are more likely to work
AVAILABLE_MODELS = {
    "Microsoft DialoGPT Large": "microsoft/DialoGPT-large",
    "Facebook BlenderBot": "facebook/blenderbot-400M-distill",
    "Google Flan-T5 Large": "google/flan-t5-large",
    "Mistral 7B Instruct": "mistralai/Mistral-7B-Instruct-v0.1",
    "Code Llama Instruct": "codellama/CodeLlama-7b-Instruct-hf",
    "Qwen 2.5 (if available)": "Qwen/Qwen2.5-72B-Instruct"
}

def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "hf_token" not in st.session_state:
        st.session_state.hf_token = ""
    if "model_endpoint" not in st.session_state:
        st.session_state.model_endpoint = ""

def test_model_availability(model_name: str, hf_token: str) -> bool:
    """Test if a model is available on Hugging Face Inference API"""
    endpoint = f"https://api-inference.huggingface.co/models/{model_name}"
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    try:
        # Send a simple test request
        test_payload = {"inputs": "Hello", "parameters": {"max_new_tokens": 1}}
        response = requests.post(endpoint, headers=headers, json=test_payload, timeout=10)
        
        # Check if the response indicates the model is available
        if response.status_code == 200:
            return True
        elif response.status_code == 503:
            # Model is loading, but available
            return True
        elif response.status_code == 404:
            # Model not found
            return False
        else:
            return False
    except Exception:
        return False

def query_huggingface_api(payload: Dict, headers: Dict, endpoint: str) -> str:
    """Query the Hugging Face API with better error handling"""
    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        
        # Handle different status codes
        if response.status_code == 503:
            # Model is loading
            st.warning("⏳ Model is loading. This may take a few moments...")
            time.sleep(20)  # Wait and retry
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        
        response.raise_for_status()
        
        # Handle different response formats
        result = response.json()
        
        # For text generation models
        if isinstance(result, list) and len(result) > 0:
            if 'generated_text' in result[0]:
                generated = result[0]['generated_text']
                # Remove the input prompt from the response
                if 'inputs' in payload and payload['inputs'] in generated:
                    generated = generated.replace(payload['inputs'], '').strip()
                return generated if generated else "I apologize, but I couldn't generate a proper response. Please try again."
            elif 'text' in result[0]:
                return result[0]['text']
        
        # For conversational models
        if isinstance(result, dict):
            if 'generated_text' in result:
                generated = result['generated_text']
                # Remove the input prompt from the response
                if 'inputs' in payload and payload['inputs'] in generated:
                    generated = generated.replace(payload['inputs'], '').strip()
                return generated if generated else "I apologize, but I couldn't generate a proper response. Please try again."
            elif 'response' in result:
                return result['response']
            elif 'text' in result:
                return result['text']
            elif 'error' in result:
                st.error(f"API Error: {result['error']}")
                return "I encountered an error while processing your request. Please try again or try a different model."
        
        return str(result)
        
    except requests.exceptions.Timeout:
        st.error("Request timed out. The model might be busy.")
        return "I apologize for the delay. The system is currently experiencing high demand. Please try again shortly."
    except requests.exceptions.RequestException as e:
        if "404" in str(e):
            st.error("Model not found. Please check if the model exists and is accessible.")
            return "The selected model appears to be unavailable. Please try selecting a different model."
        st.error(f"API Request Error: {str(e)}")
        return "I apologize, but I'm experiencing some connectivity issues at the moment. Please try again shortly."
    except json.JSONDecodeError:
        st.error("Error: Invalid JSON response from API")
        return "I received an unexpected response format. Please check your configuration."
    except Exception as e:
        st.error(f"Unexpected Error: {str(e)}")
        return "Something unexpected occurred. Let me try to assist you differently."

def format_message(role: str, content: str):
    """Format and display a chat message"""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <div class="message-header">👤 You</div>
            <div class="message-content">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <div class="message-header">🤖 Marcus Assistant</div>
            <div class="message-content">{content}</div>
        </div>
        """, unsafe_allow_html=True)

def main():
    init_session_state()
    
    # Load configuration from secrets with fallback
    try:
        hf_token = st.secrets.get("HUGGINGFACE_TOKEN", "")
        if not hf_token:
            st.error("🚨 **Configuration Error**: HUGGINGFACE_TOKEN not found in secrets.")
            return
            
        # Try to get model from secrets, with fallback options
        preferred_model = st.secrets.get("DEFAULT_MODEL", "microsoft/DialoGPT-large")
        endpoint_type = st.secrets.get("DEFAULT_ENDPOINT_TYPE", "Inference API")
        
        # Advanced settings from secrets (with defaults)
        max_length = st.secrets.get("MAX_RESPONSE_LENGTH", 200)
        temperature = st.secrets.get("TEMPERATURE", 0.7)
        top_p = st.secrets.get("TOP_P", 0.9)
        
    except Exception as e:
        st.error(f"🚨 **Configuration Error**: {str(e)}")
        st.markdown("""
        **Required secrets:**
        ```toml
        HUGGINGFACE_TOKEN = "hf_your_token_here"
        DEFAULT_MODEL = "microsoft/DialoGPT-large"  # Fallback model
        DEFAULT_ENDPOINT_TYPE = "Inference API"
        ```
        """)
        return
    
    # Sidebar with model selection and controls
    with st.sidebar:
        st.header("🤖 Marcus Assistant Controls")
        
        # Model selection
        st.subheader("🧠 Model Selection")
        selected_model_name = st.selectbox(
            "Choose AI Model:",
            options=list(AVAILABLE_MODELS.keys()),
            index=0 if preferred_model not in AVAILABLE_MODELS.values() else list(AVAILABLE_MODELS.values()).index(preferred_model)
        )
        
        model_name = AVAILABLE_MODELS[selected_model_name]
        endpoint = f"https://api-inference.huggingface.co/models/{model_name}"
        
        # Test model availability
        if st.button("🔍 Test Model", use_container_width=True):
            with st.spinner("Testing model availability..."):
                if test_model_availability(model_name, hf_token):
                    st.success(f"✅ {selected_model_name} is available!")
                else:
                    st.error(f"❌ {selected_model_name} is not available. Try another model.")
        
        # Status indicators
        st.success("🔐 Configuration loaded")
        st.info(f"🧠 Current Model: {selected_model_name}")
        st.info(f"🌐 Endpoint: {endpoint_type}")
        
        st.markdown("---")
        
        # Advanced settings
        with st.expander("⚙️ Advanced Settings"):
            max_length = st.slider("Max Response Length", 50, 500, max_length)
            temperature = st.slider("Temperature", 0.1, 2.0, temperature, 0.1)
            top_p = st.slider("Top P", 0.1, 1.0, top_p, 0.1)
        
        # Clear chat history
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        # Chat statistics
        if st.session_state.messages:
            st.markdown("📊 **Chat Statistics**")
            st.text(f"Messages: {len(st.session_state.messages)}")
            st.text(f"Conversations: {len(st.session_state.messages) // 2}")
    
    # Main chat interface
    st.title("🤖 Marcus Assistant - AI Assistant")
    st.markdown("*Your intelligent AI companion for helpful conversations and assistance.*")
    
    # Add Marcus Assistant description
    with st.expander("About Marcus Assistant"):
        st.markdown(f"""
        **Marcus Assistant** is your intelligent AI companion designed to provide helpful and engaging conversations:
        
        ✅ **Advanced natural language processing** with thoughtful responses  
        ✅ **Multi-domain expertise** spanning technology, science, and general knowledge  
        ✅ **Helpful assistance** with a friendly and professional approach  
        ✅ **Personable interaction** style that adapts to your needs  
        ✅ **Context-aware responses** that understand conversation flow  
        ✅ **Reliable support** with built-in safety and ethical guidelines  
        
        *Currently powered by: {selected_model_name}*
        """)
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            format_message(message["role"], message["content"])
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with chat_container:
            format_message("user", user_input)
        
        # Prepare API request
        headers = {
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json"
        }
        
        # Build Marcus Assistant system prompt and conversation context
        system_prompt = """You are Marcus Assistant, an intelligent AI companion designed to provide helpful and engaging conversations. You have:

- Advanced natural language processing with thoughtful responses
- Multi-domain expertise spanning technology, science, and general knowledge
- Helpful assistance with a friendly and professional approach
- Personable interaction style that adapts to user needs
- Context-aware responses that understand conversation flow
- Reliable support with built-in safety and ethical guidelines

Respond with intelligence, helpfulness, and a warm personality while maintaining professionalism."""

        # Build conversation context (keep it shorter for better compatibility)
        conversation_context = f"{system_prompt}\n\nHuman: {user_input}\nMarcus Assistant:"
        
        # Different payload based on model type
        if "flan-t5" in model_name.lower():
            # T5 models work better with simpler prompts
            payload = {
                "inputs": f"Answer this question in the style of a helpful AI assistant named Marcus: {user_input}",
                "parameters": {
                    "max_new_tokens": max_length,
                    "temperature": temperature,
                    "do_sample": True
                }
            }
        else:
            # Other models
            payload = {
                "inputs": conversation_context,
                "parameters": {
                    "max_new_tokens": max_length,
                    "temperature": temperature,
                    "top_p": top_p,
                    "do_sample": True,
                    "return_full_text": False,
                    "stop": ["Human:", "Marcus Assistant:", "\n\nHuman:", "\n\nMarcus Assistant:"]
                }
            }
        
        # Show loading indicator with Marcus Assistant style
        with st.spinner("🧠 Marcus Assistant is thinking..."):
            # Query the API
            response = query_huggingface_api(payload, headers, endpoint)
            
            # Clean up the response
            if conversation_context in response:
                response = response.replace(conversation_context, "").strip()
            
            # Remove common prefixes
            prefixes_to_remove = ["Marcus Assistant:", "Assistant:", "Bot:", "AI:", "Response:", "Answer:"]
            for prefix in prefixes_to_remove:
                if response.startswith(prefix):
                    response = response[len(prefix):].strip()
                    break
            
            # Ensure response isn't empty
            if not response.strip():
                response = "I apologize, but I seem to have encountered a brief processing delay. Could you please rephrase your query?"
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Display assistant response
        with chat_container:
            format_message("assistant", response)
        
        # Rerun to update the interface
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"🤖 **Marcus Assistant** - *Your intelligent AI companion* | "
        f"Powered by {selected_model_name} | "
        f"💡 **Tip:** Marcus Assistant is here to help with thoughtful and engaging conversations."
    )

if __name__ == "__main__":
    main()
