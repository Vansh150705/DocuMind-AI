"""
app.py — DocuMind AI
Entry point. White background, Settings tab removed.
"""

import time


from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

import streamlit as st
import os
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

from utils.styles import STYLES
from utils.pdf_processor import extract_text_from_pdfs
from utils.ai_helpers import generate_document_dna

from components.tab_chat import render_chat_tab
from components.tab_dna import render_dna_tab
from components.tab_tools import render_tools_tab
from components.tab_analytics import render_analytics_tab



st.set_page_config(page_title="DocuMind AI", page_icon="🧠", layout="centered")
st.markdown(STYLES, unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================
DEFAULTS = {
    "chat_history": [], "vectorstore": None, "pdf_names": [],
    "total_pages": 0, "total_chunks": 0, "suggested_q": None,
    "dna": None, "mode": "qa", "full_text": "", "processed": False,
    "persona": "default", "doc_language": "English",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div style="animation: fadeUp 0.5s ease both;">
    <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.15rem;">
        <div style="width:36px;height:36px;background:#111827;border-radius:10px;
                    display:flex;align-items:center;justify-content:center;font-size:1.1rem;
                    box-shadow:0 2px 8px rgba(17,24,39,0.2);">🧠</div>
        <div style="font-family:'DM Serif Display',serif;font-size:1.7rem;color:#111827;
                    letter-spacing:-0.03em;font-weight:400;line-height:1;">DocuMind AI</div>
    </div>
    <div style="font-size:0.875rem;color:#6b7280;font-weight:400;margin-top:0.5rem;
                margin-left:0.1rem;letter-spacing:0.01em;">
        Intelligent document analysis — powered by Gemini
    </div>
    <div class="header-accent"></div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# UPLOAD SECTION
# ============================================================
if not st.session_state.processed:

    # Premium empty state
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon-wrap">📄</div>
        <div class="empty-title">Upload your documents</div>
        <div class="empty-sub">
            Drop in one or more PDFs to begin intelligent analysis,
            Q&amp;A, and document insights — all powered by Gemini.
        </div>
        <div class="empty-feature-row">
            <span class="empty-feature-chip">🧬 Document DNA</span>
            <span class="empty-feature-chip">💬 Smart Q&amp;A</span>
            <span class="empty-feature-chip">🛠 Auto Tools</span>
            <span class="empty-feature-chip">📊 Analytics</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Select Files</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Upload PDFs", type="pdf",
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        file_tags = "".join([
            f"<span style='display:inline-block;background:#f0fdf4;border:1px solid #bbf7d0;"
            f"border-radius:8px;padding:0.2rem 0.6rem;font-size:0.78rem;margin:0.15rem;"
            f"color:#15803d;font-weight:500;'>📄 {f.name}</span>"
            for f in uploaded_files
        ])
        st.markdown(f"""
        <div class="upload-success">
            ✅ {len(uploaded_files)} file{'s' if len(uploaded_files) > 1 else ''} ready to process
        </div>
        <div style="margin:0.3rem 0 1rem 0;">{file_tags}</div>
        """, unsafe_allow_html=True)

        if st.button("⚡  Process & Index Documents"):
            progress_ph = st.empty()
            steps = [
                ("📖", "Reading documents…"),
                ("✂️", "Chunking text…"),
                ("🔢", "Generating embeddings…"),
                ("🗃️", "Building vector index…"),
                ("🧬", "Analysing document DNA…"),
                ("✅", "Finalising…"),
            ]

            def render_steps(active_idx):
                rows = ""
                for i, (icon, label) in enumerate(steps):
                    if i < active_idx:
                        cls, ico = "done", "✓"
                    elif i == active_idx:
                        cls, ico = "active", icon
                    else:
                        cls, ico = "", icon
                    rows += (
                        f'<div class="step-row">'
                        f'<span class="step-icon">{ico}</span>'
                        f'<span class="step-text {cls}">{label}</span>'
                        f'</div>'
                    )
                pct = int((active_idx / len(steps)) * 100)
                return f"""
                <div class="step-loader">
                    <div class="section-label" style="margin-bottom:1rem;">Processing your documents</div>
                    {rows}
                    <div class="progress-track">
                        <div style="height:3px;background:#111827;border-radius:3px;
                                    width:{pct}%;transition:width 0.4s ease;"></div>
                    </div>
                </div>"""

            progress_ph.markdown(render_steps(0), unsafe_allow_html=True)
            chunks, metas, pages, full_text = extract_text_from_pdfs(uploaded_files)

            progress_ph.markdown(render_steps(1), unsafe_allow_html=True)
            time.sleep(0.3)

            progress_ph.markdown(render_steps(2), unsafe_allow_html=True)
            embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

            progress_ph.markdown(render_steps(3), unsafe_allow_html=True)
            vectorstore = FAISS.from_texts(chunks, embeddings, metadatas=metas)

            progress_ph.markdown(render_steps(4), unsafe_allow_html=True)
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
            dna = generate_document_dna(full_text, llm)
            doc_language = dna.get("language", "English") if dna else "English"

            progress_ph.markdown(render_steps(5), unsafe_allow_html=True)
            time.sleep(0.4)
            progress_ph.empty()

            st.session_state.vectorstore  = vectorstore
            st.session_state.pdf_names    = [f.name for f in uploaded_files]
            st.session_state.total_pages  = pages
            st.session_state.total_chunks = len(chunks)
            st.session_state.chat_history = []
            st.session_state.dna          = dna
            st.session_state.full_text    = full_text
            st.session_state.doc_language = doc_language
            st.session_state.processed    = True
            st.rerun()

# ============================================================
# MAIN APP
# ============================================================
else:
    # Doc info bar
    pills       = "".join([f'<span class="doc-pill">📄 {n}</span>' for n in st.session_state.pdf_names])
    lang_pill   = f'<span class="doc-pill">🌐 {st.session_state.doc_language}</span>'
    status_badge = '<span class="status-badge status-ready">● Ready</span>'

    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                flex-wrap:wrap;gap:0.5rem;margin-bottom:1rem;animation:fadeUp 0.4s ease both;">
        <div>{pills}{lang_pill}</div>
        {status_badge}
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{st.session_state.total_pages}</div><div class="metric-label">Pages</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{st.session_state.total_chunks}</div><div class="metric-label">Chunks</div></div>', unsafe_allow_html=True)
    with c3:
        total_q = sum(1 for m in st.session_state.chat_history if m["role"] == "user")
        st.markdown(f'<div class="metric-card"><div class="metric-val">{total_q}</div><div class="metric-label">Asked</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="light-btn">', unsafe_allow_html=True)
        if st.button("🗑 Clear"):
            st.session_state.chat_history = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c5:
        st.markdown('<div class="light-btn">', unsafe_allow_html=True)
        if st.button("↺ Reset"):
            for k, v in DEFAULTS.items():
                st.session_state[k] = v
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="dm-divider"></div>', unsafe_allow_html=True)

    # 4 tabs — Settings tab removed
    tab1, tab2, tab3, tab4 = st.tabs([
        "💬  Chat", "🧬  DNA", "🛠  Tools", "📊  Analytics"
    ])

    with tab1: render_chat_tab()
    with tab2: render_dna_tab()
    with tab3: render_tools_tab()
    with tab4: render_analytics_tab()
