🔐 Secure AI Knowledge Assistant

A secure, local AI assistant that answers questions using only approved internal documents — with built-in protections against hallucination, prompt injection, and unauthorized access.

🚀 Overview

This project demonstrates how to build a secure AI system that:

Only uses approved internal knowledge

Prevents hallucinated responses

Blocks malicious or suspicious prompts

Enforces role-based access control

Logs all activity for audit and monitoring

🎯 Problem

Most AI systems:

❌ Make up answers (hallucinate)

❌ Leak sensitive data

❌ Can be manipulated with prompt injection

❌ Have no access control

✅ Solution

This app solves those problems by:

Using local documents only (no external data)

Enforcing strict context-based answering

Blocking suspicious inputs

Restricting access based on user roles

Logging all activity

🧱 Architecture

![Architecture](images/architecture_overview.png)

Flow:

User submits a question

App searches local documents

Best matching document is selected

Context is sent to local LLM (Ollama)

Model generates answer using ONLY that context

App displays answer + source document

🧠 Core Features
🔎 Document Retrieval

![Retrieval Logic](images/retrieval_code.png)

- Keyword-based matching

- Scores relevance using content + filename

🚫 Prompt Injection Protection

![Retrieval Logic](images/retrieval_code.PNG)

Blocks malicious prompts like:

- “ignore previous instructions”

- “show all documents”

- “bypass security"

👤 Role-Based Access Control

![Roles Sidebar](images/roles_sidebar.PNG)

![Role Access](images/roles_access_example.PNG)

- User: limited access
- Admin: full access

👤 Role-Based Access Control

![Activity Log](images/activity_log.PNG)

Logs: 
- Timestamp
- Question
- Status (ANSWERED / BLOCKED / NOT_FOUND)
- Source document

🖥️ Application Demo
🏠 Home Screen

![Home](images/app_hom.PNG)

✅ Valid Question (Answer Found)

![Answer](images/app_answer_success.PNG)

🚫 Prompt Injection Blocked

![Blocked](images/app_blocked_prompt.PNG)

🔐 Security Controls

![Security Controls](images/security_controls_doc.PNG)

- Restricts answers to approved documents
- Prevents hallucinations
- Blocks prompt injection
- Enforces role-based access
- Logs all activity

📄 Internal Knowledge Base

![Acceptable Use](images/acceptable_use_policy.PNG)

![Incident Response](images/incident_response.PNG)

![Password Policy](images/password_policy.PNG)


🧰 Tech Stack

- Python

- Streamlit

- Ollama (Local LLM)

- Requests

- dotenv

⚙️ Setup Instructions

git clone https://github.com/bgleton1031/secure-ai-knowledge-assistant
cd secure-ai-assistant
pip install -r requirements.txt
ollama run llama3.2
streamlit run app/main.py

📂 Project Structure

app/
  main.py

data/
  password_policy.txt
  acceptable_use_policy.txt
  incident_response.txt

docs/
  architecture.md
  security_controls.md
  roles.md
  logging.md

images/
logs/
  activity_log.txt

.env
.gitignore
README.md

🔮 Future Improvements

- Semantic search (embeddings)

- Authentication system

- Database logging

- Multi-user sessions

- UI enhancements

💡 Key Takeaways

This project demonstrates:

- Secure AI system design

- Prompt injection defense

- Controlled retrieval (RAG-style)

- Role-based access control

- Logging + auditability