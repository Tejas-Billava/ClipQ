
import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"   
# BACKEND_URL = "http://127.0.0.1:8000/" 

st.set_page_config(
    page_title="YouTube Smart Summariser & Q&A",
    page_icon="🎬",
    layout="centered",
)


def summarise_video(url: str) -> str:
    """POST /summarise  ->  string with bullet-point summary."""
    r = requests.post(f"{BACKEND_URL}/api/summarise", json={"url": url}, timeout=180)
    r.raise_for_status()
    return r.json()["summary"]


def ask_question(url: str, question: str, top_k: int = 2):
    """POST /ask  ->  answer + context passages (list)"""
    payload = {"url": url, "question": question, "top_k": top_k}
    r = requests.post(f"{BACKEND_URL}/api/ask", json=payload, timeout=180)
    r.raise_for_status()
    data = r.json()
    return data["answer"], data["context"]



st.markdown(
    """
    <style>
    /* bump default font sizes a bit */
    .big-title {font-size:2.6rem;font-weight:750;text-align:center;margin-bottom:0.4rem;}
    .subtitle  {font-size:1.15rem;text-align:center;margin-top:0; color:#6e6e6e;}

    /* widen the text-input */
    .element-container:has(#youtube_url) input {
        font-size:1.05rem;
    }
    /* Give chat bubbles rounded corners */
    .stChatMessage { border-radius: 8px; }
    </style>
""",
    unsafe_allow_html=True,
)


st.markdown('<p class="big-title">🎬 YouTube Smart&nbsp;Summariser &amp; Chat</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Paste any YouTube link, get bullet-point insights, then question about video!</p>',
    unsafe_allow_html=True,
)
st.divider()


if "summary" not in st.session_state:
    st.session_state.summary = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of dicts: {"role": "...", "content": "..."}


youtube_url = st.text_input(
    "YouTube link",
    placeholder="https://www.youtube.com/watch?v=...",
    key="youtube_url",
)

col1, col2 = st.columns(2)
with col1:
    summon = st.button("🚀 Summarise", use_container_width=True, disabled=not youtube_url)
with col2:
    clear_chat = st.button("🗑️ Clear chat", use_container_width=True) if st.session_state.chat_history else None


if summon:
    with st.spinner("Fetching transcript & Summarising, Please wait.... "):
        try:
            summary = summarise_video(youtube_url.strip())
            st.session_state.summary = summary
            st.session_state.chat_history = []  # reset chat so it matches new video
        except Exception as exc:
            st.error(f"Backend error: {exc}")


if st.session_state.summary:
    st.subheader("📋 Summary")
    # show exactly what Gemini returned – no extra parsing
    st.markdown(st.session_state.summary)

    st.divider()
    st.subheader("💬 Ask about video anything!")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


    user_prompt = st.chat_input("Type your question…")
    if user_prompt:
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    answer, ctx_passages = ask_question(youtube_url, user_prompt)
                except Exception as exc:
                    st.error(f"Backend error: {exc}")
                    answer = None

            if answer:
                st.markdown(answer)

                with st.expander("🔍 Source transcript chunks", expanded=False):
                    for i, chunk in enumerate(ctx_passages, 1):
                        st.markdown(f"**Chunk {i}:**\n{chunk}")

        st.session_state.chat_history.extend(
            [
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": answer or "Error"},
            ]
        )


if clear_chat:
    st.session_state.chat_history = []
