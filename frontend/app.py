import streamlit as st
import requests
import uuid

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="AI Support Desk", layout="wide")

# Persistent session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
session_id = st.session_state.session_id

# Persistent chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


st.title("🤖 AI Support Desk — RAG Chatbot")


# ========================= 1️⃣ UPLOAD SECTION =========================
st.subheader("📁 Upload Knowledge Base Documents")

uploaded_files = st.file_uploader(
    "Upload PDF, DOCX, CSV, or TXT files",
    type=["pdf", "docx", "csv", "txt"],
    accept_multiple_files=True,
)

if st.button("Upload & Ingest"):
    if not uploaded_files:
        st.warning("Please select at least one file.")
    else:
        with st.spinner("Uploading & processing..."):
            form_data = [( "files", (f.name, f.read(), f"type") ) for f in uploaded_files]
            res = requests.post(f"{API_BASE}/docs/upload", files=form_data)

        if res.status_code == 200:
            st.success("Documents uploaded & added to knowledge base.")
        else:
            st.error("Upload failed: " + res.text)


st.markdown("---")
# ========================= 2️⃣ CHAT SECTION =========================
st.subheader("💬 Ask Questions")

# Display history first
for role, text in st.session_state.messages:
    if role == "assistant":
        st.markdown(f"🟣 **Support Bot:** {text}")
    else:
        st.markdown(f"🧑 **You:** {text}")


# Callback runs when Enter is pressed
def send_message():
    user_msg = st.session_state.chat_input_text.strip()
    if not user_msg:
        return

    st.session_state.messages.append(("user", user_msg))

    try:
        res = requests.post(
            f"{API_BASE}/chat",
            json={"session_id": session_id, "message": user_msg},
            timeout=60
        )
        if res.status_code == 200:
            ai_reply = res.json().get("answer", "")
            st.session_state.messages.append(("assistant", ai_reply))
        else:
            st.session_state.messages.append(("assistant", "⚠ Backend error"))
    except Exception as e:
        st.session_state.messages.append(("assistant", f"⚠ Request failed: {e}"))

    # 🔥 this clears textbox on the next rerun
    st.session_state.pop("chat_input_text", None)


# Render chat input after history (Enter triggers callback)
st.text_input(
    "Type message & press Enter:",
    key="chat_input_text",
    value=st.session_state.get("chat_input_text", ""),  # 👈 default blank after pop
    on_change=send_message,
)

st.markdown("<script>document.querySelector('input[type=text]').focus();</script>", unsafe_allow_html=True)

st.markdown("---")
# ========================= 3️⃣ DASHBOARD SECTION (Lazy Loaded) =========================
with st.expander("📊 Dashboard — View Analytics", expanded=False):
    try:
        summary = requests.get(f"{API_BASE}/analytics/summary").json()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Conversations", summary["total_conversations"])
        col2.metric("Escalated to Human", summary["escalated_conversations"])
        col3.metric("Resolution Rate", summary["resolution_rate"])

        trending = requests.get(f"{API_BASE}/analytics/trending-queries").json()

        st.write("### 🔥 Latest 5 Questions")
        qs = trending["latest_user_queries"][:5]
        if qs:
            for q in qs:
                st.write("• " + q)
        else:
            st.info("Start chatting to populate trending questions.")
    except Exception as e:
        st.error("Unable to load dashboard: " + str(e))
