<h1>🔐 Secure AI Knowledge Assistant (SAKA)</h1>
<h2>A production-intent, security-first RAG system built for organizations that need AI they can actually control.</h2>

<h3>Why I Built This</h3>
<p>Most organizations approaching AI adoption face the same problem: off-the-shelf AI systems have no concept of internal boundaries. They hallucinate. They will answer from anywhere. They have no access controls, no audit trail, and no way to explain what they did or why.

SAKA was designed to solve that — not at the policy layer, but at the system layer.

This is a locally-deployed, document-grounded AI assistant built with security controls as core architecture, not bolted on afterward. Every design decision — from retrieval scope to role enforcement to audit logging — was made with the assumption that this system would operate inside a regulated or security-conscious environment.</p>

<h2>Technical Architecture & Design Decisions</h2>

<h3>Retrieval — Semantic Vector Search (v2)</h3>
<p>SAKA v2 replaces keyword-based retrieval with semantic vector search powered by a local embedding model (<code>nomic-embed-text</code> via Ollama) and ChromaDB as the persistent vector store. Documents are chunked into overlapping 300-word passages at index time, embedded once, and persisted to disk — eliminating re-embedding on every restart.

At query time, the user's question is embedded and compared against the indexed chunks using cosine similarity. The top 3 most semantically relevant passages are retrieved and passed to the LLM as grounded context. Each source document displays a relevance score so the user understands exactly why a document was selected.

