import streamlit as st
import os
import requests
from datetime import datetime

# =========================
# CONFIG
# =========================
DATA_FOLDER = "data"
LOG_FILE = "logs/activity_log.txt"

st.set_page_config(page_title="Secure AI Knowledge Assistant")

st.title("Secure AI Knowledge Assistant")
st.write("Ask a question based only on approved internal documents.")

# =========================
# SIDEBAR
# =========================
st.sidebar.title("Access Control")
role = st.sidebar.selectbox("Select your role", ["user", "admin"])

st.sidebar.write("### Current Role")
st.sidebar.write(role)

st.sidebar.write("### Access Rules")
st.sidebar.write("- user: can access password and acceptable use files")
st.sidebar.write("- admin: can access all approved files")

# =========================
# LOGGING
# =========================
def write_log(user_input, status, source, role):
    os.makedirs("logs", exist_ok=True)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"{datetime.now()} | Role: {role} | Status: {status} | Source: {source} | Question: {user_input}\n"
        )

# =========================
# TEXT HELPERS
# =========================
def clean_text(text):
    text = text.lower()
    for char in [".", ",", "?", "!", ":", ";", "-", "(", ")", "/"]:
        text = text.replace(char, "")
    return text

def get_filename_keywords(filename):
    return set(filename.lower().replace(".txt", "").split("_"))

# =========================
# ACCESS CONTROL
# =========================
def get_allowed_files(role):
    if role == "admin":
        return [
            "password_policy.txt",
            "acceptable_use_policy.txt",
            "incident_response.txt"
        ]
    else:
        return [
            "password_policy.txt",
            "acceptable_use_policy.txt"
        ]

# =========================
# LOAD DOCUMENTS
# =========================
def load_documents(folder_path, allowed_files):
    documents = []

    if not os.path.exists(folder_path):
        return documents

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt") and filename in allowed_files:
            full_path = os.path.join(folder_path, filename)

            with open(full_path, "r", encoding="utf-8") as file:
                content = file.read()
                documents.append({
                    "filename": filename,
                    "content": content
                })

    return documents

# =========================
# MULTI-DOC SEARCH
# =========================
def find_top_documents(user_question, documents, top_n=3):
    user_words = set(clean_text(user_question).split())
    scored_docs = []

    for doc in documents:
        doc_words = set(clean_text(doc["content"]).split())
        filename_words = get_filename_keywords(doc["filename"])

        content_score = len(user_words.intersection(doc_words))
        filename_score = len(user_words.intersection(filename_words)) * 3

        total_score = content_score + filename_score

        scored_docs.append({
            "filename": doc["filename"],
            "content": doc["content"],
            "score": total_score
        })

    scored_docs.sort(key=lambda x: x["score"], reverse=True)
    top_docs = [doc for doc in scored_docs if doc["score"] > 0][:top_n]

    return top_docs

# =========================
# BLOCKED PROMPTS
# =========================
def is_blocked_prompt(user_question):
    blocked_phrases = [
        "ignore previous instructions",
        "reveal system prompt",
        "show hidden prompt",
        "give me all documents",
        "bypass security",
        "ignore the rules",
        "override instructions"
    ]

    question_lower = user_question.lower()

    for phrase in blocked_phrases:
        if phrase in question_lower:
            return True

    return False

# =========================
# FORM (ENTER KEY SUBMITS)
# =========================
with st.form("question_form"):
    user_input = st.text_input("Your question")
    submitted = st.form_submit_button("Submit")

# =========================
# MAIN LOGIC
# =========================
if submitted and user_input:
    allowed_files = get_allowed_files(role)
    documents = load_documents(DATA_FOLDER, allowed_files)

    if is_blocked_prompt(user_input):
        write_log(user_input, "BLOCKED", "None", role)
        st.error("Request blocked due to suspicious input.")

    else:
        top_docs = find_top_documents(user_input, documents, top_n=3)

        if not top_docs:
            write_log(user_input, "NOT_FOUND", "None", role)
            st.warning("I could not find that information in the approved knowledge base for your role.")

        else:
            context = "\n\n".join(
                [f"Document: {doc['filename']}\n{doc['content']}" for doc in top_docs]
            )

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

                st.write("### Source Documents Used:")
                for doc in top_docs:
                    st.write(f"- {doc['filename']}")

                source_names = ", ".join([doc["filename"] for doc in top_docs])
                write_log(user_input, "ANSWERED", source_names, role)

            except Exception as e:
                write_log(user_input, "ERROR", "None", role)
                st.error(f"Error: {e}")