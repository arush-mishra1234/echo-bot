import os
import requests
import streamlit as st
from dotenv import load_dotenv

# ── Load env vars (optional – app works fine with no .env) ─────────────────────
# If .env doesn't exist dotenv simply does nothing; secrets come from the sidebar.
load_dotenv(override=False)  # override=False: env vars already set take priority

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Echo Bot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0d0d1a 0%, #111827 50%, #0d1117 100%);
    min-height: 100vh;
}

/* ── Header ── */
.chat-header {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
}

.chat-header .logo {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    background: linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.4rem;
    font-weight: 700;
    letter-spacing: -0.5px;
}

.chat-header .tagline {
    color: #6b7280;
    font-size: 0.95rem;
    margin-top: 0.3rem;
    font-weight: 400;
}

/* ── Chat container ── */
.chat-container {
    max-width: 780px;
    margin: 0 auto;
    padding: 0 1rem;
}

/* ── Message bubbles ── */
.msg-wrapper {
    display: flex;
    margin: 1rem 0;
    animation: fadeSlideIn 0.3s ease;
}

@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

.msg-wrapper.user  { justify-content: flex-end; }
.msg-wrapper.bot   { justify-content: flex-start; }

.msg-bubble {
    max-width: 75%;
    padding: 0.85rem 1.15rem;
    border-radius: 18px;
    line-height: 1.65;
    font-size: 0.95rem;
    word-break: break-word;
    position: relative;
}

.msg-bubble.user {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: #fff;
    border-bottom-right-radius: 4px;
    box-shadow: 0 4px 20px rgba(99,102,241,0.35);
}

.msg-bubble.bot {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    color: #e2e8f0;
    border-bottom-left-radius: 4px;
    backdrop-filter: blur(12px);
}

.msg-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
    opacity: 0.55;
    color: #94a3b8;
}

.msg-wrapper.user .msg-label { text-align: right; }

/* ── Avatar dots ── */
.avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}

.avatar.user { background: linear-gradient(135deg,#6366f1,#8b5cf6); margin-left: 0.6rem; }
.avatar.bot  { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12); margin-right: 0.6rem; }

/* ── Divider ── */
.chat-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin: 1.5rem 0;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 4rem 1rem;
    color: #374151;
}

.empty-state .icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-state p { font-size: 1rem; color: #4b5563; }

/* ── Input area ── */
.stChatInput > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1.5px solid rgba(99,102,241,0.35) !important;
    border-radius: 14px !important;
    transition: border-color 0.2s;
}
.stChatInput > div:focus-within {
    border-color: rgba(99,102,241,0.75) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}
.stChatInput textarea {
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(13,13,26,0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
}

.sidebar-section {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1rem 1.1rem;
    margin-bottom: 1rem;
}

.sidebar-section h4 {
    color: #94a3b8;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.6rem;
}

/* ── Model badge ── */
.model-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.35);
    color: #a5b4fc;
    font-size: 0.78rem;
    font-weight: 500;
    padding: 0.3rem 0.75rem;
    border-radius: 999px;
}

/* ── Status badge ── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    color: #34d399;
    font-size: 0.8rem;
    font-weight: 500;
}
.status-dot {
    width: 7px; height: 7px;
    background: #34d399;
    border-radius: 50%;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

/* ── Scrollable chat history ── */
.chat-scroll {
    max-height: 62vh;
    overflow-y: auto;
    padding: 0.5rem 0;
    scrollbar-width: thin;
    scrollbar-color: rgba(99,102,241,0.3) transparent;
}
.chat-scroll::-webkit-scrollbar       { width: 5px; }
.chat-scroll::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.35); border-radius: 10px; }

/* ── Typing spinner ── */
.typing-dots span {
    display: inline-block;
    width: 7px; height: 7px;
    margin: 0 2px;
    background: #8b5cf6;
    border-radius: 50%;
    animation: bounce 1.2s infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
    0%, 80%, 100% { transform: translateY(0); }
    40%           { transform: translateY(-8px); }
}