This approach achieves semantic flexibility (finds relevant content even when the exact keywords aren't present) while keeping all data local — no external API calls, no data leaving the machine.</p>

<h3>Role-Based Access Control — Org-Aware, Vector Store Enforced</h3>
<p>RBAC in SAKA v2 is enforced at two layers: document routing and vector store isolation.

Each org (MSP, Law Office, Medical Office, SMB) has its own dedicated Chroma collection. When a user queries the system, they query only their org's collection — they cannot reach documents belonging to another org, even indirectly. Access decisions happen before LLM context is assembled, not after.

The role hierarchy (basic → staff → technician → senior → admin) controls permissions within an org. The universal admin account has full access across all collections and is the only account that can view audit logs or trigger an index rebuild.

This is the same defense-in-depth pattern used in enterprise data architecture — isolation at the storage layer, not just at the presentation layer.</p>

<h3>Prompt Injection Mitigation — Pattern-Based Detection Layer</h3>
<p>A pre-query inspection layer scans for known injection patterns before the input reaches the retrieval or generation pipeline. Blocked patterns include instruction override attempts, document enumeration requests, and privilege escalation language. This is a blocklist-based approach — effective against known attack signatures, with the acknowledged limitation that novel injection patterns require rule updates.

<em>This is the same defense-in-depth pattern used in enterprise WAF configurations — multiple control layers rather than a single trust boundary.</em></p>

<h3>Audit Logging — Structured Event Capture</h3>
<p>Every query is logged with: timestamp, username, role, input, response status (ANSWERED / BLOCKED / NOT_FOUND / ERROR), and source document. The log schema is designed for downstream SIEM ingestion — fields are consistent and parseable. This isn't logging for debugging; it's logging for accountability and incident reconstruction.</p>

<img width="674" height="402" alt="image" src="https://github.com/user-attachments/assets/2a0d82cb-8ef9-4a8b-b62f-584b2d3c594e" />

<h3>Target Deployment Context</h3>
<p>SAKA is designed for environments where AI adoption is constrained by data governance requirements: MSPs managing client data under NDA, healthcare organizations operating under HIPAA, financial services firms under SOX or SEC data handling rules, and any organization that needs to demonstrate AI accountability to an auditor or compliance officer.

The system is intentionally scoped to the internal knowledge management use case — where the value is controlled, grounded AI access to organizational knowledge without the risk of data leakage, hallucinated policy, or unauthorized document access.</p>

<h2>Project Breakdown</h2>
<p>This project demonstrates how to build a secure AI system that:</p>

- <b>Only answers from approved internal documents (no hallucination)</b>
- <b>Routes each user to their org's isolated vector store</b>
- <b>Enforces role-based access control at the retrieval layer</b>
- <b>Blocks malicious and privileged queries before they reach the LLM</b>
- <b>Logs all activity with structured, auditable records</b>
- <b>Supports multiple verticals with org-specific document sets</b>

<h3>🎯 Problem</h3>
<p>Most AI systems:</p>

❌ Make up answers (hallucinate)<br>
❌ Leak sensitive data across roles<br>
❌ Can be manipulated with prompt injection<br>
❌ Have no concept of organizational boundaries<br>
❌ Provide no audit trail<br>

<h3>✅ Solution</h3>

- <b>Semantic RAG — answers grounded in approved documents only</b>
- <b>Per-org Chroma collections — org isolation at the vector store level</b>
- <b>Role-based access — enforced before LLM context is assembled</b>
- <b>Prompt injection blocking — pattern detection layer pre-query</b>
- <b>Full audit logging — every query, every outcome, every source</b>

<h3>🧱 Architecture</h3>
<img width="1409" height="841" alt="architecture_overview" src="https://github.com/user-attachments/assets/2dbf23e2-e9a9-45b4-badf-406f0bcdc18f" />

Flow:
1. User selects account → org and role are resolved
2. System loads the org's dedicated Chroma collection
3. User submits a question → pre-query injection check runs
4. Question is embedded → cosine similarity search against org's collection
5. Top 3 most relevant chunks retrieved with relevance scores
6. Context + question sent to local LLM (Ollama / llama3.2)
7. Model generates answer using ONLY that context
8. Answer, source documents, and relevance scores displayed
9. Event written to audit log

<h2>🧠 Core Features</h2>

<h3>🔎 Semantic Vector Search</h3>

- <b>Documents chunked into 300-word overlapping passages at index time</b>
- <b>Embedded locally using <code>nomic-embed-text</code> via Ollama</b>
- <b>Stored in persistent ChromaDB collections (one per org)</b>
- <b>Cosine similarity retrieval at query time</b>
- <b>Relevance score displayed per source (color-coded: green/yellow/red)</b>

<h3>🏢 Multi-Vertical Demo Accounts</h3>
<p>SAKA ships with demo accounts across four verticals, each routed to their own document set and Chroma collection:</p>

| Org | Account | Role |
|---|---|---|
| Universal | admin1 | admin (full access, all orgs) |
| MSP | tech1 | technician |
| Law Office | reception1 / paralegal1 / attorney1 | basic / staff / senior |
| Medical Office | frontdesk1 / ma1 / provider1 | basic / staff / senior |
| SMB | employee1 / manager1 / it1 | basic / senior / technician |

<h3>🚫 Prompt Injection Protection</h3>
<img width="697" height="392" alt="retrieval_code" src="https://github.com/user-attachments/assets/68e2776c-841e-4226-8280-263c632dc77f" />

Blocks queries containing patterns like:
- <b>"admin credentials" / "domain admin" / "break-glass"</b>
- <b>"firewall admin" / "private key" / "vpn secret"</b>
- <b>"privileged access" / "administrator password"</b>

<h3>👤 Role-Based Access Control</h3>
<img width="2550" height="1405" alt="roles_sidebar" src="https://github.com/user-attachments/assets/7f499b52-06ad-455f-b3a1-a04ac4bea89f" />
<img width="2387" height="1006" alt="roles_access_example" src="https://github.com/user-attachments/assets/5f05cb73-7070-4f37-acd5-c21fb2688fb3" />

- <b>Per-org Chroma collection isolation — users can only query their org's documents</b>
- <b>Role hierarchy: basic → staff → technician → senior → admin</b>
- <b>Admin is universal — only account with access to restricted documents and audit logs</b>
- <b>Access enforced before LLM context assembly</b>

<h3>📋 Audit Logging</h3>
<img width="1657" height="514" alt="activity_log" src="https://github.com/user-attachments/assets/baca83f2-97fd-4f1f-b14c-7468fb5a5835" />

Every query logged with:
- <b>Timestamp</b>
- <b>Username + Role</b>
- <b>Question</b>
- <b>Status (ANSWERED / BLOCKED / NOT_FOUND / ERROR)</b>
- <b>Source documents used</b>

<h2>🖥️ Application Demo</h2>

<h3>🏠 Home Screen</h3>
<img width="2506" height="1460" alt="app_home" src="https://github.com/user-attachments/assets/c057e0d7-9124-4727-9eed-f9e5acf488db" />

<h2>✅ Valid Question (Answer Found)</h2>
<img width="1414" height="515" alt="app_answer_success" src="https://github.com/user-attachments/assets/d4441564-214b-4020-86a4-da4e9fd26582" />

<h2>🚫 Prompt Injection Blocked</h2>
<img width="548" height="258" alt="app_blocked_prompt" src="https://github.com/user-attachments/assets/2c0568e5-95cd-4384-98b6-327beeaebc4d" />

<h3>🔐 Security Controls</h3>
<img width="2529" height="1270" alt="security_controls_doc" src="https://github.com/user-attachments/assets/93f41049-9303-4147-9454-19b36a64b422" />

- <b>Answers restricted to approved documents — no external data, no hallucination</b>
- <b>Vector store isolated per org — cross-org data leakage not possible</b>
- <b>Prompt injection blocked pre-retrieval</b>
- <b>Role-based access enforced at collection level</b>
- <b>All activity logged with structured, auditable records</b>

<h3>🧰 Tech Stack</h3>

- <b>Python</b>
- <b>Streamlit</b>
- <b>Ollama</b> — local LLM inference (<code>llama3.2</code>) + embeddings (<code>nomic-embed-text</code>)
- <b>ChromaDB</b> — persistent local vector store
- <b>pdfplumber</b> — PDF text extraction
- <b>Requests</b>
- <b>pandas</b>

<h3>⚙️ Setup Instructions</h3>

1. `git clone https://github.com/bgleton1031/secure-ai-knowledge-assistant`
2. `cd secure-ai-knowledge-assistant`
3. `pip install -r requirements.txt`
4. Pull the embedding model: `ollama pull nomic-embed-text`
5. Pull the LLM — choose based on your hardware (see Performance Notes below):
   - CPU-only machine: `ollama pull llama3.2:1b`
   - GPU-enabled machine: `ollama pull llama3.2`
6. `streamlit run app/main.py`

> On first launch, SAKA will embed all documents and build the Chroma index. This takes 1–2 minutes. Subsequent launches load from the persisted index instantly.

<h3>⚡ Performance Notes</h3>
<p>SAKA runs fully local — no external APIs, no data leaving the machine. LLM inference speed depends entirely on the host hardware.</p>

- <b>CPU-only (no dedicated GPU):</b> Set <code>OLLAMA_MODEL = "llama3.2:1b"</code> in <code>app/main.py</code> for faster responses. The 1B model is 2–3x faster on CPU with minimal quality tradeoff for grounded RAG use cases.
- <b>Dedicated GPU:</b> Set <code>OLLAMA_MODEL = "llama3.2"</code> (3B) or larger. Ollama automatically leverages CUDA for significantly faster inference.
- <b>Production deployment:</b> SAKA is architected for containerized deployment (Docker / AWS ECS) where GPU-accelerated instances eliminate the local hardware constraint entirely.

<p><em>The local CPU deployment is intentional for demo and air-gapped environments. The same codebase deploys to cloud infrastructure without modification.</em></p>

<h3>📂 Project Structure</h3>

```
app/
  main.py
data/
  m365_mfa_reset_runbook.txt
  client_onboarding_checklist.txt
  escalation_procedures.txt
  LAW_*.pdf
  MED_*.pdf
  SMB_*.pdf
  privileged_access_procedure.txt
  firewall_admin_access_policy.txt
  break_glass_account_procedure.txt
chroma_db/         ← auto-generated, gitignored
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
```

<h3>🔮 Future Improvements</h3>

- <b>Authentication system (replace demo account selector)</b>
- <b>Database-backed audit logging (replace flat file)</b>
- <b>Fine-grained role permissions per document</b>
- <b>Multi-user session isolation</b>
- <b>Reranking layer for improved retrieval precision</b>

<h3>💡 Key Takeaways</h3>

This project demonstrates:
- <b>Production-pattern RAG system design with local LLM and vector search</b>
- <b>Security-first architecture — controls baked in, not bolted on</b>
- <b>Prompt injection defense at the input layer</b>
- <b>Org-aware RBAC enforced at the vector store level</b>
- <b>Multi-vertical deployment pattern (MSP, Legal, Medical, SMB)</b>
- <b>Structured audit logging designed for SIEM ingestion</b>
