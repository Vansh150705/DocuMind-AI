"""
app.py — DocuMind AI
Entry point. Landing page has PDF + URL + YouTube inputs.
"""

import streamlit as st
import time
import re

import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from youtube_transcript_api import YouTubeTranscriptApi

from dotenv import load_dotenv
from utils.styles import STYLES
from utils.pdf_processor import extract_text_from_pdfs
from utils.ai_helpers import generate_document_dna

from components.tab_chat import render_chat_tab
from components.tab_dna import render_dna_tab
from components.tab_tools import render_tools_tab
from components.tab_analytics import render_analytics_tab
from components.tab_compare import render_compare_tab
from components.tab_timeline import render_timeline_tab
from components.tab_flashcards import render_flashcards_tab

load_dotenv()

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
    "source_type": "pdf",
    "compare_vectorstore": None, "compare_name": "",
    "compare_full_text": "", "compare_processed": False,
    "compare_history": [], "compare_suggested": None,
    "timeline_data": None, "timeline_generated": False,
    "web_url": "", "web_title": "",
    "yt_video_id": "", "yt_url": "", "yt_duration": "",
    "flashcards": None, "fc_source_label": "",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================
# HELPERS
# ============================================================

def index_text(text, source_label):
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)
    chunks = splitter.split_text(text)
    metas = [{"source": source_label, "page": i + 1} for i in range(len(chunks))]
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    return FAISS.from_texts(chunks, embeddings, metadatas=metas), len(chunks)


def scrape_url(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        raise ValueError("The website took too long to respond.")
    except requests.exceptions.ConnectionError:
        raise ValueError("Could not connect to that URL.")
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"Website returned error: {e.response.status_code}")
    except Exception as e:
        raise ValueError(f"Could not fetch URL: {str(e)}")

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe", "noscript"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title else url
    texts = []
    for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "li", "article", "section", "blockquote"]):
        t = tag.get_text(" ", strip=True)
        if len(t) > 40:
            texts.append(t)

    full_text = "\n\n".join(texts)
    if len(full_text.strip()) < 200:
        raise ValueError("Couldn't extract enough text from this page.")
    return title, full_text


def extract_video_id(url):
    m = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([a-zA-Z0-9_-]{11})", url)
    return m.group(1) if m else None


def get_transcript(video_id):
    try:
        api = YouTubeTranscriptApi()
        try:
            fetched = api.fetch(video_id, languages=["en", "en-US", "en-GB"])
            segments = [{"text": s.text, "start": s.start, "duration": s.duration} for s in fetched]
        except Exception:
            try:
                transcript_list = api.list(video_id)
                available = list(transcript_list)
                if not available:
                    raise ValueError("No transcripts found for this video.")
                fetched = api.fetch(video_id, languages=[available[0].language_code])
                segments = [{"text": s.text, "start": s.start, "duration": s.duration} for s in fetched]
            except ValueError:
                raise
            except Exception as e2:
                raise ValueError(f"No transcript available: {str(e2)}")

        if not segments:
            raise ValueError("Transcript is empty.")

        full_text = " ".join([s["text"] for s in segments])
        return full_text, segments

    except ValueError:
        raise
    except Exception as e:
        err = str(e)
        if "disabled" in err.lower() or "TranscriptsDisabled" in err:
            raise ValueError("This video has captions disabled by the creator.")
        elif "unavailable" in err.lower() or "private" in err.lower():
            raise ValueError("Video is unavailable or private.")
        else:
            raise ValueError(f"Could not fetch transcript: {err}")


def format_timestamp(seconds):
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m}:{s:02d}"


