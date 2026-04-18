"""
components/tab_timeline.py
Document Timeline Extractor — automatically extracts all dates,
events, and deadlines from the document and displays them as a
visual vertical timeline.
"""

import streamlit as st
import json
import re
import base64

from langchain_google_genai import ChatGoogleGenerativeAI


def extract_timeline(full_text: str, llm) -> list:
    sample = full_text[:6000]
    prompt = f"""You are a document analyst. Extract ALL dates, events, deadlines, and time-referenced information from this document.

Return ONLY a valid JSON array (no markdown, no backticks) in this exact format:
[
  {{
    "date": "exact date or period as written in document (e.g. March 2024, Q3 2025, 15 January 2026)",
    "sort_key": "YYYY-MM-DD format for sorting, use best estimate (e.g. 2024-03-01). If only year known use YYYY-01-01",
    "event": "clear description of what happened or is due",
    "type": "one of: deadline / milestone / event / period / announcement / other",
    "importance": "high / medium / low"
  }}
]

Rules:
- Extract EVERY date mentioned, even vague ones like 'Q1 2025' or 'early 2024'
- If no dates exist in the document, return an empty array: []
- Keep event descriptions concise (under 20 words)
- Sort by sort_key ascending

Document:
{sample}"""

    try:
        response = llm.invoke(prompt)
        raw = re.sub(r"```json|```", "", response.content.strip()).strip()
        data = json.loads(raw)
        if isinstance(data, list):
            return sorted(data, key=lambda x: x.get("sort_key", "9999"))
        return []
    except Exception:
        return []


