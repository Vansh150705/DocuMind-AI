import streamlit as st
import re
import datetime
import base64

import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

from utils.agents import (
    is_vague_query, get_clarification_question,
    self_reflect_and_improve, apply_confidence_adaptation,
    get_confidence
)


# ── Scraper ──────────────────────────────────────────────────
def scrape_url(url: str) -> tuple[str, str]:
    """
    Scrapes a URL and returns (page_title, clean_text).
    Raises ValueError with a user-friendly message on failure.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        raise ValueError("The website took too long to respond. Try a different URL.")
    except requests.exceptions.ConnectionError:
        raise ValueError("Could not connect to that URL. Check the link and try again.")
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"Website returned an error: {e.response.status_code}")
    except Exception as e:
        raise ValueError(f"Could not fetch URL: {str(e)}")

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove noise
    for tag in soup(["script", "style", "nav", "footer", "header",
                     "aside", "form", "iframe", "noscript", "meta"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title else url

    # Extract meaningful text
    texts = []
    for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "li", "article",
                               "section", "blockquote", "td", "th"]):
        t = tag.get_text(" ", strip=True)
        if len(t) > 40:
            texts.append(t)

    full_text = "\n\n".join(texts)

    if len(full_text.strip()) < 200:
        raise ValueError("Couldn't extract enough text from this page. The site may block scrapers or use JavaScript rendering.")

    return title, full_text


def index_text(text: str, source_label: str):
    """Chunks and indexes text into a FAISS vectorstore."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)
    chunks = splitter.split_text(text)
    metas = [{"source": source_label, "page": i + 1} for i in range(len(chunks))]
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    return FAISS.from_texts(chunks, embeddings, metadatas=metas), len(chunks)


