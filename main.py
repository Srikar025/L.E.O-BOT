import streamlit as st
import requests
import json
from typing import List, Dict
import time

# Page configuration
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="centered"
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
        align-self: flex-end;
        margin-left: 20%;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f5f5f5;
        align-self: flex-start;
        margin-right: 20%;
        border-left: 4px solid #4caf50;
    }
    .message-header {
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #333;
    }
    .stTextInput > div > div > input {
        background-color: white;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
    }
    .main-header {
        text-align: center;
        color: #2196f3;
        margin-bottom: 2rem;
    }
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        background-color: #fafafa;
        margin-bottom: 1rem;
    }
    .input-container {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

class HuggingFaceChatbot:
    def __init__(self, api_token: str, model_name: str = "microsoft/DialoGPT-medium"):
        self.api_token = api_token
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        self.headers = {"Authorization": f"Bearer {api_token}"}
    
    def query_model(self, payload: Dict) -> Dict:
        """Send request to Hugging Face API"""
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {str(e)}")
            return {"error": str(e)}
    
    def get_response(self, message: str, conversation_history: List[str] = None) -> str:
        """Generate response from the model"""
        if conversation_history is None:
            conversation_history = []
        
        # Prepare the input text with conversation context
        if conversation_history:
            context = " ".join(conversation_history[-6:])  # Keep last 6 exchanges
            input_text = f"{context} {message}"
        else:
            input_text = message
        
        payload = {
            "inputs": input_text,
            "parameters": {
                "max_length": 150,
                "temperature": 0.7,
                "do_sample": True,
                "pad_token_id": 50256
            },
            "options": {
                "wait_for_model": True
            }
        }
        
        result = self.query_model(payload)
        
        if "error" in result:
            return "Sorry, I encountered an error. Please try again."
        
        try:
            generated_text = result[0]["generated_text"]
            # Extract only the new response (remove the input part)
            if input_text in generated_text:
                response = generated_text.replace(input_text, "").strip()
            else:
                response = generated_text.strip()
            
            return response if response else "I'm not sure how to respond to that."
        except (KeyError, IndexError, TypeError):
            return "Sorry, I couldn't generate a proper response."

def get_secrets():
    """Retrieve secrets from Streamlit Cloud secrets"""
    try:
        api_token = st.secrets["HUGGINGFACE_API_TOKEN"]
        model_name = st.secrets.get("MODEL_NAME", "microsoft/DialoGPT-medium")
        return api_token, model_name
    except KeyError as e:
        st.error(f"Missing secret: {e}")
        st.error("Please configure your secrets in Streamlit Cloud")
        st.stop()

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = None

def display_chat_messages():
    """Display all chat messages"""
    if not st.session_state.messages:
        st.markdown("""
        <div class="chat-message bot-message">
            <div class="message-header">🤖 AI Assistant</div>
            <div>Hello! I'm your AI assistant powered by Hugging Face. How can I help you today?</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <div class="message-header">👤 You</div>
                <div>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message bot-message">
                <div class="message-header">🤖 AI Assistant</div>
                <div>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Chatbot</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Powered by Hugging Face AI</p>', unsafe_allow_html=True)
    
    initialize_session_state()
    
    # Get secrets and initialize chatbot
    try:
        api_token, model_name = get_secrets()
        
        # Initialize chatbot if not already done
        if st.session_state.chatbot is None:
            st.session_state.chatbot = HuggingFaceChatbot(api_token, model_name)
            
    except Exception as e:
        st.error("Failed to initialize chatbot. Please check your configuration.")
        st.stop()
    
    # Display model info and clear chat button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info(f"**Model:** {model_name}")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.rerun()
    
    # Chat display container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    display_chat_messages()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    # Create input form
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input(
                "Message",
                placeholder="Type your message here...",
                label_visibility="collapsed"
            )
        
        with col2:
            send_button = st.form_submit_button("Send", use_container_width=True, type="primary")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process user input
    if send_button and user_input.strip():
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.conversation_history.append(f"User: {user_input}")
        
        # Show typing indicator
        with st.spinner("🤖 AI is thinking..."):
            try:
                # Get AI response
                response = st.session_state.chatbot.get_response(
                    user_input, 
                    st.session_state.conversation_history
                )
                
                # Add AI response
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.conversation_history.append(f"Assistant: {response}")
                
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        # Rerun to show new messages
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #888; font-size: 12px;">Built with Streamlit & Hugging Face 🚀</p>', 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
