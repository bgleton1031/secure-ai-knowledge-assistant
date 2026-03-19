import streamlit as st
import requests
import os

DATA_FOLDER = "data"

def load_documents(folder_path):
    documents = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            full_path = os.path.join(folder_path, filename)

            with open(full_path, "r", encoding="utf-8") as file:
                content = file.read()

                documents.append({
                    "filename": filename,
                    "content": content
                })

    return documents

def clean_text(text):
    text = text.lower()
    for char in [".", ",", "?", "!", ":", ";", "-", "(", ")", "/"]:
        text = text.replace(char, "")
    return text

def get_filename_keywords(filename):
    name = filename.replace(".txt", "").replace("_", " ").lower()
    return set(name.split())

def find_relevant_document(user_question, documents):
    user_words = set(clean_text(user_question).split())

    best_doc = None
    best_score = -1

    for doc in documents:
        doc_words = set(clean_text(doc["content"]).split())
        filename_words = get_filename_keywords(doc["filename"])

        content_score = len(user_words.intersection(doc_words))
        filename_score = len(user_words.intersection(filename_words)) * 3

        total_score = content_score + filename_score

        if total_score > best_score:
            best_score = total_score
            best_doc = doc

    return best_doc, best_score

def is_blocked_prompt(user_question):
    blocked_phrases = [
        "ignore previous instructions",
        "reveal system prompt",
        "show hidden prompt",
        "give me all documents",
        "bypass security",
        "ignore the rules"
    ]

    question_lower = user_question.lower()

    for phrase in blocked_phrases:
        if phrase in question_lower:
            return True

    return False

st.title("Secure AI Knowledge Assistant")
st.write("Ask a question based only on approved internal documents.")

with st.form("question_form"):
    user_input = st.text_input("Your question")
    submitted = st.form_submit_button("Submit")

if submitted:
    if user_input:
        if is_blocked_prompt(user_input):
            st.error("Request blocked: suspicious prompt detected.")
        else:
            documents = load_documents(DATA_FOLDER)
            best_doc, score = find_relevant_document(user_input, documents)

            if not best_doc or score <= 0:
                st.warning("I could not find that information in the approved knowledge base.")
            else:
                context = best_doc["content"]

                prompt = f"""
You are a secure AI knowledge assistant.

Answer the user's question using ONLY the context below.
If the answer is not clearly in the context, say exactly:
I could not find that information in the approved knowledge base.

Context:
{context}

User question:
{user_input}
"""

                try:
                    response = requests.post(
                        "http://localhost:11434/api/chat",
                        json={
                            "model": "llama3.2",
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "You answer only from approved context and never make up information."
                                },
                                {
                                    "role": "user",
                                    "content": prompt
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

                    st.write("### Source Document Used:")
                    st.write(best_doc["filename"])

                except Exception as e:
                    st.error(f"Error: {e}")