"""
components/tab_chat.py
Chat tab — premium UI with skeleton loader, smooth animations,
typing indicator, voice mic, mode/persona selectors.
"""

import streamlit as st
import datetime
import base64

from langchain_google_genai import ChatGoogleGenerativeAI

from utils.agents import (
    is_vague_query, get_clarification_question,
    self_reflect_and_improve, apply_confidence_adaptation,
    get_confidence
)
from utils.ai_helpers import build_prompt, generate_chat_export


def render_chat_tab():

    # ---- Mode + Persona row ----
    col_mode, col_persona = st.columns(2)
    with col_mode:
        st.markdown('<div class="section-label">Response Mode</div>', unsafe_allow_html=True)
        mode = st.selectbox(
            "Mode",
            ["qa", "eli5", "executive", "debate"],
            format_func=lambda x: {
                "qa":        "🎯  Standard Q&A",
                "eli5":      "🧒  Explain Simply",
                "executive": "💼  Executive Brief",
                "debate":    "⚖️  Devil's Advocate"
            }[x],
            label_visibility="collapsed",
            key="mode_sel"
        )
        st.session_state.mode = mode

    with col_persona:
        st.markdown('<div class="section-label">AI Persona</div>', unsafe_allow_html=True)
        persona = st.selectbox(
            "Persona",
            ["default", "lawyer", "doctor", "financial", "teacher", "journalist"],
            format_func=lambda x: {
                "default":    "🤖  Default",
                "lawyer":     "⚖️  Lawyer",
                "doctor":     "🩺  Doctor",
                "financial":  "📈  Financial Analyst",
                "teacher":    "📚  Teacher",
                "journalist": "📰  Journalist"
            }[x],
            label_visibility="collapsed",
            key="persona_sel"
        )
        st.session_state.persona = persona

    st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)

    # ---- Language notice ----
    if st.session_state.doc_language != "English":
        st.markdown(
            f'<div class="info-banner">'
            f'🌐 Document detected in <b>{st.session_state.doc_language}</b>'
            f' — answers will be in the same language</div>',
            unsafe_allow_html=True
        )

    # ---- Suggested questions ----
    if not st.session_state.chat_history:
        st.markdown('<div class="section-label" style="margin-top:0.8rem;">Try asking</div>', unsafe_allow_html=True)
        suggestions = [
            "What is the main topic of this document?",
            "Summarize the key points",
            "What conclusions are drawn?",
            "List the most important findings"
        ]
        c1, c2 = st.columns(2)
        for i, s in enumerate(suggestions):
            with (c1 if i % 2 == 0 else c2):
                st.markdown('<div class="sug-pill-wrap">', unsafe_allow_html=True)
                if st.button(s, key=f"sug_{i}"):
                    st.session_state.suggested_q = s
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div style="height:0.9rem;"></div>', unsafe_allow_html=True)

    # ---- Chat history ----
    for msg in st.session_state.chat_history:
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
            # Source chips
            if msg.get("sources"):
                src_html = "".join([
                    f'<span class="source-chip">📄 {s}</span>'
                    for s in msg["sources"]
                ])
                st.markdown(
                    f'<div style="margin-top:0.3rem;padding-left:0.1rem;">{src_html}</div>',
                    unsafe_allow_html=True
                )
            # Confidence bar
            if msg.get("confidence") is not None:
                conf  = msg["confidence"]
                color = "#16a34a" if conf > 60 else "#d97706" if conf > 30 else "#dc2626"
                label = "High" if conf > 60 else "Medium" if conf > 30 else "Low"
                st.markdown(f"""
                <div style="margin-top:0.45rem;padding-left:0.1rem;">
                    <span style="font-size:0.7rem;color:#9ca3af;letter-spacing:0.01em;">
                        Confidence: {conf}%
                        <span style="color:{color};font-weight:500;"> ({label})</span>
                    </span>
                    <div class="conf-bar-outer">
                        <div class="conf-bar-inner" style="width:{conf}%;background:{color};"></div>
                    </div>
                </div>""", unsafe_allow_html=True)

    # ---- Export button ----
    if st.session_state.chat_history:
        st.markdown('<div style="height:0.9rem;"></div>', unsafe_allow_html=True)
        export_text = generate_chat_export(
            st.session_state.chat_history,
            st.session_state.pdf_names,
            st.session_state.dna
        )
        b64      = base64.b64encode(export_text.encode()).decode()
        filename = f"documind_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        st.markdown(
            f'<a href="data:text/plain;base64,{b64}" download="{filename}" '
            f'style="display:inline-flex;align-items:center;gap:0.4rem;'
            f'background:#f9fafb;color:#374151;border:1px solid #e5e7eb;'
            f'border-radius:10px;padding:0.48rem 1.1rem;font-size:0.82rem;'
            f'font-family:Inter,sans-serif;text-decoration:none;font-weight:500;'
            f'transition:all 0.18s;box-shadow:0 1px 3px rgba(0,0,0,0.06);">'
            f'📥 Export Chat</a>',
            unsafe_allow_html=True
        )
        st.markdown('<div style="height:0.4rem;"></div>', unsafe_allow_html=True)

    # ---- Chat input pipeline ----
    question = st.chat_input("Ask anything about your documents…")
    if st.session_state.suggested_q:
        question = st.session_state.suggested_q
        st.session_state.suggested_q = None

    if question:

        # AGENT 1: Clarification check
        if is_vague_query(question):
            clarification = get_clarification_question(question)
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"🤔 {clarification}",
                "sources": [], "confidence": None,
                "timestamp": datetime.datetime.now().strftime("%H:%M")
            })
            st.rerun()

        else:
            st.session_state.chat_history.append({"role": "user", "content": question})

            # Skeleton loader while generating
            skeleton_ph = st.empty()
            skeleton_ph.markdown("""
            <div style="display:flex;justify-content:flex-start;margin:1rem 0;">
                <div class="skeleton-wrap">
                    <div class="skeleton-line full">✨ Thinking through your question...</div>
                    <div class="skeleton-line medium"></div>
                    <div class="skeleton-line short"></div>
                    <div style="margin-top:0.6rem;display:flex;align-items:center;gap:0.5rem;">
                        <div class="typing-dots">
                            <span></span><span></span><span></span>
                        </div>
                        <span class="typing-text">DocuMind is thinking…</span>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            # Retrieval
            docs       = st.session_state.vectorstore.similarity_search(question, k=5)
            context    = "\n\n".join([d.page_content for d in docs])
            sources    = list(set([f"{d.metadata['source']} p.{d.metadata['page']}" for d in docs]))
            confidence = get_confidence(docs, question)

            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

            # AGENT 2: Generate + Self-reflect
            prompt         = build_prompt(
                question, context, st.session_state.chat_history,
                st.session_state.mode, st.session_state.persona,
                st.session_state.doc_language
            )
            initial_answer = llm.invoke(prompt).content
            answer         = self_reflect_and_improve(question, context, initial_answer, llm)

            # AGENT 3: Confidence adaptation
            answer = apply_confidence_adaptation(answer, confidence)

            skeleton_ph.empty()

            st.session_state.chat_history.append({
                "role": "assistant", "content": answer,
                "sources": sources, "confidence": confidence,
                "timestamp": datetime.datetime.now().strftime("%H:%M")
            })
            st.rerun()
