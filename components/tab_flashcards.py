import streamlit as st
import json
import re

from langchain_google_genai import ChatGoogleGenerativeAI


def generate_flashcards(text: str, llm, count: int = 10) -> list:
    """
    Asks Gemini to generate flashcards from the document text.
    Returns a list of {question, answer, difficulty} dicts.
    """
    sample = text[:5000]

    prompt = f"""You are an expert educator. Generate exactly {count} high-quality flashcards from this study material.

Return ONLY a valid JSON array (no markdown, no backticks):
[
  {{
    "question": "clear, specific question",
    "answer": "concise but complete answer (2-4 sentences max)",
    "difficulty": "easy / medium / hard",
    "topic": "short topic label (2-4 words)"
  }}
]

Rules:
- Questions should test genuine understanding, not just memorization
- Mix different difficulty levels
- Cover different topics/sections of the material
- Answers must be self-contained and accurate based on the text
- Do NOT number the questions

Study material:
{sample}"""

    try:
        response = llm.invoke(prompt)
        raw = re.sub(r"```json|```", "", response.content.strip()).strip()
        cards = json.loads(raw)
        if isinstance(cards, list):
            return cards
        return []
    except Exception:
        return []


def render_flashcards_tab():

    st.markdown('<div class="section-label" style="margin-bottom:0.5rem;">Smart Flashcard Generator</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.875rem;color:#6b7280;margin-bottom:1.2rem;line-height:1.65;">'
        'Automatically generates interactive flashcards from your uploaded document. '
        'Click any card to flip it and reveal the answer.'
        '</div>',
        unsafe_allow_html=True
    )

    # ── Flip card CSS + JS (injected once) ──
    st.markdown("""
    <style>
    .fc-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    .fc-wrap {
        perspective: 1000px;
        height: 200px;
        cursor: pointer;
    }
    .fc-inner {
        position: relative;
        width: 100%;
        height: 100%;
        transform-style: preserve-3d;
        transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        border-radius: 16px;
    }
    .fc-wrap.flipped .fc-inner { transform: rotateY(180deg); }

    .fc-front, .fc-back {
        position: absolute;
        width: 100%;
        height: 100%;
        backface-visibility: hidden;
        -webkit-backface-visibility: hidden;
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-sizing: border-box;
    }
    .fc-front {
        background: #ffffff;
        border: 1.5px solid #e5e7eb;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    }
    .fc-back {
        background: #111827;
        border: 1.5px solid #111827;
        transform: rotateY(180deg);
        box-shadow: 0 2px 10px rgba(17,24,39,0.2);
    }

    .fc-difficulty {
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 0.2rem 0.5rem;
        border-radius: 20px;
        display: inline-block;
        width: fit-content;
    }
    .fc-difficulty.easy   { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
    .fc-difficulty.medium { background: #fefce8; color: #d97706; border: 1px solid #fde68a; }
    .fc-difficulty.hard   { background: #fef2f2; color: #dc2626; border: 1px solid #fca5a5; }

    .fc-topic {
        font-size: 0.68rem;
        color: #9ca3af;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .fc-question {
        font-size: 0.9rem;
        font-weight: 600;
        color: #111827;
        line-height: 1.5;
        flex: 1;
        display: flex;
        align-items: center;
        padding: 0.4rem 0;
    }
    .fc-hint {
        font-size: 0.68rem;
        color: #d1d5db;
        text-align: right;
    }
    .fc-answer {
        font-size: 0.875rem;
        color: #f3f4f6;
        line-height: 1.65;
        flex: 1;
        display: flex;
        align-items: center;
        padding: 0.4rem 0;
    }
    .fc-back-hint {
        font-size: 0.68rem;
        color: #6b7280;
        text-align: right;
    }

    /* Progress bar */
    .fc-progress-wrap {
        background: #f3f4f6;
        border-radius: 6px;
        height: 6px;
        overflow: hidden;
        margin-bottom: 1rem;
    }
    .fc-progress-fill {
        height: 6px;
        background: #111827;
        border-radius: 6px;
        transition: width 0.4s ease;
    }
    </style>

    <script>
    function flipCard(el) {
        el.classList.toggle('flipped');
        // Track flipped count
        const total = document.querySelectorAll('.fc-wrap').length;
        const flipped = document.querySelectorAll('.fc-wrap.flipped').length;
        const pct = Math.round((flipped / total) * 100);
        const bar = document.getElementById('fc-progress');
        const label = document.getElementById('fc-label');
        if (bar) bar.style.width = pct + '%';
        if (label) label.textContent = flipped + ' of ' + total + ' revealed';
    }
    </script>
    """, unsafe_allow_html=True)

    # ── Check if primary doc is available ──
    has_primary = st.session_state.get("processed") and st.session_state.get("full_text")

    if not has_primary:
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem;">
            <div style="font-size:2rem;margin-bottom:0.8rem;">🃏</div>
            <div style="font-size:1rem;color:#6b7280;font-weight:500;">No document loaded</div>
            <div style="font-size:0.85rem;color:#9ca3af;margin-top:0.4rem;">
                Upload and process a PDF first (from the main upload screen) to generate flashcards.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Controls ──
    col_count, col_btn = st.columns([2, 1])

    with col_count:
        card_count = st.selectbox(
            "Number of cards",
            [5, 8, 10, 15, 20],
            index=2,
            label_visibility="collapsed",
            format_func=lambda x: f"{x} flashcards"
        )

    with col_btn:
        generate_btn = st.button("🃏  Generate Cards")

    # ── Filter bar (if cards exist) ──
    if st.session_state.get("flashcards"):

        cards = st.session_state.flashcards
        difficulties = ["all"] + sorted(list(set(c.get("difficulty","medium") for c in cards)))
        diff_labels  = {"all": "All", "easy": "🟢 Easy", "medium": "🟡 Medium", "hard": "🔴 Hard"}

        col_f, col_reset = st.columns([2, 1])
        with col_f:
            selected_diff = st.selectbox(
                "Filter",
                difficulties,
                format_func=lambda x: diff_labels.get(x, x.title()),
                label_visibility="collapsed",
                key="fc_filter"
            )
        with col_reset:
            st.markdown('<div class="light-btn">', unsafe_allow_html=True)
            if st.button("↺ Regenerate"):
                st.session_state.flashcards = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        filtered = cards if selected_diff == "all" else [c for c in cards if c.get("difficulty") == selected_diff]

        # ── Stats ──
        easy   = sum(1 for c in cards if c.get("difficulty") == "easy")
        medium = sum(1 for c in cards if c.get("difficulty") == "medium")
        hard   = sum(1 for c in cards if c.get("difficulty") == "hard")

        st.markdown(f"""
        <div style="display:flex;gap:0.5rem;margin:0.8rem 0 0.5rem 0;flex-wrap:wrap;">
            <span style="font-size:0.78rem;color:#6b7280;">
                {len(cards)} cards total &nbsp;·&nbsp;
                <span style="color:#16a34a;">🟢 {easy} easy</span> &nbsp;·&nbsp;
                <span style="color:#d97706;">🟡 {medium} medium</span> &nbsp;·&nbsp;
                <span style="color:#dc2626;">🔴 {hard} hard</span>
            </span>
        </div>
        <div style="font-size:0.75rem;color:#9ca3af;margin-bottom:0.3rem;" id="fc-label">0 of {len(filtered)} revealed</div>
        <div class="fc-progress-wrap">
            <div class="fc-progress-fill" id="fc-progress" style="width:0%;"></div>
        </div>
        """, unsafe_allow_html=True)

        # ── Render cards ──
        cards_html = '<div class="fc-grid">'
        for i, card in enumerate(filtered):
            diff = card.get("difficulty", "medium")
            topic = card.get("topic", "")
            q = card.get("question", "").replace("'", "&#39;").replace('"', '&quot;')
            a = card.get("answer", "").replace("'", "&#39;").replace('"', '&quot;')

            cards_html += f"""
            <div class="fc-wrap" onclick="flipCard(this)" title="Click to flip">
                <div class="fc-inner">
                    <div class="fc-front">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span class="fc-difficulty {diff}">{diff}</span>
                            <span class="fc-topic">{topic}</span>
                        </div>
                        <div class="fc-question">{q}</div>
                        <div class="fc-hint">tap to reveal answer ↗</div>
                    </div>
                    <div class="fc-back">
                        <div style="font-size:0.65rem;font-weight:600;color:#6b7280;
                                    text-transform:uppercase;letter-spacing:0.1em;">Answer</div>
                        <div class="fc-answer">{a}</div>
                        <div class="fc-back-hint">tap to flip back</div>
                    </div>
                </div>
            </div>
            """

        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)

    # ── Generate on click ──
    if generate_btn:
        with st.spinner("Generating flashcards from your document…"):
            llm   = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4)
            cards = generate_flashcards(st.session_state.full_text, llm, count=card_count)

        if not cards:
            st.markdown(
                '<div style="color:#dc2626;font-size:0.84rem;margin-top:0.5rem;">'
                '❌ Could not generate flashcards. Try again.</div>',
                unsafe_allow_html=True
            )
        else:
            st.session_state.flashcards = cards
            st.rerun()
