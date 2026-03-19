# Architecture Overview

User → Streamlit UI → Python App → Ollama (Local LLM)

## Flow
1. User submits a question
2. App searches local documents
3. Best matching document is selected
4. Context is sent to local AI model (Ollama)
5. Model generates answer based only on that context
6. App displays answer and source document