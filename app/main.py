import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# App title
st.title("Secure AI Knowledge Assistant")

st.write("Ask a question:")

# Input box
user_input = st.text_input("Your question")

# Button click
if st.button("Submit"):
    if user_input:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ]
        )

        answer = response.choices[0].message.content

        st.write("### Answer:")
        st.write(answer)