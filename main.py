import streamlit as st
import requests
import json
from typing import List, Dict
import time
import random

# Page configuration
st.set_page_config(
    page_title="AI Chatbot Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS for modern dark interface
st.markdown("""
<style>
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Main container */
    .main-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Header styles */
    .main-header {
        text-align: center;
        color: white;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .sub-header {
        text-align: center;
        color: rgba(255, 255, 255, 0.8);
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Chat container */
    .chat-container {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        max-height: 500px;
        overflow-y: auto;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(5px);
    }
    
    /* Chat messages */
    .chat-message {
        padding: 1rem 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        animation: fadeIn 0.3s ease-in-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        align-self: flex-end;
        margin-left: 15%;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .bot-message {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        align-self: flex-start;
        margin-right: 15%;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .message-header {
        font-weight: bold;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        opacity: 0.8;
    }
    
    /* Input container - Dark theme */
    .input-container {
        background: rgba(0, 0, 0, 0.4);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Dark input styling */
    .stTextInput > div > div > input {
        background-color: rgba(0, 0, 0, 0.6) !important;
        color: white !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Model info styling */
    .model-info {
        background: rgba(0, 0, 0, 0.3);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Welcome message */
    .welcome-message {
        background: rgba(76, 175, 80, 0.2);
        border-left: 4px solid #4caf50;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.9rem;
        margin-top: 2rem;
    }
    
    /* Scrollbar styling */
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# Available free Hugging Face models
AVAILABLE_MODELS = {
    "Conversational": [
        "microsoft/DialoGPT-medium",
        "microsoft/DialoGPT-large", 
        "microsoft/DialoGPT-small",
        "facebook/blenderbot-400M-distill",
        "facebook/blenderbot-1B-distill",
        "facebook/blenderbot-3B",
    ],
    "Text Generation": [
        "gpt2",
        "gpt2-medium",
        "gpt2-large",
        "distilgpt2",
        "EleutherAI/gpt-neo-1.3B",
        "EleutherAI/gpt-neo-2.7B",
        "EleutherAI/gpt-j-6B",
        "bigscience/bloom-560m",
        "bigscience/bloom-1b1",
    ],
    "Instruction Following": [
        "google/flan-t5-small",
        "google/flan-t5-base",
        "google/flan-t5-large",
        "microsoft/GODEL-v1_1-base-seq2seq",
        "microsoft/GODEL-v1_1-large-seq2seq",
    ],
    "Code Generation": [
        "Salesforce/codegen-350M-mono",
        "Salesforce/codegen-2B-mono",
        "microsoft/CodeGPT-small-py",
        "codeparrot/codeparrot-small",
    ]
}

class HuggingFaceChatbot:
    def __init__(self, api_token: str, model_name: str = "microsoft/DialoGPT-medium"):
        self.api_token = api_token
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        self.headers = {"Authorization": f"Bearer {api_token}"}
        self.model_type = self._get_model_type()
    
    def _get_model_type(self):
        """Determine model type for appropriate processing"""
        for category, models in AVAILABLE_MODELS.items():
            if self.model_name in models:
                return category
        return "Text Generation"
    
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
        """Generate response from the model based on type"""
        if conversation_history is None:
            conversation_history = []
        
        # Prepare payload based on model type
        if self.model_type == "Conversational":
            return self._get_conversational_response(message, conversation_history)
        elif self.model_type == "Instruction Following":
            return self._get_instruction_response(message)
        elif self.model_type == "Code Generation":
            return self._get_code_response(message)
        else:
            return self._get_text_generation_response(message, conversation_history)
    
    def _get_conversational_response(self, message: str, conversation_history: List[str]) -> str:
        """Handle conversational models"""
        if conversation_history:
            context = " ".join(conversation_history[-8:])
            input_text = f"{context} {message}"
        else:
            input_text = message
        
        payload = {
            "inputs": input_text,
            "parameters": {
                "max_length": 200,
                "temperature": 0.7,
                "do_sample": True,
                "pad_token_id": 50256
            },
            "options": {"wait_for_model": True}
        }
        
        result = self.query_model(payload)
        return self._extract_response(result, input_text)
    
    def _get_text_generation_response(self, message: str, conversation_history: List[str]) -> str:
        """Handle text generation models"""
        if conversation_history:
            context = " ".join(conversation_history[-4:])
            input_text = f"{context}\nHuman: {message}\nAssistant:"
        else:
            input_text = f"Human: {message}\nAssistant:"
        
        payload = {
            "inputs": input_text,
            "parameters": {
                "max_new_tokens": 150,
                "temperature": 0.8,
                "do_sample": True,
                "stop": ["Human:", "\n\n"]
            },
            "options": {"wait_for_model": True}
        }
        
        result = self.query_model(payload)
        return self._extract_response(result, input_text)
    
    def _get_instruction_response(self, message: str) -> str:
        """Handle instruction-following models"""
        input_text = f"Answer this question: {message}"
        
        payload = {
            "inputs": input_text,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.7
            },
            "options": {"wait_for_model": True}
        }
        
        result = self.query_model(payload)
        return self._extract_response(result, input_text)
    
    def _get_code_response(self, message: str) -> str:
        """Handle code generation models"""
        input_text = f"# {message}\n"
        
        payload = {
            "inputs": input_text,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.3,
                "do_sample": True
            },
            "options": {"wait_for_model": True}
        }
        
        result = self.query_model(payload)
        return self._extract_response(result, input_text)
    
    def _extract_response(self, result: Dict, input_text: str) -> str:
        """Extract and clean response from API result"""
        if "error" in result:
            return "Sorry, I encountered an error. Please try again."
        
        try:
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
            elif isinstance(result, dict):
                generated_text = result.get("generated_text", "")
            else:
                return "Sorry, I couldn't generate a proper response."
            
            # Clean the response
            if input_text in generated_text:
                response = generated_text.replace(input_text, "").strip()
            else:
                response = generated_text.strip()
            
            # Additional cleaning
            response = response.split("Human:")[0].strip()
            response = response.split("\n\n")[0].strip()
            
            return response if response else "I'm not sure how to respond to that."
        except (KeyError, IndexError, TypeError) as e:
            return "Sorry, I couldn't generate a proper response."

def get_secrets():
    """Retrieve secrets from Streamlit Cloud secrets"""
    try:
        api_token = st.secrets["HUGGINGFACE_API_TOKEN"]
        
        # Get model category and specific model
        model_category = st.secrets.get("MODEL_CATEGORY", "Conversational")
        model_name = st.secrets.get("MODEL_NAME", "microsoft/DialoGPT-medium")
        
        # Validate model exists
        all_models = []
        for models in AVAILABLE_MODELS.values():
            all_models.extend(models)
        
        if model_name not in all_models:
            model_name = "microsoft/DialoGPT-medium"
            
        return api_token, model_name, model_category
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
    if "model_switched" not in st.session_state:
        st.session_state.model_switched = False

def display_chat_messages():
    """Display all chat messages"""
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-message">
            <h4>🚀 Welcome to AI Chatbot Pro!</h4>
            <p>I'm powered by advanced Hugging Face AI models. Ask me anything - from casual conversation to coding help!</p>
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

def get_model_description(model_name: str) -> str:
    """Get model description"""
    descriptions = {
        "microsoft/DialoGPT-medium": "Conversational AI - Great for chat",
        "gpt2": "Classic text generation - Creative writing",
        "google/flan-t5-base": "Instruction following - Task completion",
        "Salesforce/codegen-350M-mono": "Code generation - Programming help",
        "facebook/blenderbot-400M-distill": "Social chatbot - Engaging conversations",
        "EleutherAI/gpt-neo-1.3B": "Large language model - Versatile AI"
    }
    return descriptions.get(model_name, "Advanced AI model")

def main():
    # Main container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Chatbot Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Powered by Multiple Hugging Face AI Models</p>', unsafe_allow_html=True)
    
    initialize_session_state()
    
    # Get secrets and initialize chatbot
    try:
        api_token, model_name, model_category = get_secrets()
        
        # Initialize chatbot if not already done
        if st.session_state.chatbot is None:
            st.session_state.chatbot = HuggingFaceChatbot(api_token, model_name)
            
    except Exception as e:
        st.error("Failed to initialize chatbot. Please check your configuration.")
        st.stop()
    
    # Model info and controls
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("🔄 Switch Model", use_container_width=True):
            # Randomly switch to a different model
            all_models = []
            for models in AVAILABLE_MODELS.values():
                all_models.extend(models)
            current_model = st.session_state.chatbot.model_name
            available_models = [m for m in all_models if m != current_model]
            new_model = random.choice(available_models)
            st.session_state.chatbot = HuggingFaceChatbot(api_token, new_model)
            st.session_state.model_switched = True
            st.rerun()
    
    with col2:
        current_model = st.session_state.chatbot.model_name
        model_desc = get_model_description(current_model)
        st.markdown(f"""
        <div class="model-info">
            <strong>🧠 Current Model:</strong><br>
            {current_model.split('/')[-1]}<br>
            <small>{model_desc}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.session_state.model_switched = False
            st.rerun()
    
    # Show model switch notification
    if st.session_state.model_switched:
        st.success(f"✅ Switched to {st.session_state.chatbot.model_name.split('/')[-1]}!")
        st.session_state.model_switched = False
    
    # Chat display container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    display_chat_messages()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input - Dark themed
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    # Create input form
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input(
                "Message",
                placeholder="Type your message here... ✨",
                label_visibility="collapsed"
            )
        
        with col2:
            send_button = st.form_submit_button("Send 🚀", use_container_width=True, type="primary")
    
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
    st.markdown("""
    <div class="footer">
        <p>🌟 Built with Streamlit & Hugging Face • Multiple AI Models Available 🌟</p>
        <p>Switch models anytime for different AI personalities and capabilities!</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
