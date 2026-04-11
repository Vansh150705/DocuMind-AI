"""
components/tab_analytics.py — Analytics tab (white theme)
"""
import streamlit as st
import datetime, base64
from utils.ai_helpers import get_analytics, generate_chat_export

def render_analytics_tab():
    if not st.session_state.chat_history:
        st.markdown("""
        <div style="text-align:center;padding:3.5rem 1rem;animation:fadeUp 0.4s ease both;">
            <div style="font-size:2.4rem;margin-bottom:0.9rem;">📊</div>
            <div style="font-family:'DM Serif Display',serif;font-size:1.2rem;color:#111827;margin-bottom:0.4rem;">No data yet</div>
            <div style="font-size:0.875rem;color:#9ca3af;">Ask questions in the Chat tab to see analytics</div>
        </div>""", unsafe_allow_html=True)
        return

    a = get_analytics(st.session_state.chat_history)

    st.markdown('<div class="section-label" style="margin-bottom:1rem;">Session Overview</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{a["total_q"]}</div><div class="metric-label">Questions</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{a["avg_conf"]}%</div><div class="metric-label">Avg Confidence</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{a["high_conf"]}</div><div class="metric-label">High Conf.</div></div>', unsafe_allow_html=True)

    if a["confs"]:
        st.markdown('<div class="dm-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label" style="margin-bottom:1rem;">Confidence Per Answer</div>', unsafe_allow_html=True)
        for i, conf in enumerate(a["confs"]):
            color = "#16a34a" if conf > 60 else "#d97706" if conf > 30 else "#dc2626"
            label = "High" if conf > 60 else "Medium" if conf > 30 else "Low"
            st.markdown(f"""
            <div style="margin-bottom:0.7rem;">
                <div style="font-size:0.78rem;color:#6b7280;margin-bottom:0.25rem;font-weight:500;">
                    Answer {i+1}
                    <span style="color:{color};"> — {label}</span>
                    <span style="color:#9ca3af;font-weight:400;"> ({conf}%)</span>
                </div>
                <div class="analytics-bar-outer">
                    <div class="analytics-bar-inner" style="width:{conf}%;background:{color};"></div>
                </div>
            </div>""", unsafe_allow_html=True)

    if a["top_words"]:
        st.markdown('<div class="dm-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label" style="margin-bottom:1rem;">Most Asked About</div>', unsafe_allow_html=True)
        max_count = a["top_words"][0][1] if a["top_words"] else 1
        for word, count in a["top_words"]:
            pct = int((count / max_count) * 100)
            st.markdown(f"""
            <div style="margin-bottom:0.7rem;">
                <div style="font-size:0.82rem;color:#374151;margin-bottom:0.25rem;font-weight:500;">
                    {word} <span style="color:#9ca3af;font-weight:400;">({count}×)</span>
                </div>
                <div class="analytics-bar-outer">
                    <div class="analytics-bar-inner" style="width:{pct}%;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

    if a["low_conf"] > 0:
        st.markdown(
            f'<div class="warn-banner">⚠️ {a["low_conf"]} answer(s) had low confidence — '
            f'the document may not cover those topics well.</div>',
            unsafe_allow_html=True
        )

    st.markdown('<div style="height:1.3rem;"></div>', unsafe_allow_html=True)
    export_text = generate_chat_export(st.session_state.chat_history, st.session_state.pdf_names, st.session_state.dna)
    b64      = base64.b64encode(export_text.encode()).decode()
    filename = f"documind_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    st.markdown(
        f'<a href="data:text/plain;base64,{b64}" download="{filename}" '
        f'style="display:inline-flex;align-items:center;gap:0.4rem;background:#111827;color:#ffffff;'
        f'border-radius:10px;padding:0.55rem 1.3rem;font-size:0.84rem;font-family:Inter,sans-serif;'
        f'text-decoration:none;font-weight:500;box-shadow:0 2px 8px rgba(17,24,39,0.2);">'
        f'📥 Export Full Report</a>',
        unsafe_allow_html=True
    )