def show_progress(ph, msg):
    ph.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.6rem;
                padding:0.8rem 1rem;background:#f9fafb;
                border:1px solid #e5e7eb;border-radius:12px;
                font-size:0.875rem;color:#6b7280;">
        <div class="typing-dots"><span></span><span></span><span></span></div>
        <span>{msg}</span>
    </div>""", unsafe_allow_html=True)


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
# LANDING PAGE
# ============================================================
if not st.session_state.processed:

    st.markdown("""
    <div class="empty-state" style="padding:2rem 0 1.5rem 0;">
        <div class="empty-icon-wrap">🧠</div>
        <div class="empty-title">Choose your source</div>
        <div class="empty-sub">Upload a PDF, paste a website URL, or drop a YouTube link to get started.</div>
    </div>
    """, unsafe_allow_html=True)

    src_tab1, src_tab2, src_tab3 = st.tabs(["📄  PDF Upload", "🌐  Website URL", "▶  YouTube Video"])

    # ── PDF TAB ──
    with src_tab1:
        st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
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
            <div class="upload-success">✅ {len(uploaded_files)} file{'s' if len(uploaded_files)>1 else ''} ready</div>
            <div style="margin:0.3rem 0 0.8rem 0;">{file_tags}</div>
            """, unsafe_allow_html=True)

            if st.button("⚡  Process & Index PDF", key="btn_pdf"):
                progress_ph = st.empty()
                steps = [
                    ("📖","Reading…"), ("✂️","Chunking…"), ("🔢","Embedding…"),
                    ("🗃️","Indexing…"), ("🧬","DNA Analysis…"), ("✅","Done!")
                ]

                def render_steps(idx):
                    rows = ""
                    for i, (icon, label) in enumerate(steps):
                        if i < idx: cls, ico = "done", "✓"
                        elif i == idx: cls, ico = "active", icon
                        else: cls, ico = "", icon
                        rows += f'<div class="step-row"><span class="step-icon">{ico}</span><span class="step-text {cls}">{label}</span></div>'
                    pct = int((idx / len(steps)) * 100)
                    return (f'<div class="step-loader">'
                            f'<div class="section-label" style="margin-bottom:1rem;">Processing your documents</div>'
                            f'{rows}'
                            f'<div class="progress-track"><div style="height:3px;background:#111827;'
                            f'border-radius:3px;width:{pct}%;transition:width 0.4s ease;"></div></div>'
                            f'</div>')

                progress_ph.markdown(render_steps(0), unsafe_allow_html=True)
                chunks, metas, pages, full_text = extract_text_from_pdfs(uploaded_files)
                progress_ph.markdown(render_steps(1), unsafe_allow_html=True)
                time.sleep(0.2)
                progress_ph.markdown(render_steps(2), unsafe_allow_html=True)
                embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
                progress_ph.markdown(render_steps(3), unsafe_allow_html=True)
                vectorstore = FAISS.from_texts(chunks, embeddings, metadatas=metas)
                progress_ph.markdown(render_steps(4), unsafe_allow_html=True)
                llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
                dna = generate_document_dna(full_text, llm)
                doc_language = dna.get("language", "English") if dna else "English"
                progress_ph.markdown(render_steps(5), unsafe_allow_html=True)
                time.sleep(0.3)
                progress_ph.empty()

                st.session_state.vectorstore    = vectorstore
                st.session_state.pdf_names      = [f.name for f in uploaded_files]
                st.session_state.total_pages    = pages
                st.session_state.total_chunks   = len(chunks)
                st.session_state.chat_history   = []
                st.session_state.dna            = dna
                st.session_state.full_text      = full_text
                st.session_state.doc_language   = doc_language
                st.session_state.source_type    = "pdf"
                st.session_state.fc_source_label = ", ".join([f.name for f in uploaded_files])
                st.session_state.processed      = True
                st.rerun()

    # ── WEBSITE TAB ──
    with src_tab2:
        st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.85rem;color:#6b7280;margin-bottom:0.6rem;">'
            'Paste any website URL to chat with its content</div>',
            unsafe_allow_html=True
        )
        web_url = st.text_input(
            "Website URL",
            placeholder="https://example.com/article",
            label_visibility="collapsed",
            key="web_url_input"
        )

        if web_url:
            if not web_url.startswith(("http://", "https://")):
                st.markdown(
                    '<div style="color:#dc2626;font-size:0.82rem;margin-top:0.3rem;">'
                    '⚠️ URL must start with http:// or https://</div>',
                    unsafe_allow_html=True
                )
            else:
                if st.button("🌐  Scrape & Index Page", key="btn_web"):
                    ph = st.empty()
                    try:
                        show_progress(ph, "Fetching page…")
                        title, text = scrape_url(web_url)
                        show_progress(ph, "Indexing content…")
                        vs, chunks_count = index_text(text, title)
                        ph.empty()

                        st.session_state.vectorstore    = vs
                        st.session_state.full_text      = text
                        st.session_state.pdf_names      = [title]
                        st.session_state.total_pages    = 1
                        st.session_state.total_chunks   = chunks_count
                        st.session_state.chat_history   = []
                        st.session_state.dna            = None
                        st.session_state.doc_language   = "English"
                        st.session_state.source_type    = "web"
                        st.session_state.web_url        = web_url
                        st.session_state.web_title      = title
                        st.session_state.fc_source_label = title
                        st.session_state.processed      = True
                        st.rerun()
                    except ValueError as e:
                        ph.empty()
                        st.markdown(
                            f'<div style="background:#fef2f2;border:1px solid #fca5a5;'
                            f'border-radius:12px;padding:0.8rem 1rem;font-size:0.84rem;color:#dc2626;">'
                            f'❌ {str(e)}</div>',
                            unsafe_allow_html=True
                        )

    # ── YOUTUBE TAB ──
    with src_tab3:
        st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.85rem;color:#6b7280;margin-bottom:0.6rem;">'
            'Paste any YouTube video link to chat with its transcript</div>',
            unsafe_allow_html=True
        )
        yt_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
            key="yt_url_input"
        )

        if yt_url:
            vid_id = extract_video_id(yt_url)
            if not vid_id:
                st.markdown(
                    '<div style="color:#dc2626;font-size:0.82rem;margin-top:0.3rem;">'
                    '⚠️ Could not detect a valid YouTube video ID.</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<img src="https://img.youtube.com/vi/{vid_id}/hqdefault.jpg" '
                    f'style="width:100%;max-width:380px;border-radius:12px;'
                    f'border:1px solid #e5e7eb;margin:0.6rem 0;display:block;"/>',
                    unsafe_allow_html=True
                )
                if st.button("▶  Extract Transcript & Index", key="btn_yt"):
                    ph = st.empty()
                    try:
                        show_progress(ph, "Fetching transcript…")
                        full_text, segments = get_transcript(vid_id)
                        show_progress(ph, "Indexing transcript…")
                        vs, chunks_count = index_text(full_text, f"youtube/{vid_id}")
                        duration = format_timestamp(
                            segments[-1].get("start", 0) + segments[-1].get("duration", 0)
                        ) if segments else "0:00"
                        ph.empty()

                        st.session_state.vectorstore    = vs
                        st.session_state.full_text      = full_text
                        st.session_state.pdf_names      = [f"YouTube: {yt_url[:50]}"]
                        st.session_state.total_pages    = 1
                        st.session_state.total_chunks   = chunks_count
                        st.session_state.chat_history   = []
                        st.session_state.dna            = None
                        st.session_state.doc_language   = "English"
                        st.session_state.source_type    = "youtube"
                        st.session_state.yt_video_id    = vid_id
                        st.session_state.yt_url         = yt_url
                        st.session_state.yt_duration    = duration
                        st.session_state.fc_source_label = f"YouTube Video ({vid_id})"
                        st.session_state.processed      = True
                        st.rerun()
                    except ValueError as e:
                        ph.empty()
                        st.markdown(
                            f'<div style="background:#fef2f2;border:1px solid #fca5a5;'
                            f'border-radius:12px;padding:0.8rem 1rem;font-size:0.84rem;color:#dc2626;">'
                            f'❌ {str(e)}</div>',
                            unsafe_allow_html=True
                        )


