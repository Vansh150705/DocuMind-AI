"""
components/tab_dna.py — Document DNA tab (white theme)
"""
import streamlit as st

def render_dna_tab():
    dna = st.session_state.dna
    if not dna:
        st.markdown('<div style="color:#9ca3af;font-size:0.9rem;margin-top:1rem;padding:1rem 0;">DNA analysis unavailable. Re-process your document to try again.</div>', unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div class="dna-card">
        <div style="font-family:'DM Serif Display',serif;font-size:1.2rem;color:#111827;
                    margin-bottom:0.55rem;letter-spacing:-0.01em;">📋 {dna.get("title","Document")}</div>
        <div style="font-size:0.9rem;color:#6b7280;line-height:1.7;">{dna.get("one_line_summary","")}</div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="dna-card" style="height:100%;">
            <div style="font-size:0.68rem;color:#9ca3af;text-transform:uppercase;letter-spacing:0.12em;font-weight:600;">Domain</div>
            <div style="font-size:1.05rem;font-weight:600;color:#111827;margin-top:0.3rem;margin-bottom:1.1rem;">{dna.get("domain","—")}</div>
            <div style="font-size:0.68rem;color:#9ca3af;text-transform:uppercase;letter-spacing:0.12em;font-weight:600;">Tone</div>
            <div style="font-size:1.05rem;font-weight:600;color:#111827;margin-top:0.3rem;margin-bottom:1.1rem;">{dna.get("tone","—")}</div>
            <div style="font-size:0.68rem;color:#9ca3af;text-transform:uppercase;letter-spacing:0.12em;font-weight:600;">Language</div>
            <div style="font-size:1.05rem;font-weight:600;color:#111827;margin-top:0.3rem;">🌐 {dna.get("language","English")}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        comp = dna.get("complexity", 50)
        sent = dna.get("sentiment", 50)
        info = dna.get("informativeness", 50)
        sent_color = "#16a34a" if sent > 60 else "#d97706" if sent > 40 else "#dc2626"
        st.markdown(f"""
        <div class="dna-card" style="height:100%;">
            <div class="dna-bar-label" style="margin-top:0;">Complexity — {comp}%</div>
            <div class="dna-bar-outer"><div class="dna-bar-inner" style="width:{comp}%;background:#111827;"></div></div>
            <div class="dna-bar-label">Sentiment — {sent}%</div>
            <div class="dna-bar-outer"><div class="dna-bar-inner" style="width:{sent}%;background:{sent_color};"></div></div>
            <div class="dna-bar-label">Informativeness — {info}%</div>
            <div class="dna-bar-outer"><div class="dna-bar-inner" style="width:{info}%;background:#6366f1;"></div></div>
        </div>""", unsafe_allow_html=True)

    if dna.get("key_themes"):
        tags = "".join([f'<span class="dna-tag">#{t}</span>' for t in dna["key_themes"]])
        st.markdown(f'<div class="dna-card"><div class="section-label" style="margin-bottom:0.7rem;">Key Themes</div>{tags}</div>', unsafe_allow_html=True)

    if dna.get("key_entities"):
        tags = "".join([f'<span class="dna-tag">🏷 {e}</span>' for e in dna["key_entities"]])
        st.markdown(f'<div class="dna-card"><div class="section-label" style="margin-bottom:0.7rem;">Key Entities</div>{tags}</div>', unsafe_allow_html=True)

    if dna.get("unusual_insight"):
        st.markdown(
            f'<div class="dna-card">'
            f'<div class="section-label" style="margin-bottom:0.6rem;">💡 Unusual Insight</div>'
            f'<div style="font-size:0.9rem;color:#374151;line-height:1.75;">{dna["unusual_insight"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
