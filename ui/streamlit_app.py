"""Streamlit UI for the HDFC MF FAQ Assistant (PRD §12, architecture.md §2).

Welcome line + 3 example questions + chat, with a persistent facts-only
disclaimer. Renders pipeline.ask() responses: factual answers show one clickable
Source link + freshness stamp; refusals/out-of-scope are styled distinctly.
Nothing the user types is persisted to disk.

Run from the repo root:  streamlit run ui/streamlit_app.py
"""
import os
import sys

# Make the repo root importable regardless of the working directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

import config
from app.generate.prompts import DISCLAIMER, EXAMPLES, WELCOME
from app.pipeline import ask

_ICON = {
    "answer": "✅",
    "not_found": "ℹ️",
    "out_of_scope": "🧭",
    "refusal_advice": "🚫",
    "refusal_performance": "📈",
    "refusal_pii": "🔒",
}

_COVERED = [
    config.SCHEME_LARGE_CAP,
    config.SCHEME_FLEXI_CAP,
    config.SCHEME_ELSS,
    config.SCHEME_SMALL_CAP,
    config.SCHEME_BAF,
]

st.set_page_config(page_title="HDFC MF FAQ Assistant", page_icon="💬", layout="centered")


@st.cache_resource(show_spinner="Preparing the knowledge base…")
def _ensure_index() -> bool:
    """Build the ChromaDB index once if it's missing (e.g. on a fresh deploy where
    data/chroma is not shipped). Runs a single time per process via cache_resource."""
    from app.ingest.index import get_collection
    if get_collection().count() == 0:
        from app.ingest.build_index import main as build_index_main
        build_index_main()
    return True


_ensure_index()


def render_response(r) -> None:
    """Render one AskResponse inside a chat bubble."""
    if r.type == "answer":
        body = r.text.rsplit("\n\nSource:", 1)[0].strip()
        st.markdown(body)
        if r.source_url:
            st.markdown(f"🔗 **Source:** [{r.source_url}]({r.source_url})")
            st.caption(f"Last updated from sources: {r.last_updated}")
    else:
        st.markdown(f"{_ICON.get(r.type, '💬')} {r.text}")


# --- Sidebar: scope + controls ---
with st.sidebar:
    st.header("What I cover")
    st.markdown("**Factual** questions about 5 HDFC schemes:")
    for s in _COVERED:
        st.markdown(f"- {s.split(' - ')[0]}")
    st.caption("Facts-only · No advice · No returns/performance · No PII")
    if st.button("🧹 Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Header ---
st.title("💬 HDFC Mutual Fund — FAQ Assistant")
st.markdown(WELCOME)

# --- Example questions ---
st.caption("Try an example:")
cols = st.columns(len(EXAMPLES))
example_click = None
for i, ex in enumerate(EXAMPLES):
    if cols[i].button(ex, key=f"ex_{i}", use_container_width=True):
        example_click = ex

# --- Chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m["role"] == "assistant":
            render_response(m["resp"])
        else:
            st.markdown(m["content"])

# --- New input (example button or typed) ---
typed = st.chat_input("Ask a factual question about an HDFC scheme…")
user_q = example_click or typed

if user_q:
    st.session_state.messages.append({"role": "user", "content": user_q})
    with st.chat_message("user"):
        st.markdown(user_q)
    with st.chat_message("assistant"):
        with st.spinner("Looking it up…"):
            r = ask(user_q)
        render_response(r)
    st.session_state.messages.append({"role": "assistant", "resp": r})

# --- Persistent disclaimer ---
st.divider()
st.caption(f"⚠️ {DISCLAIMER}")
