"""
components/tab_flashcards.py
Smart Flashcard Generator — uses native Streamlit expanders.
No HTML/JS flip cards — works reliably in Streamlit sandbox.
"""

import streamlit as st
import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI


def generate_flashcards(text: str, llm, count: int = 10) -> list:
    sample = text[:5000]
    prompt = f"""You are an expert educator. Generate exactly {count} flashcards from this study material.

Return ONLY a valid JSON array (no markdown, no backticks, no explanation before or after):
[
  {{
    "question": "clear specific question",
    "answer": "concise complete answer (2-3 sentences max)",
    "difficulty": "easy",
    "topic": "short topic (2-3 words)"
  }}
]

Mix difficulty levels: easy, medium, hard.
Cover different topics from the material.
Do NOT number questions.

Material:
{sample}"""

    try:
        response = llm.invoke(prompt)
        raw = response.content.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start == -1 or end == 0:
            return []
        cards = json.loads(raw[start:end])
        return cards if isinstance(cards, list) else []
    except Exception:
        return []


def render_flashcards_tab():

    st.markdown(
        '<div style="font-size:0.875rem;color:#6b7280;margin-bottom:1.2rem;line-height:1.65;">'
        'Automatically generates flashcards from your content. '
        'Click <b>Reveal Answer</b> on any card to see the answer.'
        '</div>',
        unsafe_allow_html=True
    )

    # Check content is loaded
    if not st.session_state.get("processed") or not st.session_state.get("full_text"):
        st.markdown("""
        <div style="text-align:center;padding:2rem 1rem;">
            <div style="font-size:2rem;margin-bottom:0.8rem;">🃏</div>
            <div style="font-size:0.95rem;color:#6b7280;">No content loaded yet.</div>
            <div style="font-size:0.82rem;color:#9ca3af;margin-top:0.3rem;">
                Upload a PDF, website, or YouTube video first.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Source label
    source = st.session_state.get("source_type", "pdf")
    icons = {"pdf": "📄", "web": "🌐", "youtube": "▶"}
    names = st.session_state.get("pdf_names", ["Document"])
    label = f"{icons.get(source, '📄')} {names[0][:45] if names else 'Content'}"
    st.markdown(
        f'<div style="font-size:0.78rem;color:#6b7280;margin-bottom:1rem;">'
        f'Source: <b style="color:#111827;">{label}</b></div>',
        unsafe_allow_html=True
    )

    # Controls
    col_count, col_btn = st.columns([2, 1])
    with col_count:
        card_count = st.selectbox(
            "cards", [5, 8, 10, 15, 20], index=2,
            label_visibility="collapsed",
            format_func=lambda x: f"{x} flashcards"
        )
    with col_btn:
        generate_btn = st.button("🃏  Generate")

    # Generate
    if generate_btn:
        with st.spinner("Generating flashcards…"):
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4)
            cards = generate_flashcards(st.session_state.full_text, llm, count=card_count)
        if not cards:
            st.error("Could not generate flashcards. Please try again.")
        else:
            st.session_state.flashcards = cards
            st.rerun()

    # Show cards
    if not st.session_state.get("flashcards"):
        return

    cards = st.session_state.flashcards

    # Stats + filter
    diff_counts = {}
    for c in cards:
        d = c.get("difficulty", "medium")
        diff_counts[d] = diff_counts.get(d, 0) + 1

    col_f, col_r = st.columns([2, 1])
    with col_f:
        options = ["all"] + sorted(diff_counts.keys())
        labels = {
            "all":    f"All ({len(cards)})",
            "easy":   f"🟢 Easy ({diff_counts.get('easy', 0)})",
            "medium": f"🟡 Medium ({diff_counts.get('medium', 0)})",
            "hard":   f"🔴 Hard ({diff_counts.get('hard', 0)})",
        }
        selected = st.selectbox(
            "filter", options,
            format_func=lambda x: labels.get(x, x),
            label_visibility="collapsed",
            key="fc_filter"
        )
    with col_r:
        st.markdown('<div class="light-btn">', unsafe_allow_html=True)
        if st.button("↺ New Cards"):
            st.session_state.flashcards = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    filtered = cards if selected == "all" else [
        c for c in cards if c.get("difficulty") == selected
    ]

    # Stats bar
    easy   = diff_counts.get("easy", 0)
    medium = diff_counts.get("medium", 0)
    hard   = diff_counts.get("hard", 0)
    st.markdown(f"""
    <div style="font-size:0.78rem;color:#6b7280;margin:0.6rem 0 1rem 0;">
        {len(cards)} cards &nbsp;·&nbsp;
        <span style="color:#16a34a;">🟢 {easy} easy</span> &nbsp;·&nbsp;
        <span style="color:#d97706;">🟡 {medium} medium</span> &nbsp;·&nbsp;
        <span style="color:#dc2626;">🔴 {hard} hard</span>
    </div>
    """, unsafe_allow_html=True)

    # Difficulty styling
    diff_styles = {
        "easy":   {"bg": "#f0fdf4", "border": "#86efac", "color": "#16a34a", "label": "🟢 Easy"},
        "medium": {"bg": "#fefce8", "border": "#fde68a", "color": "#d97706", "label": "🟡 Medium"},
        "hard":   {"bg": "#fef2f2", "border": "#fca5a5", "color": "#dc2626", "label": "🔴 Hard"},
    }

    # Render each card
    for i, card in enumerate(filtered):
        diff   = card.get("difficulty", "medium")
        style  = diff_styles.get(diff, diff_styles["medium"])
        topic  = card.get("topic", "")
        q      = card.get("question", "")
        a      = card.get("answer", "")

        # Question card (always visible)
        st.markdown(f"""
        <div style="background:{style['bg']};border:1.5px solid {style['border']};
                    border-radius:14px;padding:1rem 1.2rem;margin-bottom:0.4rem;">
            <div style="display:flex;justify-content:space-between;
                        align-items:center;margin-bottom:0.5rem;">
                <span style="font-size:0.68rem;font-weight:700;
                            color:{style['color']};text-transform:uppercase;
                            letter-spacing:0.09em;">{style['label']}</span>
                <span style="font-size:0.68rem;color:#9ca3af;
                            text-transform:uppercase;letter-spacing:0.07em;
                            font-weight:500;">{topic}</span>
            </div>
            <div style="font-size:0.93rem;font-weight:600;
                        color:#111827;line-height:1.55;">{q}</div>
        </div>
        """, unsafe_allow_html=True)

        # Answer — native Streamlit expander (always works)
        with st.expander("👁  Reveal Answer"):
            st.markdown(f"""
            <div style="background:#111827;border-radius:10px;
                        padding:0.9rem 1.1rem;margin-top:0.2rem;">
                <div style="font-size:0.65rem;font-weight:600;color:#6b7280;
                            text-transform:uppercase;letter-spacing:0.1em;
                            margin-bottom:0.45rem;">Answer</div>
                <div style="font-size:0.9rem;color:#f3f4f6;line-height:1.65;">{a}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div style="height:0.3rem;"></div>', unsafe_allow_html=True)