# ============================================================
# MAIN APP
# ============================================================
else:
    source = st.session_state.source_type

    if source == "pdf":
        pills = "".join([f'<span class="doc-pill">📄 {n}</span>' for n in st.session_state.pdf_names])
    elif source == "web":
        short = st.session_state.web_url[:45] + "…" if len(st.session_state.web_url) > 45 else st.session_state.web_url
        pills = (f'<span class="doc-pill">🌐 {st.session_state.web_title[:35]}</span>'
                 f'<span class="doc-pill" style="font-size:0.72rem;color:#9ca3af;">{short}</span>')
    else:
        pills = (f'<span class="doc-pill">▶ YouTube</span>'
                 f'<span class="doc-pill">⏱ {st.session_state.yt_duration}</span>')

    lang_pill = f'<span class="doc-pill">🌐 {st.session_state.doc_language}</span>' if source == "pdf" else ""
    status_badge = '<span class="status-badge status-ready">● Ready</span>'

    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                flex-wrap:wrap;gap:0.5rem;margin-bottom:1rem;animation:fadeUp 0.4s ease both;">
        <div>{pills}{lang_pill}</div>
        {status_badge}
    </div>""", unsafe_allow_html=True)

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

    if source == "pdf":
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "💬  Chat", "🧬  DNA", "🛠  Tools", "📊  Analytics",
            "🔀  Compare", "🕐  Timeline", "🃏  Flashcards"
        ])
        with tab1: render_chat_tab()
        with tab2: render_dna_tab()
        with tab3: render_tools_tab()
        with tab4: render_analytics_tab()
        with tab5: render_compare_tab()
        with tab6: render_timeline_tab()
        with tab7: render_flashcards_tab()
    else:
        tab1, tab2, tab3 = st.tabs(["💬  Chat", "🕐  Timeline", "🃏  Flashcards"])
        with tab1: render_chat_tab()
        with tab2: render_timeline_tab()
        with tab3: render_flashcards_tab()