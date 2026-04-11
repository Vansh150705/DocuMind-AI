"""
components/tab_tools.py — Smart Tools tab (white theme)
"""
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

def render_tools_tab():
    st.markdown('<div class="section-label" style="margin-bottom:1rem;">Select a Tool</div>', unsafe_allow_html=True)

    tool = st.selectbox("Tool", [
        "📝  Auto-Summary",
        "❓  Generate Quiz Questions",
        "📧  Draft Email from Document",
        "🔍  Find Contradictions",
        "📊  Extract Action Items"
    ], label_visibility="collapsed")

    if st.button("▶   Run Tool"):
        llm    = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
        sample = st.session_state.full_text[:4000]
        lang   = st.session_state.doc_language
        lang_note = f" Respond in {lang}." if lang != "English" else ""

        prompts = {
            "📝  Auto-Summary":
                f"Create a structured summary: 1) Overview 2) Key Points 3) Important Details 4) Conclusion.{lang_note}\n\nDocument:\n{sample}",
            "❓  Generate Quiz Questions":
                f"Generate 5 multiple-choice quiz questions with 4 options (A-D), mark correct answer.{lang_note}\n\nDocument:\n{sample}",
            "📧  Draft Email from Document":
                f"Draft a professional email. Include subject line, greeting, body, call to action.{lang_note}\n\nDocument:\n{sample}",
            "🔍  Find Contradictions":
                f"Find contradictions or inconsistencies. Be specific. If none, say so.{lang_note}\n\nDocument:\n{sample}",
            "📊  Extract Action Items":
                f"Extract all action items as a numbered checklist with owner and priority.{lang_note}\n\nDocument:\n{sample}"
        }

        tool_ph = st.empty()
        tool_ph.markdown("""
        <div style="display:flex;align-items:center;gap:0.6rem;padding:1rem 0;color:#6b7280;font-size:0.875rem;">
            <div class="typing-dots"><span></span><span></span><span></span></div>
            <span style="font-style:italic;">Running tool…</span>
        </div>""", unsafe_allow_html=True)

        response = llm.invoke(prompts[tool])
        tool_ph.empty()

        st.markdown(
            f'<div class="dna-card" style="margin-top:0.8rem;animation:scaleIn 0.3s ease both;">'
            f'<div style="font-size:0.92rem;line-height:1.82;color:#111827;white-space:pre-wrap;">'
            f'{response.content}</div></div>',
            unsafe_allow_html=True
        )
