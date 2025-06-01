import streamlit as st
import openai
import os
from dotenv import load_dotenv

# Load OpenAI API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("OpenAI Chatbot 🤖")

user_input = st.text_input("You:")

if user_input:
    with st.spinner("OpenAI is thinking..."):
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        st.write("Bot:", response.choices[0].message.content)
        