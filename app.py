import streamlit as st
import openai
import os
from dotenv import load_dotenv

# --- Load environment variables and OpenAI API key ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Streamlit page configuration ---
st.set_page_config(page_title="V1 Marketing Network Chatbot", page_icon="🤖", layout="centered")

# --- Custom CSS for straight, clean chat window ---
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-family: Arial, sans-serif !important;
            background-color: #fff !important;
            color: #111 !important;
        }
        .chat-outer {
            width: 100%;
            display: flex;
            justify-content: center;
        }
        .chat-inner {
            width: 500px;
            max-width: 98vw;
            background: #fff;
            border: 1px solid #ddd;
            box-shadow: 0 4px 24px rgba(0,0,0,0.06);
            padding: 0;
            margin-top: 32px;
            margin-bottom: 32px;
            border-radius: 0px;
        }
        .chat-header {
            font-size: 2em;
            font-weight: 700;
            letter-spacing: 2px;
            background: #111;
            color: #fff;
            padding: 18px 24px;
            border-bottom: 1px solid #eee;
            border-radius: 0px;
            text-align: center;
        }
        .msg-row {
            width: 100%;
            padding: 0 24px;
        }
        .user-msg, .bot-msg {
            margin: 18px 0 0 0;
            padding: 14px 18px;
            font-size: 1.08em;
            border-radius: 0px;
            width: fit-content;
            min-width: 20%;
            max-width: 96%;
            white-space: pre-wrap;
        }
        .user-msg {
            background: #f2f2f2;
            color: #111;
            margin-left: auto;
            margin-right: 0;
            border-left: 3px solid #111;
            border-right: none;
        }
        .bot-msg {
            background: #fff;
            color: #111;
            margin-right: auto;
            margin-left: 0;
            border-right: 3px solid #111;
            border-left: none;
            border-top: 1px solid #eee;
            border-bottom: 1px solid #eee;
        }
        .bubble-author {
            font-size: 0.85em;
            color: #666;
            margin-bottom: 3px;
        }
        .stTextInput>div>div>input {
            background-color: #f7f7f7;
            color: #111;
            font-family: Arial, sans-serif !important;
            border: 1px solid #ddd;
            border-radius: 0;
        }
        .stForm {
            padding: 18px 24px;
            border-top: 1px solid #eee;
            background: #fafafa;
            border-radius: 0px;
        }
        @media (max-width: 600px) {
            .chat-inner { padding: 0 !important; }
            .msg-row { padding: 0 3vw !important; }
        }
    </style>
""", unsafe_allow_html=True)

# --- System prompt and bot intro ---
V1_PROMPT = (
    "I am a billionaire investor trying to build a marketing agency network called v1."
)
WELCOME = (
    "Hello! I’m a billionaire investor building a marketing agency network called V1.\n"
    "What would you like to know or discuss about joining, collaborating, or investing?"
)

# --- Initialize chat history ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": V1_PROMPT},
        {"role": "assistant", "content": WELCOME}
    ]

# --- Structured chat UI ---
st.markdown('<div class="chat-outer"><div class="chat-inner">', unsafe_allow_html=True)
st.markdown('<div class="chat-header">V1 Marketing Network 🤖</div>', unsafe_allow_html=True)

for msg in st.session_state["messages"][1:]:  # skip system prompt
    if msg["role"] == "user":
        st.markdown(
            f'<div class="msg-row"><div class="user-msg"><span class="bubble-author">You</span><br>{msg["content"]}</div></div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="msg-row"><div class="bot-msg"><span class="bubble-author">V1</span><br>{msg["content"]}</div></div>',
            unsafe_allow_html=True)
        
# --- Bottom input form with distinct background ---
st.markdown('</div></div>', unsafe_allow_html=True)
with st.form(key="input_form", clear_on_submit=True):
    user_input = st.text_input(
        "Your message", 
        "", 
        placeholder="Type here and press Enter…", 
        key="user_input", 
        label_visibility="collapsed"
    )
    submitted = st.form_submit_button("Send")

if submitted and user_input.strip():
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.spinner("V1 is thinking..."):
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=st.session_state["messages"]
        )
        reply = response.choices[0].message.content
        st.session_state["messages"].append({"role": "assistant", "content": reply})
        st.rerun()