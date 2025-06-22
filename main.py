import streamlit as st
import requests
import json
from typing import List, Dict
import time
import os

# Configuration
st.set_page_config(
    page_title="L.E.O - Nutrition & Diet Assistant",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_URL = "https://router.huggingface.co/featherless-ai/v1/chat/completions"

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

# Models compatible with the new inference provider
AVAILABLE_MODELS = {
    "DeepSeek R1": "deepseek-ai/DeepSeek-R1-0528",
    "DeepSeek Coder V2": "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
    "Mistral Large": "mistralai/Mistral-Large",
    "Mixtral 8x22B": "mistralai/Mixtral-8x22B-Instruct-v0.1",
    "Llama 3 70B": "meta-llama/Meta-Llama-3-70B-Instruct"
}

def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "hf_token" not in st.session_state:
        st.session_state.hf_token = ""

def query_chat_api(model: str, headers: Dict, messages: List[Dict]) -> str:
    """Query the chat completions API with error handling"""
    payload = {
        "model": model,
        "messages": messages,
        "stream": False  # We'll handle responses once they are complete
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        response.raise_for_status()
        
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0].get("message", {})
            content = message.get("content", "")
            return content if content else "I apologize, but I couldn't generate a proper response. Please try again."
        elif "error" in result:
            st.error(f"API Error: {result['error']}")
            return "I encountered an error while processing your request. Please check the model compatibility or your API token."
        
        return str(result)
        
    except requests.exceptions.Timeout:
        st.error("Request timed out. The model might be busy or the request too long.")
        return "I apologize for the delay. The system is currently experiencing high demand. Please try again shortly."
    except requests.exceptions.RequestException as e:
        st.error(f"API Request Error: {str(e)}")
        if e.response:
            st.error(f"Response Content: {e.response.text}")
        return "I apologize, but I'm experiencing some connectivity issues at the moment. Please try again shortly."
    except json.JSONDecodeError:
        st.error("Error: Invalid JSON response from API. The model may be unavailable.")
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
            <div class="message-header">🥗 L.E.O</div>
            <div class="message-content">{content}</div>
        </div>
        """, unsafe_allow_html=True)

def main():
    init_session_state()
    
    # Load configuration from secrets
    try:
        hf_token = st.secrets.get("HF_TOKEN")
        if not hf_token:
            # Fallback for local development if secrets aren't set
            hf_token = os.environ.get("HF_TOKEN")

        if not hf_token:
            st.error("🚨 **Configuration Error**: HF_TOKEN not found in secrets or environment variables.")
            st.markdown("""
            **Please add your Hugging Face token to Streamlit Cloud secrets:**
            ```toml
            HF_TOKEN = "hf_your_token_here"
            ```
            **Or set it as an environment variable for local development.**
            """)
            return
            
        # Try to get model from secrets, with fallback options
        preferred_model = st.secrets.get("DEFAULT_MODEL", "deepseek-ai/DeepSeek-R1-0528")
        
        # Advanced settings from secrets (with defaults)
        temperature = st.secrets.get("TEMPERATURE", 0.7)
        top_p = st.secrets.get("TOP_P", 0.9)
        
    except Exception as e:
        st.error(f"🚨 **Configuration Error**: {str(e)}")
        st.markdown("""
        **Required secrets:**
        ```toml
        HF_TOKEN = "hf_your_token_here"
        DEFAULT_MODEL = "deepseek-ai/DeepSeek-R1-0528"
        ```
        """)
        return
    
    # Sidebar with model selection and controls
    with st.sidebar:
        st.header("🥗 L.E.O Controls")
        
        # Model selection
        st.subheader("🧠 Model Selection")
        selected_model_name = st.selectbox(
            "Choose AI Model:",
            options=list(AVAILABLE_MODELS.keys()),
            index=0 if preferred_model not in AVAILABLE_MODELS.values() else list(AVAILABLE_MODELS.values()).index(preferred_model)
        )
        
        model_name = AVAILABLE_MODELS[selected_model_name]
        
        # Status indicators
        st.success("🔐 Configuration loaded")
        st.info(f"🧠 Current Model: {selected_model_name}")
        st.info(f"🌐 Provider: Featherless AI Router")
        
        st.markdown("---")
        
        # Advanced settings (Note: these may not be supported by all models/endpoints)
        with st.expander("⚙️ Advanced Settings (Model Dependent)"):
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
    st.title("🥗 L.E.O - Nutrition & Diet Assistant")
    st.markdown("*Your expert guide to nutrition, diet, and wellness - powered by advanced AI models.*")
    
    # Add L.E.O description
    with st.expander("About L.E.O"):
        st.markdown(f"""
        **L.E.O** is your trusted nutrition and diet expert:
        
        ✅ **Expert nutrition knowledge** with science-based advice  
        ✅ **Personalized diet recommendations** for your goals and needs  
        ✅ **Meal planning expertise** for weight loss, muscle gain, and health conditions  
        ✅ **Food science insights** and ingredient analysis  
        ✅ **Supplement guidance** and wellness strategies  
        ✅ **Supportive and non-judgmental** approach to nutrition  
        
        *Currently powered by: {selected_model_name}*
        """)
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            format_message(message["role"], message["content"])
    
    # Chat input
    user_input = st.chat_input("Ask me about nutrition, diet, or wellness...")
    
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
        
        system_prompt = """You are NutriGuide, a highly knowledgeable and friendly AI assistant who is an expert in all things related to nutrition, diet, food science, and wellness.

You provide accurate, science-based, and practical advice on topics such as:

Nutritional content of foods

Personalized diet recommendations (based on age, gender, activity level, and health conditions)

Meal planning for different goals (weight loss, muscle gain, managing diabetes, etc.)

Understanding food labels and ingredients

Nutrient deficiencies and their symptoms

Gut health, hydration, supplements, and holistic well-being

Your tone is supportive, non-judgmental, and clear.
You always cite evidence or mention when something is general advice vs. clinical guidance.
You do not diagnose medical conditions or replace a doctor, but you help people make informed choices.

If users ask non-nutrition-related questions, politely guide them back to nutrition or wellness topics.

Focus on macros, supplements, and fitness-linked meal plans. Include sport-specific nutrition strategies."""

        # Build conversation context
        messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
        
        # Show loading indicator
        with st.spinner(f"🥗 L.E.O is consulting with {selected_model_name}..."):
            # Query the API
            response = query_chat_api(model_name, headers, messages)
            
            # Clean up the response
            prefixes_to_remove = ["L.E.O:", "Assistant:", "Bot:", "AI:", "Response:", "Answer:", "NutriGuide:"]
            for prefix in prefixes_to_remove:
                if response.startswith(prefix):
                    response = response[len(prefix):].strip()
                    break
            
            # Ensure response isn't empty
            if not response.strip():
                response = "I apologize, but I seem to have encountered a brief processing delay. Could you please rephrase your nutrition question?"
        
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
        f"🥗 **L.E.O** - *Your Nutrition & Diet Expert* | "
        f"Powered by {selected_model_name} | "
        f"💡 **Tip:** Ask L.E.O about meal plans, supplements, macros, or any nutrition topic!"
    )

if __name__ == "__main__":
    main()
