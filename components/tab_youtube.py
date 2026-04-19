import streamlit as st
import re

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

from utils.agents import (
    is_vague_query, get_clarification_question,
    self_reflect_and_improve, apply_confidence_adaptation,
    get_confidence
)


# ── Helpers ───────────────────────────────────────────────────
def extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r"(?:v=|youtu\.be/|embed/|shorts/)([a-zA-Z0-9_-]{11})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def get_transcript(video_id: str) -> tuple[str, list]:
    """
    Fetches transcript for a YouTube video.
    Returns (full_text, segments_with_timestamps).
    Raises ValueError with user-friendly message on failure.
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try English first, then any available language
        try:
            transcript = transcript_list.find_transcript(["en", "en-US", "en-GB"])
        except Exception:
            # Fall back to first available and translate
            try:
                transcript = transcript_list.find_generated_transcript(
                    [t.language_code for t in transcript_list]
                )
            except Exception:
                transcript = list(transcript_list)[0]

        segments = transcript.fetch()
        full_text = " ".join([seg["text"] for seg in segments])
        return full_text, segments

    except TranscriptsDisabled:
        raise ValueError("This video has subtitles/captions disabled by the creator.")
    except NoTranscriptFound:
        raise ValueError("No transcript available for this video. It may not have captions.")
    except Exception as e:
        if "Could not retrieve" in str(e) or "VideoUnavailable" in str(e):
            raise ValueError("Video not found or is private/unavailable.")
        raise ValueError(f"Could not fetch transcript: {str(e)}")


def format_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS format."""
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m}:{s:02d}"


