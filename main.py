import streamlit as st
import requests

st.set_page_config(page_title="HF Chatbot", layout="centered")
st.title("🤖 Chat with Hugging Face Models")

# Get token from Streamlit Secrets
HF_TOKEN = st.secrets["hf_token"]

# Model selector
MODEL_OPTIONS = {
    "LLaMA 2 7B Chat": "meta-llama/Llama-2-7b-chat-hf",
    "Mistral Instruct": "mistralai/Mistral-7B-Instruct-v0.2",
    "Falcon 7B Instruct": "tiiuae/falcon-7b-instruct",
    "Phi-2": "microsoft/Phi-2",
    "Gemma 2B IT": "google/gemma-1.1-2b-it",
    "OpenChat 3.5": "openchat/openchat-3.5-1210"
}

selected_model_name = st.selectbox("Choose a model", list(MODEL_OPTIONS.keys()))
model_id = MODEL_OPTIONS[selected_model_name]

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# Display previous messages
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Say something...")
if user_input:
    # Show user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Prepare payload for Hugging Face Inference API
    payload = {
        "inputs": {
            "past_user_inputs": [m["content"] for m in st.session_state.messages if m["role"] == "user"],
            "generated_responses": [m["content"] for m in st.session_state.messages if m["role"] == "assistant"],
            "text": user_input
        }
    }

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }

    # Send request
    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model_id}",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        output = response.json()
        if isinstance(output, dict) and "generated_text" in output:
            reply = output["generated_text"]
        elif isinstance(output, list) and "generated_text" in output[0]:
            reply = output[0]["generated_text"]
        else:
            reply = "⚠️ Model did not return a proper response."

    except Exception as e:
        reply = f"❌ Error: {str(e)}"

    # Show assistant reply
    st.chat_message("assistant").markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
