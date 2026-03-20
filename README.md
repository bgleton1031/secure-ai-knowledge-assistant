<h1>🔐 Secure AI Knowledge Assistant</h1>

<h2>A secure, local AI assistant that answers questions using only approved internal documents — with built-in protections against hallucination, prompt injection, and unauthorized access.</h2>

<h3>🚀 Overview</h3>

<p>This project demonstrates how to build a secure AI system that:</p>

- <b>Only uses approved internal knowledge</b>

- <b>Prevents hallucinated responses</b>

- <b>Blocks malicious or suspicious prompts</b>

- <b>Enforces role-based access control</b>

- <b>Logs all activity for audit and monitoring</b>

<h3>🎯 Problem</h3>

<p>Most AI systems:</p>

❌ Make up answers (hallucinate)

❌ Leak sensitive data

❌ Can be manipulated with prompt injection

❌ Have no access control

<h3>✅ Solution</h3>

This app solves those problems by:

- <b>Using local documents only (no external data)</b>

- <b>Enforcing strict context-based answering</b>

- <b>Blocking suspicious inputs</b>

- <b>Restricting access based on user roles</b>

- <b>Logging all activity</b>

<h3>🧱 Architecture</h3>

<img width="1409" height="841" alt="architecture_overview" src="https://github.com/user-attachments/assets/2dbf23e2-e9a9-45b4-badf-406f0bcdc18f" />


Flow:

User submits a question

App searches local documents

Best matching document is selected

Context is sent to local LLM (Ollama)

Model generates answer using ONLY that context

App displays answer + source document

<h2>🧠 Core Features</h2>
<h3>🔎 Document Retrieval</h3>

<img width="697" height="392" alt="retrieval_code" src="https://github.com/user-attachments/assets/f5a683a3-af78-4482-9a1f-15983e810751" />

- <b>Keyword-based matching</b>

- <b>Scores relevance using content + filename</b>

<h3>🚫 Prompt Injection Protection</h3>

<img width="697" height="392" alt="retrieval_code" src="https://github.com/user-attachments/assets/68e2776c-841e-4226-8280-263c632dc77f" />

Blocks malicious prompts like:

- <b>“ignore previous instructions”</b>

- <b>“show all documents”</b>

- <b>“bypass security"</b>

<h3>👤 Role-Based Access Control</h3>

<img width="2550" height="1405" alt="roles_sidebar" src="https://github.com/user-attachments/assets/7f499b52-06ad-455f-b3a1-a04ac4bea89f" />

<img width="2387" height="1006" alt="roles_access_example" src="https://github.com/user-attachments/assets/5f05cb73-7070-4f37-acd5-c21fb2688fb3" />

- <b>User: limited access</b>
- <b>Admin: full access</b>

<h3>👤 Role-Based Access Control</h3>

<img width="1657" height="514" alt="activity_log" src="https://github.com/user-attachments/assets/baca83f2-97fd-4f1f-b14c-7468fb5a5835" />

Logs: 
- <b>Timestamp</b>
- <b>Question</b>
- <b>Status (ANSWERED / BLOCKED / NOT_FOUND)</b>
- <b>Source document</b>

<h2>🖥️ Application Demo</h2>
<h3>🏠 Home Screen</h3>

<img width="2506" height="1460" alt="app_hom" src="https://github.com/user-attachments/assets/c057e0d7-9124-4727-9eed-f9e5acf488db" />

<h2>✅ Valid Question (Answer Found)</h3>

<img width="1414" height="515" alt="app_answer_success" src="https://github.com/user-attachments/assets/d4441564-214b-4020-86a4-da4e9fd26582" />

<h2>🚫 Prompt Injection Blocked</h3>

<img width="548" height="258" alt="app_blocked_prompt" src="https://github.com/user-attachments/assets/2c0568e5-95cd-4384-98b6-327beeaebc4d" />

<h3>🔐 Security Controls</h3>

<img width="2529" height="1270" alt="security_controls_doc" src="https://github.com/user-attachments/assets/93f41049-9303-4147-9454-19b36a64b422" />

- <b>Restricts answers to approved documents</b>
- <b>Prevents hallucinations</b>
- <b>Blocks prompt injection</b>
- <b>Enforces role-based access</b>
- <b>Logs all activity</b>

<h3>📄 Internal Knowledge Base</h3>

<img width="1627" height="1322" alt="acceptable_use_policy" src="https://github.com/user-attachments/assets/e0961d8a-e22b-4af0-a319-ded592f6d39c" />

<img width="1617" height="1287" alt="incident_response" src="https://github.com/user-attachments/assets/dd4e0b3f-bb19-4fce-a194-05e386cf740e" />

<img width="1819" height="1107" alt="password_policy" src="https://github.com/user-attachments/assets/bce9257f-f5d8-42f6-9b1b-4d8b3a3a4722" />


<h3>🧰 Tech Stack</h3>

- <b>Python</b>

- <b>Streamlit</b>

- <b>Ollama (Local LLM)</b>

- <b>Requests</b>

- <b>dotenv</b>

<h3>⚙️ Setup Instructions</h3>

1. <n>git clone https://github.com/bgleton1031/secure-ai-knowledge-assistant</n>
2. <n>cd secure-ai-assistant</n>
3. <n>pip install -r requirements.txt</n>
4. <n>ollama run llama3.2</n>
5. <n>streamlit run app/main.py</n>

<h3>📂 Project Structure</h3>

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

<h3>🔮 Future Improvements</h3>

- <b>Semantic search (embeddings)</b>

- <b>Authentication system</b>

- <b>Database logging</b>

- <b>Multi-user sessions</b>

- <b>UI enhancements</b>

<h3>💡 Key Takeaways</h3>

This project demonstrates:

- <b>Secure AI system design</b>

- <b>Prompt injection defense</b>

- <b>Controlled retrieval (RAG-style)</b>

- <b>Role-based access control</b>

- <b>Logging + auditability</b>
