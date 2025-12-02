import streamlit as st
import requests
import uuid

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="AI Support Desk", layout="wide")

# Persistent session_id
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

session_id = st.session_state.session_id


# ---------------------- TAB NAVIGATION ----------------------
tab1, tab2, tab3 = st.tabs(["📁 Upload Docs", "💬 Chat", "📊 Dashboard"])


# ---------------------- UPLOAD PAGE ----------------------
with tab1:
    st.header("Upload Knowledge Base Documents")

    files = st.file_uploader(
        "Upload PDF / DOCX / CSV / TXT files",
        type=["pdf", "docx", "csv", "txt"],
        accept_multiple_files=True,
    )

    if st.button("Upload & Ingest") and files:
        with st.spinner("Uploading and processing..."):
            form_data = []
            for f in files:
                form_data.append(("files", (f.name, f.read(), f"type")))

            res = requests.post(f"{API_BASE}/docs/upload", files=form_data)

        if res.status_code == 200:
            st.success("Documents uploaded & added to knowledge base.")
        else:
            st.error("Upload failed: " + res.text)


# ---------------------- CHAT PAGE ----------------------
with tab2:
    st.header("AI Support Chat")

    # Persist chat history on UI
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        role, text = msg
        if role == "assistant":
            st.markdown(f"🟣 **Support Agent:** {text}")
        else:
            st.markdown(f"🧑 **You:** {text}")

    user_input = st.chat_input("Ask anything about support, warranty, refund, etc...")

    if user_input:
        st.session_state.messages.append(("user", user_input))

        res = requests.post(
            f"{API_BASE}/chat",
            json={"session_id": session_id, "message": user_input},
        )

        if res.status_code == 200:
            data = res.json()
            ai_reply = data["answer"]
            st.session_state.messages.append(("assistant", ai_reply))
        else:
            st.session_state.messages.append(("assistant", "⚠ Error contacting backend"))

        st.rerun()  # 🔥 ensures chat refreshes immediately


# ---------------------- DASHBOARD PAGE ----------------------
with tab3:
    st.header("Support Analytics")

    col1, col2, col3 = st.columns(3)

    try:
        summary = requests.get(f"{API_BASE}/analytics/summary").json()

        col1.metric("Total Conversations", summary["total_conversations"])
        col2.metric("Escalated to Human", summary["escalated_conversations"])
        col3.metric("Resolution Rate", summary["resolution_rate"])

        trending = requests.get(f"{API_BASE}/analytics/trending-queries").json()

        st.subheader("Recent User Questions")
        for q in trending["latest_user_queries"]:
            st.write("• " + q)

    except Exception as e:
        st.error("Could not load analytics: " + str(e))