def render_timeline_tab():

    st.markdown('<div class="section-label" style="margin-bottom:0.6rem;">Document Timeline</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.875rem;color:#6b7280;margin-bottom:1.3rem;line-height:1.65;">'
        'Automatically extracts all dates, events, deadlines, and milestones from your document '
        'and displays them as a chronological timeline.'
        '</div>',
        unsafe_allow_html=True
    )

    if "timeline_data" not in st.session_state:
        st.session_state.timeline_data = None
        st.session_state.timeline_generated = False

    if not st.session_state.timeline_generated:
        if st.button("🕐  Extract Timeline"):
            with st.spinner("Analysing document for dates and events…"):
                llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
                timeline = extract_timeline(st.session_state.full_text, llm)
                st.session_state.timeline_data = timeline
                st.session_state.timeline_generated = True
            st.rerun()

    if st.session_state.timeline_generated:
        timeline = st.session_state.timeline_data

        col_r, _ = st.columns([1, 3])
        with col_r:
            st.markdown('<div class="light-btn">', unsafe_allow_html=True)
            if st.button("↺ Re-extract"):
                st.session_state.timeline_generated = False
                st.session_state.timeline_data = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div style="height:0.6rem;"></div>', unsafe_allow_html=True)

        if not timeline:
            st.markdown("""
            <div style="text-align:center;padding:3rem 1rem;">
                <div style="font-size:2rem;margin-bottom:0.8rem;">📅</div>
                <div style="font-size:1rem;color:#6b7280;font-weight:500;">No dates found</div>
                <div style="font-size:0.85rem;color:#9ca3af;margin-top:0.4rem;">
                    This document doesn't appear to contain specific dates or timeline events.
                </div>
            </div>
            """, unsafe_allow_html=True)
            return

        types = list(set(e.get("type", "other") for e in timeline))
        all_types = ["all"] + sorted(types)
        type_labels = {
            "all": "All", "deadline": "⏰ Deadlines", "milestone": "🏁 Milestones",
            "event": "📌 Events", "period": "📆 Periods",
            "announcement": "📢 Announcements", "other": "📋 Other"
        }

        selected_type = st.selectbox(
            "Filter by type", all_types,
            format_func=lambda x: type_labels.get(x, x.title()),
            label_visibility="collapsed"
        )

        filtered = timeline if selected_type == "all" else [e for e in timeline if e.get("type") == selected_type]

        high_count = sum(1 for e in timeline if e.get("importance") == "high")

        st.markdown(f"""
        <div style="display:flex;gap:0.6rem;margin-bottom:1.4rem;flex-wrap:wrap;">
            <div class="metric-card" style="flex:1;min-width:100px;">
                <div class="metric-val">{len(timeline)}</div>
                <div class="metric-label">Total Events</div>
            </div>
            <div class="metric-card" style="flex:1;min-width:100px;">
                <div class="metric-val">{high_count}</div>
                <div class="metric-label">High Priority</div>
            </div>
            <div class="metric-card" style="flex:1;min-width:100px;">
                <div class="metric-val">{len(types)}</div>
                <div class="metric-label">Event Types</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        type_colors = {
            "deadline":     {"bg": "fef2f2", "border": "fca5a5", "dot": "dc2626", "label": "⏰ Deadline"},
            "milestone":    {"bg": "f0fdf4", "border": "86efac", "dot": "16a34a", "label": "🏁 Milestone"},
            "event":        {"bg": "eff6ff", "border": "93c5fd", "dot": "2563eb", "label": "📌 Event"},
            "period":       {"bg": "fefce8", "border": "fde68a", "dot": "d97706", "label": "📆 Period"},
            "announcement": {"bg": "faf5ff", "border": "d8b4fe", "dot": "9333ea", "label": "📢 Announcement"},
            "other":        {"bg": "f9fafb", "border": "e5e7eb", "dot": "6b7280", "label": "📋 Other"},
        }
        importance_size   = {"high": "1rem",    "medium": "0.875rem", "low": "0.8rem"}
        importance_weight = {"high": "600",      "medium": "500",      "low": "400"}

        timeline_html = '<div style="position:relative;padding-left:2rem;">'
        timeline_html += '<div style="position:absolute;left:7px;top:8px;bottom:8px;width:2px;background:#e5e7eb;border-radius:2px;"></div>'

        for i, event in enumerate(filtered):
            etype  = event.get("type", "other")
            colors = type_colors.get(etype, type_colors["other"])
            imp    = event.get("importance", "medium")
            is_last = (i == len(filtered) - 1)

            timeline_html += f"""
            <div style="position:relative;margin-bottom:{'0.6rem' if not is_last else '0'};">
                <div style="position:absolute;left:-1.65rem;top:0.85rem;
                            width:14px;height:14px;border-radius:50%;
                            background:#{colors['dot']};border:2px solid #ffffff;
                            box-shadow:0 0 0 2px #{colors['dot']}33;"></div>
                <div style="background:#{colors['bg']};border:1px solid #{colors['border']};
                            border-radius:12px;padding:0.8rem 1rem;">
                    <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:0.5rem;flex-wrap:wrap;">
                        <div style="font-size:0.72rem;font-weight:600;color:#{colors['dot']};text-transform:uppercase;letter-spacing:0.08em;">
                            {colors['label']}
                        </div>
                        <div style="font-size:0.72rem;color:#9ca3af;font-weight:500;">
                            {'⬆ High priority' if imp == 'high' else ('— Medium' if imp == 'medium' else '↓ Low')}
                        </div>
                    </div>
                    <div style="font-size:0.8rem;font-weight:600;color:#111827;margin-top:0.25rem;">
                        📅 {event.get('date', '—')}
                    </div>
                    <div style="font-size:{importance_size.get(imp,'0.875rem')};font-weight:{importance_weight.get(imp,'500')};color:#374151;margin-top:0.3rem;line-height:1.55;">
                        {event.get('event', '')}
                    </div>
                </div>
            </div>
            """

        timeline_html += '</div>'
        st.markdown(timeline_html, unsafe_allow_html=True)

        st.markdown('<div style="height:1.2rem;"></div>', unsafe_allow_html=True)
        lines = ["DOCUMIND AI — DOCUMENT TIMELINE", "=" * 50, ""]
        for e in timeline:
            lines.append(f"[{e.get('type','').upper()}] {e.get('date','')}")
            lines.append(f"  {e.get('event','')}")
            lines.append(f"  Priority: {e.get('importance','')}")
            lines.append("")
        export_text = "\n".join(lines)
        b64 = base64.b64encode(export_text.encode()).decode()
        st.markdown(
            f'<a href="data:text/plain;base64,{b64}" download="timeline.txt" '
            f'style="display:inline-flex;align-items:center;gap:0.4rem;background:#f9fafb;'
            f'color:#374151;border:1px solid #e5e7eb;border-radius:10px;padding:0.48rem 1.1rem;'
            f'font-size:0.82rem;font-family:Inter,sans-serif;text-decoration:none;font-weight:500;">'
            f'📥 Export Timeline</a>',
            unsafe_allow_html=True
        )