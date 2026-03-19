import streamlit as st
import requests

st.title("Secure AI Knowledge Assistant")
st.write("Ask a question:")

user_input = st.text_input("Your question")

if st.button("Submit"):
    if user_input:
        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "llama3.2",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant."
                        },
                        {
                            "role": "user",
                            "content": user_input
                        }
                    ],
                    "stream": False
                },
                timeout=300
            )

            response.raise_for_status()
            data = response.json()
            answer = data["message"]["content"]

            st.write("### Answer:")
            st.write(answer)

        except Exception as e:
            st.error(f"Error: {e}")