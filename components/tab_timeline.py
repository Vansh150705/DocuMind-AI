"""
components/tab_timeline.py
Document Timeline Extractor
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
    "date": "exact date or period as written in document",
    "sort_key": "YYYY-MM-DD format for sorting, best estimate",
    "event": "clear description of what happened or is due (under 20 words)",
    "type": "one of: deadline / milestone / event / period / announcement / other",
    "importance": "high / medium / low"
  }}
]

Rules:
- Extract EVERY date mentioned, even vague ones like Q1 2025 or early 2024
- If no dates exist, return empty array: []
- Sort by sort_key ascending

Document:
{sample}"""

    try:
        response = llm.invoke(prompt)
        raw = response.content.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start == -1 or end == 0:
            return []
        data = json.loads(raw[start:end])
        if isinstance(data, list):
            return sorted(data, key=lambda x: x.get("sort_key", "9999"))
        return []
    except Exception:
        return []


def render_timeline_tab():

    st.markdown(
        '<div style="font-size:0.875rem;color:#6b7280;margin-bottom:1.3rem;line-height:1.65;">'
        'Automatically extracts all dates, events, deadlines, and milestones '
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
        return

    # Re-extract button
    col_r, _ = st.columns([1, 3])
    with col_r:
        st.markdown('<div class="light-btn">', unsafe_allow_html=True)
        if st.button("↺ Re-extract"):
            st.session_state.timeline_generated = False
            st.session_state.timeline_data = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    timeline = st.session_state.timeline_data

    if not timeline:
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem;">
            <div style="font-size:2rem;margin-bottom:0.8rem;">📅</div>
            <div style="font-size:1rem;color:#6b7280;font-weight:500;">No dates found</div>
            <div style="font-size:0.85rem;color:#9ca3af;margin-top:0.4rem;">
                This document does not appear to contain specific dates or timeline events.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Filter
    types = list(set(e.get("type", "other") for e in timeline))
    all_types = ["all"] + sorted(types)
    type_labels = {
        "all": "All", "deadline": "⏰ Deadlines", "milestone": "🏁 Milestones",
        "event": "📌 Events", "period": "📆 Periods",
        "announcement": "📢 Announcements", "other": "📋 Other"
    }
    selected_type = st.selectbox(
        "Filter", all_types,
        format_func=lambda x: type_labels.get(x, x.title()),
        label_visibility="collapsed"
    )
    filtered = timeline if selected_type == "all" else [
        e for e in timeline if e.get("type") == selected_type
    ]

    # Stats
    high_count = sum(1 for e in timeline if e.get("importance") == "high")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{len(timeline)}</div><div class="metric-label">Total Events</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{high_count}</div><div class="metric-label">High Priority</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{len(types)}</div><div class="metric-label">Event Types</div></div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)

    # Inject CSS classes — no inline styles on timeline cards
    st.markdown("""
    <style>
    .tl-wrap { position:relative; padding-left:2rem; margin-top:0.5rem; }
    .tl-line { position:absolute; left:7px; top:8px; bottom:8px; width:2px; background:#e5e7eb; border-radius:2px; }
    .tl-item { position:relative; margin-bottom:0.65rem; }
    .tl-dot  { position:absolute; left:-1.65rem; top:0.85rem; width:14px; height:14px;
                border-radius:50%; border:2px solid #ffffff; }

    .tl-card { border-radius:12px; padding:0.8rem 1rem; border:1px solid; }

    .tl-type  { font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; }
    .tl-pri   { font-size:0.7rem; color:#9ca3af; font-weight:500; }
    .tl-date  { font-size:0.8rem; font-weight:700; color:#111827; margin-top:0.2rem; }
    .tl-event { font-size:0.875rem; color:#374151; margin-top:0.3rem; line-height:1.55; }

    .tl-deadline     { background:#fef2f2; border-color:#fca5a5; }
    .tl-deadline .tl-dot  { background:#dc2626; box-shadow:0 0 0 3px #dc262633; }
    .tl-deadline .tl-type { color:#dc2626; }

    .tl-milestone     { background:#f0fdf4; border-color:#86efac; }
    .tl-milestone .tl-dot  { background:#16a34a; box-shadow:0 0 0 3px #16a34a33; }
    .tl-milestone .tl-type { color:#16a34a; }

    .tl-event-type     { background:#eff6ff; border-color:#93c5fd; }
    .tl-event-type .tl-dot  { background:#2563eb; box-shadow:0 0 0 3px #2563eb33; }
    .tl-event-type .tl-type { color:#2563eb; }

    .tl-period     { background:#fefce8; border-color:#fde68a; }
    .tl-period .tl-dot  { background:#d97706; box-shadow:0 0 0 3px #d9770633; }
    .tl-period .tl-type { color:#d97706; }

    .tl-announcement     { background:#faf5ff; border-color:#d8b4fe; }
    .tl-announcement .tl-dot  { background:#9333ea; box-shadow:0 0 0 3px #9333ea33; }
    .tl-announcement .tl-type { color:#9333ea; }

    .tl-other     { background:#f9fafb; border-color:#e5e7eb; }
    .tl-other .tl-dot  { background:#6b7280; box-shadow:0 0 0 3px #6b728033; }
    .tl-other .tl-type { color:#6b7280; }
    </style>
    """, unsafe_allow_html=True)

    # Type → CSS class mapping
    type_class = {
        "deadline": "tl-deadline",
        "milestone": "tl-milestone",
        "event": "tl-event-type",
        "period": "tl-period",
        "announcement": "tl-announcement",
        "other": "tl-other",
    }
    type_icon = {
        "deadline": "⏰ Deadline", "milestone": "🏁 Milestone",
        "event": "📌 Event", "period": "📆 Period",
        "announcement": "📢 Announcement", "other": "📋 Other",
    }
    pri_label = {
        "high": "⬆ High priority",
        "medium": "— Medium",
        "low": "↓ Low"
    }

    # Build timeline HTML using only CSS classes
    html = '<div class="tl-wrap"><div class="tl-line"></div>'
    for event in filtered:
        etype  = event.get("type", "other")
        imp    = event.get("importance", "medium")
        css    = type_class.get(etype, "tl-other")
        icon   = type_icon.get(etype, "📋 Other")
        date   = event.get("date", "—")
        desc   = event.get("event", "")
        pri    = pri_label.get(imp, "— Medium")

        html += f"""
        <div class="tl-item">
            <div class="tl-dot {css}"></div>
            <div class="tl-card {css}">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span class="tl-type {css}">{icon}</span>
                    <span class="tl-pri">{pri}</span>
                </div>
                <div class="tl-date">📅 {date}</div>
                <div class="tl-event">{desc}</div>
            </div>
        </div>
        """
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

    # Export
    st.markdown('<div style="height:1.2rem;"></div>', unsafe_allow_html=True)
    lines = ["DOCUMIND AI — DOCUMENT TIMELINE", "=" * 50, ""]
    for e in timeline:
        lines.append(f"[{e.get('type','').upper()}] {e.get('date','')}")
        lines.append(f"  {e.get('event','')}")
        lines.append(f"  Priority: {e.get('importance','')}")
        lines.append("")
    b64 = base64.b64encode("\n".join(lines).encode()).decode()
    st.markdown(
        f'<a href="data:text/plain;base64,{b64}" download="timeline.txt" '
        f'style="display:inline-flex;align-items:center;gap:0.4rem;background:#f9fafb;'
        f'color:#374151;border:1px solid #e5e7eb;border-radius:10px;padding:0.48rem 1.1rem;'
        f'font-size:0.82rem;font-family:Inter,sans-serif;text-decoration:none;font-weight:500;">'
        f'📥 Export Timeline</a>',
        unsafe_allow_html=True
    )