/* ── Streamlit widget overrides ── */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #e2e8f0 !important;
}
.stSlider > div > div > div { background: #6366f1 !important; }
button[data-testid="baseButton-secondary"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Groq API call ──────────────────────────────────────────────────────────────
MODELS = {
    "⚡ Llama 3.1 8B Instant": "llama-3.1-8b-instant",
    "🧠 Llama 3.3 70B Versatile": "llama-3.3-70b-versatile",
    "🚀 Mixtral 8x7B": "mixtral-8x7b-32768",
    "🔬 Gemma 2 9B": "gemma2-9b-it",
}

def groq_chat(api_key: str, messages: list, model: str, temperature: float) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {"messages": messages, "model": model, "stream": False, "temperature": temperature}
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

# ── Session state init ─────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []          # [{role, content}]
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "You are a helpful, concise, and friendly AI assistant."

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 Echo Bot")
    st.markdown('<div class="status-badge"><div class="status-dot"></div> Online</div>', unsafe_allow_html=True)
    st.markdown("---")

    # API Key
    st.markdown('<div class="sidebar-section"><h4>🔑 Authentication</h4>', unsafe_allow_html=True)

    # ── Key resolution (priority order) ────────────────────────────────────────
    # 1. Whatever the user types in the sidebar (highest priority)
    # 2. st.secrets["GROQ_API_KEY"]  (Streamlit Cloud / secrets.toml)
    # 3. GROQ_API_KEY environment variable / .env file
    # The text field is always blank so the key is never displayed in the UI.
    secrets_key = ""
    try:
        secrets_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass  # secrets not configured – fine, continue

    env_key = os.environ.get("GROQ_API_KEY", "")

    api_key_input = st.text_input(
        "Groq API Key",
        value="",                      # always blank – stored keys stay hidden
        type="password",
        placeholder="gsk_…  (paste to override default key)",
        label_visibility="collapsed",
        help="Get a free key at console.groq.com/keys",
    )

    # Resolve in priority order
    api_key = api_key_input.strip() or secrets_key or env_key

    if api_key_input.strip():
        st.markdown('<p style="color:#34d399;font-size:0.78rem;margin-top:0.4rem">✓ Custom key entered — ready to chat</p>', unsafe_allow_html=True)
    elif secrets_key:
        st.markdown('<p style="color:#34d399;font-size:0.78rem;margin-top:0.4rem">✓ Key loaded from Streamlit Secrets</p>', unsafe_allow_html=True)
    elif env_key:
        st.markdown('<p style="color:#34d399;font-size:0.78rem;margin-top:0.4rem">✓ Key loaded from environment</p>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<p style="color:#f87171;font-size:0.78rem;margin-top:0.4rem">'
            '⚠ No API key — paste yours above or get one free at '
            '<a href="https://console.groq.com/keys" target="_blank" '
            'style="color:#a5b4fc">console.groq.com</a></p>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # Model selection
    st.markdown('<div class="sidebar-section"><h4>🤖 Model</h4>', unsafe_allow_html=True)
    model_label = st.selectbox("Model", list(MODELS.keys()), label_visibility="collapsed")
    selected_model = MODELS[model_label]
    st.markdown(f'<div class="model-badge">⚙ {selected_model}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Temperature
    st.markdown('<div class="sidebar-section"><h4>🌡 Temperature</h4>', unsafe_allow_html=True)
    temperature = st.slider("Temp", 0.0, 1.5, 0.7, 0.05, label_visibility="collapsed")
    st.markdown(f'<p style="color:#6b7280;font-size:0.75rem">{"🎯 Precise" if temperature < 0.4 else "⚖ Balanced" if temperature < 0.9 else "🎨 Creative"} ({temperature})</p>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # System prompt
    st.markdown('<div class="sidebar-section"><h4>💬 System Prompt</h4>', unsafe_allow_html=True)
    st.session_state.system_prompt = st.text_area(
        "System prompt",
        value=st.session_state.system_prompt,
        height=90,
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Clear history
    if st.button("🗑 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown('<p style="color:#374151;font-size:0.72rem;text-align:center">Echo Bot · Powered by Groq</p>', unsafe_allow_html=True)

# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="chat-header">
  <div class="logo">🤖 Echo Bot</div>
  <div class="tagline">Your personal AI assistant — fast, smart, and powered by Groq</div>
</div>
""", unsafe_allow_html=True)

# ── Render message history ─────────────────────────────────────────────────────
chat_html = '<div class="chat-scroll">'

if not st.session_state.messages:
    chat_html += """
    <div class="empty-state">
      <div class="icon">💬</div>
      <p>Start a conversation — ask me anything!</p>
    </div>
    """
else:
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            chat_html += f"""
            <div class="msg-wrapper user">
              <div>
                <div class="msg-label">You</div>
                <div class="msg-bubble user">{content}</div>
              </div>
              <div class="avatar user">🧑</div>
            </div>"""
        else:
            # Preserve line breaks for assistant
            content_html = content.replace("\n", "<br>")
            chat_html += f"""
            <div class="msg-wrapper bot">
              <div class="avatar bot">⚡</div>
              <div>
                <div class="msg-label">Echo Bot</div>
                <div class="msg-bubble bot">{content_html}</div>
              </div>
            </div>"""

chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask me anything…")

if user_input:
    if not api_key:
        st.error("⚠️ Please enter your Groq API key in the sidebar to start chatting.")
        st.stop()

    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Build full payload (system + history)
    payload_messages = [{"role": "system", "content": st.session_state.system_prompt}]
    payload_messages += st.session_state.messages

    # Call Groq
    with st.spinner(""):
        try:
            reply = groq_chat(api_key, payload_messages, selected_model, temperature)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except requests.exceptions.HTTPError as e:
            detail = ""
            try:
                detail = e.response.json().get("error", {}).get("message", "")
            except Exception:
                pass
            st.error(f"❌ API Error: {detail or str(e)}")
            st.session_state.messages.pop()  # remove unanswered user message
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            st.session_state.messages.pop()

    st.rerun()
