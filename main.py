import streamlit as st
import requests

# Load secrets
API_TOKEN = st.secrets["huggingface"]["api_token"]
MODEL = st.secrets["huggingface"]["model"]

st.set_page_config(page_title="HF Chatbot", page_icon="🤖")

st.title("🤖 Hugging Face Chatbot")
st.caption(f"Model: `{MODEL}`")

# Session state to store chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input form
user_input = st.chat_input("Type your message here...")

# On user message
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            # Call Hugging Face API
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{MODEL}",
                headers={"Authorization": f"Bearer {API_TOKEN}"},
                json={"inputs": user_input},
            )
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list):
                    reply = result[0]["generated_text"]
                elif "generated_text" in result:
                    reply = result["generated_text"]
                else:
                    reply = "⚠️ Unexpected response format."
            else:
                reply = f"⚠️ Error: {response.status_code} - {response.text}"

            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
