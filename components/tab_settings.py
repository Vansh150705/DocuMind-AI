"""
components/tab_settings.py
Renders the Settings tab — persona selection and language override.
"""

import streamlit as st


PERSONAS = {
    "default":   ("🤖 Default AI",         "Balanced, helpful, and accurate"),
    "lawyer":    ("⚖️ Lawyer",              "Legal perspective, risk analysis, precise language"),
    "doctor":    ("🩺 Doctor",              "Clinical perspective, medical terminology"),
    "financial": ("📈 Financial Analyst",   "Financial impact, ROI, business risk"),
    "teacher":   ("📚 Teacher",             "Patient explanations with examples"),
    "journalist":("📰 Journalist",          "Key story, surprising facts, what's unsaid")
}


def render_settings_tab():
    st.markdown('<div class="section-label" style="margin-bottom:0.9rem;">AI Persona</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.86rem;color:#888;margin-bottom:1.1rem;line-height:1.65;">'
        'Choose how DocuMind interprets and responds to your document.</div>',
        unsafe_allow_html=True
    )

    for pid, (pname, pdesc) in PERSONAS.items():
        selected = st.session_state.persona == pid
        check    = "✓ " if selected else ""
        if st.button(f"{check}{pname} — {pdesc}", key=f"persona_btn_{pid}"):
            st.session_state.persona = pid
            st.rerun()

    st.markdown('<div style="height:1px;background:#e8e4dc;margin:1.6rem 0;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label" style="margin-bottom:0.6rem;">Document Language</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:0.9rem;color:#555;line-height:1.65;">'
        f'Detected: <b>{st.session_state.doc_language}</b> — responses will match automatically.</div>',
        unsafe_allow_html=True
    )

    if st.session_state.doc_language != "English":
        st.markdown('<div style="height:0.6rem;"></div>', unsafe_allow_html=True)
        if st.button("🔄 Force English Responses"):
            st.session_state.doc_language = "English"
            st.rerun()