def index_transcript(text: str, video_id: str):
    """Chunks and indexes transcript into FAISS."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)
    chunks = splitter.split_text(text)
    metas = [{"source": f"youtube/{video_id}", "page": i + 1} for i in range(len(chunks))]
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    return FAISS.from_texts(chunks, embeddings, metadatas=metas), len(chunks)


# ── Tab renderer ──────────────────────────────────────────────
def render_youtube_tab():

    st.markdown('<div class="section-label" style="margin-bottom:0.5rem;">YouTube Video Q&A</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.875rem;color:#6b7280;margin-bottom:1.2rem;line-height:1.65;">'
        'Paste any YouTube link — lectures, tutorials, interviews, podcasts — '
        'and ask questions about the video without watching the whole thing.'
        '</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.get("yt_processed"):

        url_input = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed"
        )

        if url_input:
            video_id = extract_video_id(url_input)
            if not video_id:
                st.markdown(
                    '<div style="color:#dc2626;font-size:0.83rem;margin-top:0.4rem;">'
                    '⚠️ Could not detect a valid YouTube video ID. Please paste the full video URL.</div>',
                    unsafe_allow_html=True
                )
            else:
                # Show thumbnail preview
                st.markdown(f"""
                <div style="margin:0.6rem 0 0.9rem 0;">
                    <img src="https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                         style="width:100%;max-width:420px;border-radius:12px;
                                border:1px solid #e5e7eb;display:block;" />
                </div>
                """, unsafe_allow_html=True)

                if st.button("▶  Extract Transcript & Index"):
                    progress_ph = st.empty()
                    try:
                        progress_ph.markdown("""
                        <div style="display:flex;align-items:center;gap:0.6rem;
                                    padding:0.8rem 1rem;background:#f9fafb;
                                    border:1px solid #e5e7eb;border-radius:12px;
                                    font-size:0.875rem;color:#6b7280;">
                            <div class="typing-dots"><span></span><span></span><span></span></div>
                            <span>Fetching transcript…</span>
                        </div>""", unsafe_allow_html=True)

                        full_text, segments = get_transcript(video_id)

                        progress_ph.markdown("""
                        <div style="display:flex;align-items:center;gap:0.6rem;
                                    padding:0.8rem 1rem;background:#f9fafb;
                                    border:1px solid #e5e7eb;border-radius:12px;
                                    font-size:0.875rem;color:#6b7280;">
                            <div class="typing-dots"><span></span><span></span><span></span></div>
                            <span>Indexing transcript…</span>
                        </div>""", unsafe_allow_html=True)

                        vs, chunk_count = index_transcript(full_text, video_id)
                        duration_sec = segments[-1]["start"] + segments[-1]["duration"] if segments else 0
                        progress_ph.empty()

                        st.session_state.yt_vectorstore = vs
                        st.session_state.yt_video_id   = video_id
                        st.session_state.yt_url        = url_input
                        st.session_state.yt_text       = full_text
                        st.session_state.yt_chunks     = chunk_count
                        st.session_state.yt_segments   = segments
                        st.session_state.yt_duration   = format_timestamp(duration_sec)
                        st.session_state.yt_history    = []
                        st.session_state.yt_processed  = True
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
        vid  = st.session_state.yt_video_id
        url  = st.session_state.yt_url

        # ── Video info card ──
        st.markdown(f"""
        <div style="display:flex;gap:0.9rem;align-items:flex-start;
                    background:#f9fafb;border:1px solid #e5e7eb;
                    border-radius:14px;padding:0.9rem 1rem;margin-bottom:1rem;">
            <img src="https://img.youtube.com/vi/{vid}/default.jpg"
                 style="width:80px;border-radius:8px;flex-shrink:0;" />
            <div>
                <div style="font-size:0.68rem;color:#9ca3af;text-transform:uppercase;
                            letter-spacing:0.1em;font-weight:600;margin-bottom:0.25rem;">Indexed Video</div>
                <a href="{url}" target="_blank"
                   style="font-size:0.82rem;color:#2563eb;text-decoration:none;word-break:break-all;">
                   {url[:60]}{"…" if len(url) > 60 else ""}
                </a>
                <div style="font-size:0.75rem;color:#9ca3af;margin-top:0.35rem;">
                    ⏱ {st.session_state.yt_duration} &nbsp;|&nbsp;
                    {st.session_state.yt_chunks} chunks indexed &nbsp;|&nbsp;
                    {len(st.session_state.yt_text.split())} words transcribed
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Suggested questions ──
        if not st.session_state.yt_history:
            st.markdown('<div class="section-label">Try asking</div>', unsafe_allow_html=True)
            suggestions = [
                "What is this video about?",
                "Summarize the key points",
                "What are the main takeaways?",
                "What examples are mentioned?"
            ]
            c1, c2 = st.columns(2)
            for i, s in enumerate(suggestions):
                with (c1 if i % 2 == 0 else c2):
                    st.markdown('<div class="sug-pill-wrap">', unsafe_allow_html=True)
                    if st.button(s, key=f"yt_sug_{i}"):
                        st.session_state.yt_suggested = s
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div style="height:0.8rem;"></div>', unsafe_allow_html=True)

        # ── Chat history ──
        for msg in st.session_state.yt_history:
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
            if st.button("↺ New Video"):
                for k in ["yt_vectorstore","yt_video_id","yt_url","yt_text","yt_chunks",
                          "yt_segments","yt_duration","yt_history","yt_processed","yt_suggested"]:
                    st.session_state.pop(k, None)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Chat input ──
        question = st.chat_input("Ask anything about this video…", key="yt_input")

        if st.session_state.get("yt_suggested"):
            question = st.session_state.yt_suggested
            del st.session_state["yt_suggested"]

        if question:
            if is_vague_query(question):
                clarification = get_clarification_question(question)
                st.session_state.yt_history.append({"role": "user", "content": question})
                st.session_state.yt_history.append({
                    "role": "assistant", "content": f"🤔 {clarification}", "confidence": None
                })
                st.rerun()

            else:
                st.session_state.yt_history.append({"role": "user", "content": question})

                skeleton_ph = st.empty()
                skeleton_ph.markdown("""
                <div style="display:flex;justify-content:flex-start;margin:1rem 0;">
                    <div class="skeleton-wrap">
                        <div class="skeleton-line full"></div>
                        <div class="skeleton-line medium"></div>
                        <div class="skeleton-line short"></div>
                        <div style="margin-top:0.6rem;display:flex;align-items:center;gap:0.5rem;">
                            <div class="typing-dots"><span></span><span></span><span></span></div>
                            <span class="typing-text">Searching transcript…</span>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

                docs       = st.session_state.yt_vectorstore.similarity_search(question, k=5)
                context    = "\n\n".join([d.page_content for d in docs])
                confidence = get_confidence(docs, question)

                prompt = f"""You are DocuMind AI analyzing a YouTube video transcript.
Answer the question based ONLY on the transcript content below.
If the answer is not in the transcript, say so clearly. Never fabricate.

Video URL: {url}

Transcript excerpt:
{context}

Question: {question}
Answer:"""

                llm     = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
                initial = llm.invoke(prompt).content
                answer  = self_reflect_and_improve(question, context, initial, llm)
                answer  = apply_confidence_adaptation(answer, confidence)

                skeleton_ph.empty()

                st.session_state.yt_history.append({
                    "role": "assistant", "content": answer, "confidence": confidence
                })
                st.rerun()
