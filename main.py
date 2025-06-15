import streamlit as st
import requests
import json
from typing import List, Dict
import time
import random

# Page configuration
st.set_page_config(
    page_title="Marcus - AI Nutrition Assistant",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS for nutrition-themed interface
st.markdown("""
<style>
    /* Global styles - Green nutrition theme */
    .stApp {
        background: linear-gradient(135deg, #4ade80 0%, #22c55e 50%, #16a34a 100%);
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
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .sub-header {
        text-align: center;
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 500;
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
        background: linear-gradient(135deg, #22c55e, #16a34a);
        color: white;
        align-self: flex-end;
        margin-left: 15%;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
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
        border-color: #22c55e !important;
        box-shadow: 0 0 10px rgba(34, 197, 94, 0.3) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #22c55e, #16a34a) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(34, 197, 94, 0.4) !important;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background-color: rgba(0, 0, 0, 0.6) !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
    }
    
    .stSelectbox > div > div > div {
        color: white !important;
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
        background: rgba(34, 197, 94, 0.2);
        border-left: 4px solid #22c55e;
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* Nutrition tips */
    .nutrition-tip {
        background: rgba(251, 191, 36, 0.2);
        border-left: 4px solid #fbbf24;
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

# Available Qwen 2.5 models and other nutrition-focused models
AVAILABLE_MODELS = {
    "Qwen 2.5 Models": [
        "Qwen/Qwen2.5-7B-Instruct",
        "Qwen/Qwen2.5-3B-Instruct",
        "Qwen/Qwen2.5-1.5B-Instruct",
        "Qwen/Qwen2.5-0.5B-Instruct",
        "Qwen/Qwen2.5-14B-Instruct",
        "Qwen/Qwen2.5-32B-Instruct",
    ],
    "Alternative Models": [
        "microsoft/DialoGPT-medium",
        "google/flan-t5-large",
        "microsoft/GODEL-v1_1-large-seq2seq",
        "facebook/blenderbot-1B-distill",
        "EleutherAI/gpt-neo-2.7B",
    ],
    "Specialized Models": [
        "google/flan-t5-base",
        "microsoft/DialoGPT-large",
        "bigscience/bloom-1b1",
    ]
}

# Nutrition-focused prompts and templates
NUTRITION_PROMPTS = {
    "general": "You are Marcus, a knowledgeable and friendly AI nutrition assistant. Your expertise includes meal planning, dietary advice, nutritional analysis, healthy recipes, and wellness guidance. Always provide evidence-based advice and remind users to consult healthcare professionals for serious health concerns.",
    "meal_planning": "As Marcus, your nutrition assistant, help create balanced meal plans considering dietary preferences, restrictions, and health goals.",
    "recipe_analysis": "As Marcus, analyze recipes for nutritional content, suggest healthier alternatives, and provide cooking tips.",
    "dietary_advice": "As Marcus, provide personalized dietary recommendations based on health goals, lifestyle, and nutritional needs."
}

class MarcusNutritionChatbot:
    def __init__(self, api_token: str, model_name: str = "Qwen/Qwen2.5-7B-Instruct"):
        self.api_token = api_token
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        self.headers = {"Authorization": f"Bearer {api_token}"}
        self.model_type = self._get_model_type()
        self.nutrition_context = NUTRITION_PROMPTS["general"]
    
    def _get_model_type(self):
        """Determine model type for appropriate processing"""
        if "Qwen" in self.model_name:
            return "Instruction Following"
        elif "DialoGPT" in self.model_name or "blenderbot" in self.model_name:
            return "Conversational"
        elif "flan-t5" in self.model_name or "GODEL" in self.model_name:
            return "Instruction Following"
        else:
            return "Text Generation"
    
    def query_model(self, payload: Dict) -> Dict:
        """Send request to Hugging Face API with enhanced error handling"""
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 503:
                return {"error": "Model is loading, please wait 1-2 minutes and try again"}
            elif response.status_code == 401:
                return {"error": "Invalid API token. Please check your Hugging Face token"}
            elif response.status_code == 429:
                return {"error": "Rate limit exceeded. Please wait 30 seconds and try again"}
            elif response.status_code == 400:
                return {"error": "Invalid request. Try a shorter message"}
            
            response.raise_for_status()
            result = response.json()
            
            if isinstance(result, dict) and "error" in result:
                error_msg = result["error"]
                if "loading" in error_msg.lower():
                    return {"error": "Model is still loading. Please wait 1-2 minutes"}
                elif "token" in error_msg.lower():
                    return {"error": "API token issue. Please check your token"}
                else:
                    return {"error": f"API Error: {error_msg}"}
            
            return result
            
        except requests.exceptions.Timeout:
            return {"error": "Request timeout. Please try again"}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection failed. Check your internet connection"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def get_nutrition_response(self, message: str, conversation_history: List[str] = None) -> str:
        """Generate nutrition-focused response"""
        if conversation_history is None:
            conversation_history = []
        
        # Create nutrition-focused prompt
        nutrition_prompt = f"{self.nutrition_context}\n\nUser question: {message}\n\nMarcus (Nutrition Assistant):"
        
        if self.model_type == "Instruction Following":
            return self._get_instruction_response(nutrition_prompt)
        elif self.model_type == "Conversational":
            return self._get_conversational_response(message, conversation_history)
        else:
            return self._get_text_generation_response(nutrition_prompt, conversation_history)
    
    def _get_instruction_response(self, prompt: str) -> str:
        """Handle instruction-following models like Qwen 2.5"""
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 300,
                "temperature": 0.7,
                "do_sample": True,
                "top_p": 0.9,
                "repetition_penalty": 1.1
            },
            "options": {"wait_for_model": True}
        }
        
        result = self.query_model(payload)
        return self._extract_response(result, prompt)
    
    def _get_conversational_response(self, message: str, conversation_history: List[str]) -> str:
        """Handle conversational models"""
        context = f"Marcus the nutrition assistant: {message}"
        if conversation_history:
            recent_history = " ".join(conversation_history[-6:])
            context = f"{recent_history} {context}"
        
        payload = {
            "inputs": context,
            "parameters": {
                "max_length": 250,
                "temperature": 0.8,
                "do_sample": True,
                "pad_token_id": 50256
            },
            "options": {"wait_for_model": True}
        }
        
        result = self.query_model(payload)
        return self._extract_response(result, context)
    
    def _get_text_generation_response(self, prompt: str, conversation_history: List[str]) -> str:
        """Handle text generation models"""
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.8,
                "do_sample": True,
                "stop": ["User:", "Human:", "\n\n"]
            },
            "options": {"wait_for_model": True}
        }
        
        result = self.query_model(payload)
        return self._extract_response(result, prompt)
    
    def _extract_response(self, result: Dict, input_text: str) -> str:
        """Extract and clean response from API result"""
        if "error" in result:
            return "I apologize, but I'm having trouble connecting right now. Please try again in a moment! 🥗"
        
        try:
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
            elif isinstance(result, dict):
                generated_text = result.get("generated_text", "")
            else:
                return "I'm having trouble generating a response. Could you rephrase your question? 🤔"
            
            # Clean the response
            if input_text in generated_text:
                response = generated_text.replace(input_text, "").strip()
            else:
                response = generated_text.strip()
            
            # Additional cleaning for nutrition responses
            response = response.split("User:")[0].strip()
            response = response.split("Human:")[0].strip()
            response = response.split("\n\n")[0].strip()
            
            # Ensure response is nutrition-focused if empty or generic
            if not response or len(response) < 10:
                return "I'd be happy to help with your nutrition question! Could you provide more details so I can give you the best advice? 🥗"
            
            return response
        except (KeyError, IndexError, TypeError):
            return "I'm having some technical difficulties. Please try rephrasing your nutrition question! 🍎"

def get_secrets():
    """Retrieve secrets from Streamlit Cloud secrets"""
    try:
        api_token = st.secrets["HUGGINGFACE_API_TOKEN"]
        
        # Default to Qwen 2.5 model
        model_name = st.secrets.get("MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")
        
        # Validate model exists
        all_models = []
        for models in AVAILABLE_MODELS.values():
            all_models.extend(models)
        
        if model_name not in all_models:
            model_name = "Qwen/Qwen2.5-7B-Instruct"
            
        return api_token, model_name
    except KeyError as e:
        st.error(f"Missing secret: {e}")
        st.error("Please configure your HUGGINGFACE_API_TOKEN in Streamlit Cloud secrets")
        st.stop()

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = None
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "Qwen/Qwen2.5-7B-Instruct"

def display_chat_messages():
    """Display all chat messages"""
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-message">
            <h4>🥗 Hello! I'm Marcus, Your AI Nutrition Assistant</h4>
            <p>I'm here to help you with:</p>
            <ul>
                <li>🍽️ Meal planning and recipe suggestions</li>
                <li>📊 Nutritional analysis and dietary advice</li>
                <li>🎯 Health goal planning and tracking</li>
                <li>🥑 Food recommendations and alternatives</li>
                <li>💪 Sports nutrition and wellness tips</li>
            </ul>
            <p><strong>Ask me anything about nutrition, and let's start your healthy journey!</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display a random nutrition tip
        tips = [
            "💡 Tip: Eating a rainbow of colorful fruits and vegetables ensures you get diverse nutrients!",
            "💡 Tip: Drinking water before meals can help with portion control and digestion.",
            "💡 Tip: Combining protein with carbs post-workout helps with muscle recovery.",
            "💡 Tip: Meal prep on Sundays can set you up for a week of healthy eating!"
        ]
        
        st.markdown(f"""
        <div class="nutrition-tip">
            <p>{random.choice(tips)}</p>
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
                <div class="message-header">🥗 Marcus (Nutrition Assistant)</div>
                <div>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

def get_model_description(model_name: str) -> str:
    """Get model description"""
    descriptions = {
        "Qwen/Qwen2.5-7B-Instruct": "Qwen 2.5 7B - Advanced instruction following",
        "Qwen/Qwen2.5-3B-Instruct": "Qwen 2.5 3B - Efficient and smart",
        "Qwen/Qwen2.5-1.5B-Instruct": "Qwen 2.5 1.5B - Fast and responsive",
        "Qwen/Qwen2.5-14B-Instruct": "Qwen 2.5 14B - Powerful and detailed",
        "Qwen/Qwen2.5-32B-Instruct": "Qwen 2.5 32B - Maximum performance",
        "microsoft/DialoGPT-medium": "DialoGPT - Conversational AI",
        "google/flan-t5-large": "FLAN-T5 - Instruction following",
    }
    return descriptions.get(model_name, "Advanced AI model for nutrition guidance")

def main():
    # Main container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🥗 Marcus</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your Personal AI Nutrition Assistant - Powered by Qwen 2.5</p>', unsafe_allow_html=True)
    
    initialize_session_state()
    
    # Get secrets and initialize chatbot
    try:
        api_token, default_model = get_secrets()
        
        # Model selection sidebar
        with st.sidebar:
            st.markdown("### 🤖 Model Selection")
            
            # Flatten all models for selection
            all_models = []
            for category, models in AVAILABLE_MODELS.items():
                all_models.extend(models)
            
            selected_model = st.selectbox(
                "Choose AI Model:",
                all_models,
                index=all_models.index(st.session_state.selected_model) if st.session_state.selected_model in all_models else 0
            )
            
            if selected_model != st.session_state.selected_model:
                st.session_state.selected_model = selected_model
                st.session_state.chatbot = MarcusNutritionChatbot(api_token, selected_model)
                st.success(f"Switched to {selected_model.split('/')[-1]}!")
        
        # Initialize chatbot if not already done
        if st.session_state.chatbot is None or st.session_state.chatbot.model_name != selected_model:
            st.session_state.chatbot = MarcusNutritionChatbot(api_token, selected_model)
            
    except Exception as e:
        st.error("Failed to initialize Marcus. Please check your API configuration.")
        st.stop()
    
    # Model info and controls
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("🔄 Random Model", use_container_width=True):
            # Randomly switch to a different Qwen model
            qwen_models = AVAILABLE_MODELS["Qwen 2.5 Models"]
            current_model = st.session_state.chatbot.model_name
            available_models = [m for m in qwen_models if m != current_model]
            if available_models:
                new_model = random.choice(available_models)
                st.session_state.selected_model = new_model
                st.session_state.chatbot = MarcusNutritionChatbot(api_token, new_model)
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
            st.rerun()
    
    # Quick nutrition topics
    st.markdown("### 🍎 Quick Topics:")
    topic_cols = st.columns(4)
    
    topics = [
        ("🍽️ Meal Planning", "Help me create a balanced meal plan for the week"),
        ("🥗 Recipe Analysis", "Analyze this recipe for nutritional content"),
        ("💪 Sports Nutrition", "What should I eat before and after workouts?"),
        ("🎯 Weight Goals", "Help me with healthy weight management strategies")
    ]
    
    for i, (topic_name, topic_prompt) in enumerate(topics):
        with topic_cols[i]:
            if st.button(topic_name, use_container_width=True):
                # Add the topic as a user message
                st.session_state.messages.append({"role": "user", "content": topic_prompt})
                st.rerun()
    
    # Chat display container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    display_chat_messages()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input(
                "Message",
                placeholder="Ask Marcus about nutrition, meal planning, recipes, or health goals... 🥗",
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
        with st.spinner("🥗 Marcus is preparing your nutrition advice..."):
            try:
                # Get Marcus's nutrition response
                response = st.session_state.chatbot.get_nutrition_response(
                    user_input, 
                    st.session_state.conversation_history
                )
                
                # Add Marcus's response
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.conversation_history.append(f"Marcus: {response}")
                
            except Exception as e:
                error_msg = f"I apologize, but I'm experiencing some technical difficulties. Please try again! 🥗"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        st.rerun()
    
    # Process quick topic if clicked
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_message = st.session_state.messages[-1]["content"]
        
        # Check if it's a topic prompt that needs processing
        topic_prompts = [prompt for _, prompt in topics]
        if last_message in topic_prompts:
            with st.spinner("🥗 Marcus is preparing your nutrition advice..."):
                try:
                    response = st.session_state.chatbot.get_nutrition_response(
                        last_message, 
                        st.session_state.conversation_history[:-1]
                    )
                    
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state.conversation_history.append(f"Marcus: {response}")
                    
                except Exception as e:
                    error_msg = f"I apologize, but I'm experiencing some technical difficulties. Please try again! 🥗"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            
            st.rerun()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>🥗 Marcus - AI Nutrition Assistant • Powered by Qwen 2.5 & Hugging Face 🥗</p>
        <p>💚 Your journey to better health starts with better nutrition choices! 💚</p>
        <p><small>⚠️ Always consult healthcare professionals for serious health concerns</small></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
