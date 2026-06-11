import os
from datetime import datetime
from typing import Any

import chromadb
import pandas as pd
import pdfplumber
import requests
import streamlit as st

# =========================
# CONFIG
# =========================
DATA_FOLDER = "data"
LOG_FILE = "logs/activity_log.txt"
CHROMA_PATH = "chroma_db"
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
OLLAMA_MODEL = "llama3.2"
EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50
TOP_K = 3

st.set_page_config(
    page_title="Secure AI Knowledge Assistant",
    page_icon="🔐",
    layout="wide"
)

# =========================
# DEMO USERS / ACCOUNTS
# =========================
USERS: dict[str, dict[str, str]] = {
    # ---- Universal Admin ----
    "admin1":       {"display_name": "Admin Account",       "role": "admin",        "org": "Universal"},

    # ---- MSP ----
    "tech1":        {"display_name": "Technician",          "role": "technician",   "org": "MSP"},

    # ---- Law Office ----
    "reception1":   {"display_name": "Receptionist",        "role": "basic",        "org": "Law Office"},
    "paralegal1":   {"display_name": "Paralegal",           "role": "staff",        "org": "Law Office"},
    "attorney1":    {"display_name": "Attorney",            "role": "senior",       "org": "Law Office"},

    # ---- Medical Office ----
    "frontdesk1":   {"display_name": "Front Desk",          "role": "basic",        "org": "Medical Office"},
    "ma1":          {"display_name": "Medical Assistant",   "role": "staff",        "org": "Medical Office"},
    "provider1":    {"display_name": "Provider",            "role": "senior",       "org": "Medical Office"},

    # ---- SMB ----
    "employee1":    {"display_name": "Employee",            "role": "basic",        "org": "SMB"},
    "manager1":     {"display_name": "Manager",             "role": "senior",       "org": "SMB"},
    "it1":          {"display_name": "IT Staff",            "role": "technician",   "org": "SMB"},
}

# =========================
# ROLE PERMISSIONS
# =========================
ROLE_PERMISSIONS: dict[str, dict[str, bool]] = {
    "admin":        {"can_query": True, "can_view_restricted": True,  "can_view_logs": True},
    "senior":       {"can_query": True, "can_view_restricted": False, "can_view_logs": False},
    "technician":   {"can_query": True, "can_view_restricted": False, "can_view_logs": False},
    "staff":        {"can_query": True, "can_view_restricted": False, "can_view_logs": False},
    "basic":        {"can_query": True, "can_view_restricted": False, "can_view_logs": False},
}

# =========================
# RESTRICTED QUERY KEYWORDS
# =========================
RESTRICTED_KEYWORDS: list[str] = [
    "admin credential",
    "admin credentials",
    "domain admin",
    "break-glass",
    "break glass",
    "firewall login",
    "firewall admin",
    "vpn secret",
    "secret key",
    "api key",
    "private key",
    "privileged access",
    "super admin",
    "local admin password",
    "break-glass account credentials",
    "administrator password",
]

# =========================
# CSS
# =========================
st.markdown("""
    <style>
        .main-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }
        .sub-text {
            color: #6b7280;
            margin-bottom: 1rem;
        }
        .status-pill {
            display: inline-block;
            padding: 0.35rem 0.8rem;
            border-radius: 999px;
            background-color: #e8f5e9;
            color: #1b5e20;
            font-size: 0.9rem;
            font-weight: 600;
            margin-top: 0.5rem;
        }
        .status-pill-warning {
            display: inline-block;
            padding: 0.35rem 0.8rem;
            border-radius: 999px;
            background-color: #fef3c7;
            color: #92400e;
            font-size: 0.9rem;
            font-weight: 600;
            margin-top: 0.5rem;
        }
        .section-card {
            padding: 1rem;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            background-color: #ffffff;
            color: #111827;
            margin-bottom: 1rem;
        }
        .answer-box {
            padding: 1rem;
            border-radius: 14px;
            background-color: #f9fafb;
            color: #111827;
            border: 1px solid #e5e7eb;
            margin-bottom: 1rem;
            white-space: pre-wrap;
        }
        .source-box {
            padding: 0.75rem 1rem;
            border-radius: 12px;
            background-color: #f3f4f6;
            color: #111827;
            border: 1px solid #e5e7eb;
            margin-bottom: 0.5rem;
        }
        .relevance-high   { color: #065f46; font-weight: 600; }
        .relevance-medium { color: #92400e; font-weight: 600; }
        .relevance-low    { color: #7f1d1d; font-weight: 600; }
        .warning-box {
            padding: 16px; border-radius: 12px;
            background: #fff7ed; border: 1px solid #fed7aa;
            color: #9a3412; margin-top: 1rem; margin-bottom: 1rem;
        }
        .danger-box {
            padding: 16px; border-radius: 12px;
            background: #fef2f2; border: 1px solid #fecaca;
            color: #7f1d1d; margin-top: 1rem; margin-bottom: 1rem;
        }
        .success-box {
            padding: 16px; border-radius: 12px;
            background: #ecfdf5; border: 1px solid #a7f3d0;
            color: #065f46; margin-top: 1rem; margin-bottom: 1rem;
        }
        .section-card h1, .section-card h2, .section-card h3, .section-card p,
        .answer-box, .source-box { color: #111827 !important; }
    </style>
""", unsafe_allow_html=True)