# ── Tab renderer ─────────────────────────────────────────────
def render_web_tab():

    st.markdown('<div class="section-label" style="margin-bottom:0.5rem;">Chat with any Website</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.875rem;color:#6b7280;margin-bottom:1.2rem;line-height:1.65;">'
        'Paste any URL — news articles, blog posts, documentation, product pages — '
        'and chat with the content using the same AI pipeline.'
        '</div>',
        unsafe_allow_html=True
    )

    # ── URL input ──
    if not st.session_state.get("web_processed"):

        url_input = st.text_input(
            "URL",
            placeholder="https://example.com/article",
            label_visibility="collapsed"
        )

        if url_input:
            # Basic URL validation
            if not url_input.startswith(("http://", "https://")):
                st.markdown(
                    '<div style="color:#dc2626;font-size:0.83rem;margin-top:0.4rem;">'
                    '⚠️ URL must start with http:// or https://</div>',
                    unsafe_allow_html=True
                )
            else:
                if st.button("🌐  Scrape & Index Page"):
                    progress_ph = st.empty()
                    try:
                        progress_ph.markdown("""
                        <div style="display:flex;align-items:center;gap:0.6rem;
                                    padding:0.8rem 1rem;background:#f9fafb;
                                    border:1px solid #e5e7eb;border-radius:12px;
                                    font-size:0.875rem;color:#6b7280;">
                            <div class="typing-dots"><span></span><span></span><span></span></div>
                            <span>Fetching page…</span>
                        </div>""", unsafe_allow_html=True)

                        title, text = scrape_url(url_input)

                        progress_ph.markdown("""
                        <div style="display:flex;align-items:center;gap:0.6rem;
                                    padding:0.8rem 1rem;background:#f9fafb;
                                    border:1px solid #e5e7eb;border-radius:12px;
                                    font-size:0.875rem;color:#6b7280;">
                            <div class="typing-dots"><span></span><span></span><span></span></div>
                            <span>Indexing content…</span>
                        </div>""", unsafe_allow_html=True)

                        vs, chunk_count = index_text(text, title)
                        progress_ph.empty()

                        st.session_state.web_vectorstore = vs
                        st.session_state.web_title       = title
                        st.session_state.web_url         = url_input
                        st.session_state.web_text        = text
                        st.session_state.web_chunks      = chunk_count
                        st.session_state.web_history     = []
                        st.session_state.web_processed   = True
                        st.rerun()

                    except ValueError as e:
                        progress_ph.empty()
                        st.markdown(
                            f'<div style="background:#fef2f2;border:1px solid #fca5a5;'
                            f'border-radius:12px;padding:0.8rem 1rem;font-size:0.84rem;color:#dc2626;">'
                            f'❌ {str(e)}</div>',
                            unsafe_allow_html=True
                        )

    else:
        # ── Page info bar ──
        title = st.session_state.web_title
        url   = st.session_state.web_url
        short_url = url[:55] + "…" if len(url) > 55 else url

        st.markdown(f"""
        <div class="dna-card" style="margin-bottom:1rem;padding:0.9rem 1.1rem;">
            <div style="font-size:0.68rem;color:#9ca3af;text-transform:uppercase;
                        letter-spacing:0.1em;font-weight:600;margin-bottom:0.3rem;">Indexed Page</div>
            <div style="font-size:0.95rem;font-weight:600;color:#111827;margin-bottom:0.25rem;">
                🌐 {title}
            </div>
            <a href="{url}" target="_blank"
               style="font-size:0.78rem;color:#2563eb;text-decoration:none;">{short_url}</a>
            <div style="font-size:0.75rem;color:#9ca3af;margin-top:0.4rem;">
                {st.session_state.web_chunks} chunks indexed
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Suggested questions ──
        if not st.session_state.web_history:
            st.markdown('<div class="section-label">Try asking</div>', unsafe_allow_html=True)
            suggestions = [
                "What is this page about?",
                "Summarize the key points",
                "What are the main conclusions?",
                "List the most important facts"
            ]
            c1, c2 = st.columns(2)
            for i, s in enumerate(suggestions):
                with (c1 if i % 2 == 0 else c2):
                    st.markdown('<div class="sug-pill-wrap">', unsafe_allow_html=True)
                    if st.button(s, key=f"web_sug_{i}"):
                        st.session_state.web_suggested = s
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div style="height:0.8rem;"></div>', unsafe_allow_html=True)

        # ── Chat history ──
        for msg in st.session_state.web_history:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="msg-user"><div class="msg-user-inner">{msg["content"]}</div></div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="msg-bot"><div class="msg-bot-inner">{msg["content"]}</div></div>',
                    unsafe_allow_html=True
                )
                if msg.get("confidence") is not None:
                    conf  = msg["confidence"]
                    color = "#16a34a" if conf > 60 else "#d97706" if conf > 30 else "#dc2626"
                    label = "High" if conf > 60 else "Medium" if conf > 30 else "Low"
                    st.markdown(f"""
                    <div style="margin-top:0.4rem;">
                        <span style="font-size:0.7rem;color:#9ca3af;">
                            Confidence: {conf}%
                            <span style="color:{color};font-weight:500;"> ({label})</span>
                        </span>
                        <div class="conf-bar-outer">
                            <div class="conf-bar-inner" style="width:{conf}%;background:{color};"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)

        # ── Reset button ──
        col_r, _ = st.columns([1, 3])
        with col_r:
            st.markdown('<div class="light-btn">', unsafe_allow_html=True)
            if st.button("↺ New URL"):
                for k in ["web_vectorstore","web_title","web_url","web_text",
                          "web_chunks","web_history","web_processed","web_suggested"]:
                    st.session_state.pop(k, None)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Chat input ──
        question = st.chat_input("Ask anything about this page…", key="web_input")

        if st.session_state.get("web_suggested"):
            question = st.session_state.web_suggested
            del st.session_state["web_suggested"]

        if question:
            # Clarification agent
            if is_vague_query(question):
                clarification = get_clarification_question(question)
                st.session_state.web_history.append({"role": "user", "content": question})
                st.session_state.web_history.append({
                    "role": "assistant", "content": f"🤔 {clarification}",
                    "confidence": None
                })
                st.rerun()

            else:
                st.session_state.web_history.append({"role": "user", "content": question})

                skeleton_ph = st.empty()
                skeleton_ph.markdown("""
                <div style="display:flex;justify-content:flex-start;margin:1rem 0;">
                    <div class="skeleton-wrap">
                        <div class="skeleton-line full"></div>
                        <div class="skeleton-line medium"></div>
                        <div class="skeleton-line short"></div>
                        <div style="margin-top:0.6rem;display:flex;align-items:center;gap:0.5rem;">
                            <div class="typing-dots"><span></span><span></span><span></span></div>
                            <span class="typing-text">Reading the page…</span>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

                docs       = st.session_state.web_vectorstore.similarity_search(question, k=5)
                context    = "\n\n".join([d.page_content for d in docs])
                confidence = get_confidence(docs, question)

                prompt = f"""You are DocuMind AI. Answer the question based ONLY on the web page content below.
If the answer is not on the page, say so clearly. Never fabricate.

Page: {st.session_state.web_title}
URL: {st.session_state.web_url}

Page content:
{context}

Question: {question}
Answer:"""

                llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
                initial = llm.invoke(prompt).content
                answer  = self_reflect_and_improve(question, context, initial, llm)
                answer  = apply_confidence_adaptation(answer, confidence)

                skeleton_ph.empty()

                st.session_state.web_history.append({
                    "role": "assistant", "content": answer, "confidence": confidence
                })
                st.rerun()