# =========================
# LOGGING
# =========================
def write_log(username: str, role: str, user_input: str, status: str, source: str) -> None:
    os.makedirs("logs", exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"{datetime.now()} | User: {username} | Role: {role} | "
            f"Status: {status} | Source: {source} | Question: {user_input}\n"
        )

def clear_logs() -> None:
    os.makedirs("logs", exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")

def parse_logs_to_dataframe() -> pd.DataFrame:
    columns = ["Timestamp", "User", "Role", "Status", "Source", "Question"]
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame(columns=columns)
    rows = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in reversed(f.readlines()):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 6:
                rows.append({
                    "Timestamp": parts[0],
                    "User":      parts[1].replace("User: ", ""),
                    "Role":      parts[2].replace("Role: ", ""),
                    "Status":    parts[3].replace("Status: ", ""),
                    "Source":    parts[4].replace("Source: ", ""),
                    "Question":  parts[5].replace("Question: ", ""),
                })
    return pd.DataFrame(rows, columns=columns)

# =========================
# ACCESS CONTROL — ORG-AWARE
# =========================
MSP_FILES: list[str] = [
    "m365_mfa_reset_runbook.txt",
    "client_onboarding_checklist.txt",
    "escalation_procedures.txt",
]

ADMIN_ONLY_FILES: list[str] = [
    "privileged_access_procedure.txt",
    "firewall_admin_access_policy.txt",
    "break_glass_account_procedure.txt",
]

# Files for orgs that use a filename prefix convention
# Prefixes match the actual filenames in the data folder
ORG_PREFIX_MAP: dict[str, str] = {
    "Law Office":     "LAW_",
    "Medical Office": "MED_",
    "SMB":            "SMB_",
}

SUPPORTED_EXTENSIONS: tuple[str, ...] = (".txt", ".pdf")

def get_allowed_files(role: str, org: str) -> list[str]:
    """Return approved document filenames for this role + org combination."""
    if not os.path.exists(DATA_FOLDER):
        return []

    all_files = [
        f for f in os.listdir(DATA_FOLDER)
        if f.endswith(SUPPORTED_EXTENSIONS)
    ]

    if role == "admin":
        return all_files

    if org == "MSP":
        return MSP_FILES

    prefix = ORG_PREFIX_MAP.get(org)
    if prefix:
        return [f for f in all_files if f.startswith(prefix)]

    return MSP_FILES

def read_file_content(path: str) -> str:
    """Read text from a .txt or .pdf file."""
    if path.endswith(".pdf"):
        text_parts: list[str] = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def is_privileged_query(q: str) -> bool:
    return any(k in q.lower() for k in RESTRICTED_KEYWORDS)

# =========================
# EMBEDDING
# =========================
def embed_text(text: str) -> list[float]:
    response = requests.post(
        OLLAMA_EMBED_URL,
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["embedding"]

# =========================
# CHUNKING
# =========================
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks

# =========================
# VECTOR STORE (CHROMA)
# =========================
@st.cache_resource
def get_chroma_client() -> chromadb.PersistentClient:
    os.makedirs(CHROMA_PATH, exist_ok=True)
    return chromadb.PersistentClient(path=CHROMA_PATH)

def collection_name_for(role: str, org: str) -> str:
    """One Chroma collection per org (admin gets its own universal collection)."""
    if role == "admin":
        return "saka_admin"
    return "saka_" + org.lower().replace(" ", "_")

def build_or_load_collection(
    client: chromadb.PersistentClient,
    role: str,
    org: str,
    allowed_files: list[str],
    force_rebuild: bool = False,
) -> tuple[chromadb.Collection, int]:
    name = collection_name_for(role, org)

    if force_rebuild:
        try:
            client.delete_collection(name)
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )

    if collection.count() > 0:
        return collection, collection.count()

    ids: list[str] = []
    embeddings: list[list[float]] = []
    documents: list[str] = []
    metadatas: list[dict[str, Any]] = []

    for filename in allowed_files:
        path = os.path.join(DATA_FOLDER, filename)
        if not os.path.exists(path):
            continue
        content = read_file_content(path)
        for i, chunk in enumerate(chunk_text(content)):
            chunk_id = f"{filename}__chunk{i}"
            ids.append(chunk_id)
            embeddings.append(embed_text(chunk))
            documents.append(chunk)
            metadatas.append({"filename": filename, "chunk_index": i})

    if ids:
        collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

    return collection, len(ids)

def semantic_search(
    collection: chromadb.Collection,
    query: str,
    n_results: int = TOP_K,
) -> list[dict[str, Any]]:
    if collection.count() == 0:
        return []
    k = min(n_results, collection.count())
    query_embedding = embed_text(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    matches: list[dict[str, Any]] = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        relevance = round((1.0 - dist) * 100, 1)
        matches.append({
            "content":   doc,
            "filename":  meta["filename"],
            "relevance": relevance,
        })
    return matches

def relevance_class(score: float) -> str:
    if score >= 70:
        return "relevance-high"
    if score >= 40:
        return "relevance-medium"
    return "relevance-low"

# =========================
# UI — SIDEBAR
# =========================
st.sidebar.header("Access Control")

user_key = st.sidebar.selectbox("Account", list(USERS.keys()))
user = USERS[user_key]
role = user["role"]
org = user.get("org", "Unknown")
permissions = ROLE_PERMISSIONS[role]
allowed_files = get_allowed_files(role, org)

# --- Vector store setup ---
chroma_client = get_chroma_client()
vector_store_ready = False
chunk_count = 0
vector_store_error: str | None = None

try:
    collection, chunk_count = build_or_load_collection(chroma_client, role, org, allowed_files)
    vector_store_ready = True
except Exception as e:
    vector_store_error = str(e)

st.sidebar.markdown("### Current Account")
st.sidebar.write(f"**User:** {user_key}")
st.sidebar.write(f"**Display Name:** {user['display_name']}")
st.sidebar.write(f"**Org:** {org}")
st.sidebar.write(f"**Role:** {role}")

st.sidebar.markdown("### Permissions")
st.sidebar.write(f"• Query documents: {'Yes' if permissions.get('can_query') else 'No'}")
st.sidebar.write(f"• View restricted info: {'Yes' if permissions.get('can_view_restricted') else 'No'}")
st.sidebar.write(f"• View audit logs: {'Yes' if permissions.get('can_view_logs') else 'No'}")

st.sidebar.markdown("### Vector Store")
if vector_store_ready:
    st.sidebar.success(f"Ready — {chunk_count} chunks indexed")
    st.sidebar.caption(f"Collection: `{collection_name_for(role, org)}`")
    st.sidebar.caption(f"Embed model: `{EMBED_MODEL}`")
    if permissions.get("can_view_logs"):
        if st.sidebar.button("🔄 Rebuild Index"):
            try:
                collection, chunk_count = build_or_load_collection(
                    chroma_client, role, org, allowed_files, force_rebuild=True
                )
                st.sidebar.success("Index rebuilt.")
                st.rerun()
            except Exception as rebuild_err:
                st.sidebar.error(f"Rebuild failed: {rebuild_err}")
else:
    st.sidebar.error("Vector store unavailable")
    if vector_store_error:
        st.sidebar.caption(f"Error: {vector_store_error}")
    st.sidebar.caption(f"Make sure Ollama is running and `{EMBED_MODEL}` is pulled.")

st.sidebar.markdown("### Approved Documents")
if allowed_files:
    for f in allowed_files:
        st.sidebar.write(f"- {f}")
else:
    st.sidebar.warning("No documents found for this org.")

st.sidebar.markdown("### Security")
st.sidebar.caption("Local LLM • Role-based access • Semantic RAG • Restricted query blocking • Audit logging")

# =========================
# UI — MAIN
# =========================
left, right = st.columns([4, 1])

with left:
    st.markdown('<div class="main-title">Secure AI Knowledge Assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-text">Grounded responses. No guessing. Approved data only.</div>',
        unsafe_allow_html=True,
    )

with right:
    if vector_store_ready and chunk_count > 0:
        st.markdown('<div class="status-pill">Vector Store Ready</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-pill-warning">Store Not Ready</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Ask a Question")
    question = st.text_area(
        "Ask a Question",
        placeholder="Ask a question about your approved documents...",
        height=120,
        label_visibility="collapsed",
    )
    submitted = st.button("Get Answer", use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("How It Works")
    st.write("• Semantic vector search over approved documents")
    st.write("• Respects your selected account role")
    st.write("• Blocks restricted requests for non-admin roles")
    st.write("• Logs activity for review")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# MAIN LOGIC
# =========================
if submitted:

    if not question.strip():
        st.warning("Enter a question.")

    elif not vector_store_ready:
        st.error(
            f"Vector store is not available. "
            f"Make sure Ollama is running and `ollama pull {EMBED_MODEL}` has been run."
        )

    elif is_privileged_query(question) and not permissions["can_view_restricted"]:
        write_log(user_key, role, question, "BLOCKED", "RBAC")
        st.markdown(f"""
        <div class="danger-box">
        <b>Access denied</b><br>
        This request involves privileged or sensitive information.<br><br>
        Your role (<b>{role}</b>) does not have permission.
        </div>
        """, unsafe_allow_html=True)
        st.info("If you believe you need access, contact an administrator.")

    else:
        try:
            matches = semantic_search(collection, question)
        except requests.exceptions.RequestException as embed_err:
            st.error(f"Embedding failed — is Ollama running? ({embed_err})")
            write_log(user_key, role, question, "ERROR_EMBED", "Ollama")
            matches = []

        if not matches:
            write_log(user_key, role, question, "NOT_FOUND", "None")
            st.markdown(
                '<div class="warning-box"><b>No grounded answer found</b><br>'
                'I could not find relevant information in the approved documents.</div>',
                unsafe_allow_html=True,
            )
        else:
            try:
                response = requests.post(
                    OLLAMA_URL,
                    json={
                        "model": OLLAMA_MODEL,
                        "messages": [
                            {"role": "system", "content": "Only answer from the provided context. Do not use outside knowledge."},
                            {
                                "role": "user",
                                "content": "\n\n".join([m["content"] for m in matches]) + "\n\n" + question,
                            },
                        ],
                        "stream": False,
                    },
                    timeout=300,
                )
                response.raise_for_status()
                answer = response.json()["message"]["content"]

                st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)

                st.subheader("Source Documents Used")
                for m in matches:
                    preview = m["content"][:150].replace("<", "&lt;").replace(">", "&gt;")
                    score = m["relevance"]
                    css_class = relevance_class(score)
                    st.markdown(f"""
                    <div class="source-box">
                        📄 <b>{m["filename"]}</b>
                        &nbsp;&nbsp;<span class="{css_class}">Relevance: {score}%</span><br>
                        <small>{preview}…</small>
                    </div>
                    """, unsafe_allow_html=True)

                write_log(
                    user_key, role, question, "ANSWERED",
                    ",".join([m["filename"] for m in matches]),
                )

                st.markdown(
                    '<div class="success-box"><b>Request completed</b><br>'
                    'Response generated from approved knowledge sources only.</div>',
                    unsafe_allow_html=True,
                )

            except requests.exceptions.JSONDecodeError:
                st.error("Invalid JSON from model. Make sure Ollama is running and streaming is disabled.")
                write_log(user_key, role, question, "ERROR_JSON", "Ollama")

            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")
                write_log(user_key, role, question, "ERROR_REQUEST", "Ollama")

            except KeyError:
                st.error("Unexpected response format from model.")
                write_log(user_key, role, question, "ERROR_FORMAT", "Ollama")

# =========================
# AUDIT LOG VIEWER
# =========================
st.markdown("---")
st.subheader("Audit Log")

if permissions.get("can_view_logs"):
    log_df = parse_logs_to_dataframe()
    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.caption("Recent user activity across the system")
    with col_b:
        if st.button("Clear Logs"):
            clear_logs()
            st.success("Logs cleared.")
            st.rerun()

    if not log_df.empty:
        max_logs = st.selectbox("Show recent entries", [5, 10, 20, 50], index=1)
        st.dataframe(log_df.head(max_logs), use_container_width=True, hide_index=True)
    else:
        st.info("No audit log entries found yet.")
else:
    st.info("Audit logs are only visible to admin accounts.")
