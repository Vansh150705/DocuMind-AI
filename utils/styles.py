"""
utils/styles.py
Premium UI — white background, full polish, skeleton loaders,
smooth animations, Settings tab removed.
"""

STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* ============================================================
   BASE — White background throughout
   ============================================================ */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stAppViewBlockContainer"],
.main, .block-container,
section[data-testid="stSidebar"] + div,
[class*="main"] {
    background-color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    color: #111827 !important;
}

.block-container {
    max-width: 820px !important;
    padding: 2.8rem 2rem !important;
    background: #ffffff !important;
}

[data-testid="stSidebar"]    { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ============================================================
   ANIMATIONS
   ============================================================ */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes slideInRight {
    from { opacity: 0; transform: translateX(16px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-16px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes dotBounce {
    0%, 80%, 100% { transform: translateY(0);    opacity: 0.4; }
    40%           { transform: translateY(-7px); opacity: 1;   }
}
@keyframes shimmer {
    0%   { background-position: -600px 0; }
    100% { background-position:  600px 0; }
}
@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.97); }
    to   { opacity: 1; transform: scale(1); }
}
@keyframes pulse {
    0%,100% { opacity: 1; }
    50%     { opacity: 0.45; }
}

/* ============================================================
   BUTTONS
   ============================================================ */
.stButton > button {
    background: #111827 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    padding: 0.65rem 1.4rem !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    width: 100% !important;
    letter-spacing: 0.01em !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12) !important;
}
.stButton > button:hover {
    background: #1f2937 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(17,24,39,0.22) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12) !important;
}

/* Light ghost button */
.light-btn > button,
.light-btn .stButton > button {
    background: #f9fafb !important;
    color: #374151 !important;
    border: 1px solid #e5e7eb !important;
    box-shadow: none !important;
}
.light-btn > button:hover,
.light-btn .stButton > button:hover {
    background: #f3f4f6 !important;
    border-color: #d1d5db !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07) !important;
}

/* ============================================================
   FILE UPLOADER — fully white/light
   ============================================================ */
[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border: 2px dashed #e5e7eb !important;
    border-radius: 16px !important;
    padding: 1.2rem !important;
    transition: border-color 0.2s, background 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #9ca3af !important;
    background: #fafafa !important;
}
[data-testid="stFileUploader"] button,
[data-testid="stFileUploaderDropzone"] button,
[data-testid="baseButton-secondary"] {
    background: #f3f4f6 !important;
    color: #374151 !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.45rem 1rem !important;
    box-shadow: none !important;
    width: auto !important;
}
[data-testid="stFileUploader"] button:hover,
[data-testid="stFileUploaderDropzone"] button:hover {
    background: #e5e7eb !important;
    transform: none !important;
    box-shadow: none !important;
}
[data-testid="stFileUploaderDropzoneInstructions"],
[data-testid="stFileUploaderDropzoneInstructions"] * {
    color: #9ca3af !important;
    font-size: 0.875rem !important;
}

/* ============================================================
   CHAT INPUT — force white on ALL internal elements
   ============================================================ */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] > div > div,
[data-testid="stChatInput"] > div > div > div,
div[class*="stChatInput"],
div[class*="chatInput"] {
    background: #ffffff !important;
    border: 1.5px solid #e5e7eb !important;
    border-radius: 16px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #111827 !important;
    box-shadow: 0 0 0 3px rgba(17,24,39,0.08) !important;
}
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] textarea:active {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    color: #111827 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    line-height: 1.5 !important;
    caret-color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #9ca3af !important;
    -webkit-text-fill-color: #9ca3af !important;
}
[data-testid="stChatInput"] button[kind="primaryFormSubmit"],
[data-testid="stChatInput"] button {
    background: #111827 !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    border: none !important;
    width: auto !important;
    transition: opacity 0.2s !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] button:hover {
    opacity: 0.8 !important;
    transform: none !important;
    box-shadow: none !important;
}
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div {
    background: #ffffff !important;
}

/* ============================================================
   SELECTBOX
   ============================================================ */
[data-testid="stSelectbox"] > div > div {
    background: #ffffff !important;
    border: 1.5px solid #e5e7eb !important;
    border-radius: 10px !important;
    color: #111827 !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s !important;
}
[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: #111827 !important;
    box-shadow: 0 0 0 3px rgba(17,24,39,0.08) !important;
}

/* ============================================================
   TABS
   ============================================================ */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1.5px solid #f3f4f6 !important;
    gap: 0 !important;
    margin-bottom: 1.6rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #9ca3af !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    border: none !important;
    padding: 0.75rem 1.25rem !important;
    transition: color 0.18s !important;
    letter-spacing: 0.01em !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #6b7280 !important; }
.stTabs [aria-selected="true"] {
    color: #111827 !important;
    border-bottom: 2px solid #111827 !important;
    background: transparent !important;
    font-weight: 600 !important;
}

/* ============================================================
   METRIC CARDS
   ============================================================ */
.metric-card {
    background: #ffffff;
    border: 1px solid #f3f4f6;
    border-radius: 14px;
    padding: 1.1rem 1rem;
    text-align: center;
    transition: box-shadow 0.22s, transform 0.22s;
    animation: fadeUp 0.4s ease both;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.metric-card:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.09);
    transform: translateY(-2px);
}
.metric-val {
    font-family: 'DM Serif Display', serif;
    font-size: 1.7rem;
    color: #111827;
    line-height: 1.2;
}
.metric-label {
    font-size: 0.68rem;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 0.25rem;
    font-weight: 500;
}

/* ============================================================
   CHAT MESSAGES
   ============================================================ */
.msg-user {
    display: flex;
    justify-content: flex-end;
    margin: 1rem 0;
    animation: slideInRight 0.25s cubic-bezier(0.4, 0, 0.2, 1) both;
}
.msg-user-inner {
    background: #111827;
    color: #f9fafb;
    padding: 0.9rem 1.2rem;
    border-radius: 18px 18px 4px 18px;
    max-width: 76%;
    font-size: 0.938rem;
    line-height: 1.7;
    box-shadow: 0 2px 12px rgba(17,24,39,0.18);
    letter-spacing: 0.01em;
}
.msg-bot {
    display: flex;
    justify-content: flex-start;
    margin: 1rem 0;
    animation: slideInLeft 0.25s cubic-bezier(0.4, 0, 0.2, 1) both;
}
.msg-bot-inner {
    background: #ffffff;
    color: #111827;
    padding: 0.9rem 1.2rem;
    border-radius: 18px 18px 18px 4px;
    max-width: 84%;
    font-size: 0.938rem;
    line-height: 1.75;
    border: 1px solid #f3f4f6;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    letter-spacing: 0.01em;
}

/* ============================================================
   TYPING INDICATOR
   ============================================================ */
.typing-indicator {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.75rem 1.1rem;
    background: #ffffff;
    border: 1px solid #f3f4f6;
    border-radius: 18px 18px 18px 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    animation: fadeIn 0.2s ease both;
    margin: 0.6rem 0;
}
.typing-text {
    font-size: 0.82rem;
    color: #6b7280;
    font-style: italic;
    letter-spacing: 0.01em;
}
.typing-dots { display: flex; gap: 4px; align-items: center; }
.typing-dots span {
    width: 6px; height: 6px;
    background: #d1d5db;
    border-radius: 50%;
    display: inline-block;
    animation: dotBounce 1.3s infinite ease-in-out;
}
.typing-dots span:nth-child(2) { animation-delay: 0.16s; }
.typing-dots span:nth-child(3) { animation-delay: 0.32s; }

/* ============================================================
   SKELETON LOADER
   ============================================================ */
.skeleton-line {
    background: linear-gradient(90deg, #f3f4f6 25%, #e9eaec 50%, #f3f4f6 75%);
    background-size: 600px 100%;
    animation: shimmer 1.4s infinite linear;
    border-radius: 6px;
    height: 14px;
    margin-bottom: 10px;
}
.skeleton-line.short  { width: 55%; }
.skeleton-line.medium { width: 78%; }
.skeleton-line.full   { width: 100%; }
.skeleton-wrap {
    background: #ffffff;
    border: 1px solid #f3f4f6;
    border-radius: 18px 18px 18px 4px;
    padding: 1rem 1.2rem;
    max-width: 84%;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    animation: fadeIn 0.2s ease both;
}

/* ============================================================
   SOURCE CHIPS
   ============================================================ */
.source-chip {
    display: inline-block;
    background: #f9fafb;
    color: #6b7280;
    font-size: 0.7rem;
    font-weight: 500;
    padding: 0.22rem 0.65rem;
    border-radius: 20px;
    margin: 0.12rem;
    border: 1px solid #e5e7eb;
    transition: background 0.15s, color 0.15s;
    letter-spacing: 0.01em;
}
.source-chip:hover { background: #f3f4f6; color: #374151; }

/* ============================================================
   CONFIDENCE BAR
   ============================================================ */
.conf-bar-outer {
    background: #f3f4f6;
    border-radius: 6px;
    height: 5px;
    margin-top: 0.45rem;
    overflow: hidden;
}
.conf-bar-inner {
    border-radius: 6px;
    height: 5px;
    transition: width 0.7s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ============================================================
   DNA / INFO CARDS
   ============================================================ */
.dna-card {
    background: #ffffff;
    border: 1px solid #f3f4f6;
    border-radius: 16px;
    padding: 1.3rem 1.5rem;
    margin: 0.8rem 0;
    animation: fadeUp 0.35s ease both;
    transition: box-shadow 0.22s, transform 0.22s;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.dna-card:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    transform: translateY(-1px);
}
.dna-tag {
    display: inline-block;
    background: #f9fafb;
    color: #374151;
    font-size: 0.76rem;
    font-weight: 500;
    padding: 0.28rem 0.75rem;
    border-radius: 20px;
    margin: 0.2rem;
    border: 1px solid #e5e7eb;
    transition: background 0.15s, transform 0.15s;
    letter-spacing: 0.01em;
}
.dna-tag:hover { background: #f3f4f6; transform: translateY(-1px); }
.dna-bar-label {
    font-size: 0.775rem;
    color: #6b7280;
    font-weight: 500;
    margin: 0.65rem 0 0.25rem 0;
}
.dna-bar-outer {
    background: #f3f4f6;
    border-radius: 6px;
    height: 8px;
    overflow: hidden;
}
.dna-bar-inner {
    border-radius: 6px;
    height: 8px;
    transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ============================================================
   SECTION LABEL
   ============================================================ */
.section-label {
    font-size: 0.7rem;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    margin-bottom: 0.7rem;
    font-weight: 600;
}

/* ============================================================
   DOC PILLS + STATUS BADGE
   ============================================================ */
.doc-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 20px;
    padding: 0.36rem 0.9rem;
    font-size: 0.82rem;
    color: #374151;
    margin: 0.2rem;
    animation: fadeIn 0.4s ease both;
    transition: box-shadow 0.2s;
    font-weight: 500;
}
.doc-pill:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.38rem 0.9rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    animation: fadeIn 0.4s ease both;
    letter-spacing: 0.01em;
}
.status-ready {
    background: #f0fdf4;
    color: #16a34a;
    border: 1px solid #bbf7d0;
}

/* ============================================================
   UPLOAD FEEDBACK
   ============================================================ */
.upload-success {
    background: #f0fdf4;
    color: #15803d;
    border: 1px solid #bbf7d0;
    border-radius: 12px;
    padding: 0.85rem 1.2rem;
    font-size: 0.875rem;
    font-weight: 500;
    animation: fadeUp 0.35s ease both;
    display: flex;
    align-items: center;
    gap: 0.55rem;
    margin: 0.65rem 0;
    letter-spacing: 0.01em;
}

/* ============================================================
   STEP PROGRESS LOADER
   ============================================================ */
.step-loader {
    background: #ffffff;
    border: 1px solid #f3f4f6;
    border-radius: 16px;
    padding: 1.5rem 1.75rem;
    animation: fadeUp 0.3s ease both;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}
.step-row {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    padding: 0.5rem 0;
    font-size: 0.9rem;
    transition: all 0.22s;
}
.step-icon { font-size: 1rem; width: 1.4rem; text-align: center; }
.step-text          { color: #9ca3af; }
.step-text.active   { color: #111827; font-weight: 600; }
.step-text.done     { color: #16a34a; font-weight: 500; }
.progress-track {
    height: 3px;
    background: #f3f4f6;
    border-radius: 3px;
    margin-top: 1.2rem;
    overflow: hidden;
}

/* ============================================================
   EMPTY STATE
   ============================================================ */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    animation: fadeUp 0.5s ease both;
}
.empty-icon-wrap {
    width: 72px; height: 72px;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 20px;
    display: flex; align-items: center; justify-content: center;
    font-size: 2rem;
    margin: 0 auto 1.4rem auto;
    animation: scaleIn 0.5s ease 0.1s both;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}
.empty-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.6rem;
    color: #111827;
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}
.empty-sub {
    font-size: 0.9rem;
    color: #6b7280;
    line-height: 1.7;
    max-width: 340px;
    margin: 0 auto;
}
.empty-feature-row {
    display: flex;
    justify-content: center;
    gap: 0.6rem;
    margin-top: 1.5rem;
    flex-wrap: wrap;
}
.empty-feature-chip {
    display: inline-flex; align-items: center; gap: 0.35rem;
    background: #f9fafb; border: 1px solid #e5e7eb;
    border-radius: 20px; padding: 0.35rem 0.85rem;
    font-size: 0.78rem; color: #374151; font-weight: 500;
}

/* ============================================================
   ANALYTICS BARS
   ============================================================ */
.analytics-bar-outer {
    background: #f3f4f6;
    border-radius: 6px;
    height: 10px;
    margin-top: 0.3rem;
    overflow: hidden;
}
.analytics-bar-inner {
    border-radius: 6px;
    height: 10px;
    background: #111827;
    transition: width 0.7s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ============================================================
   SUGGESTION PILLS
   ============================================================ */
.sug-pill-wrap .stButton > button {
    background: #ffffff !important;
    color: #374151 !important;
    border: 1px solid #e5e7eb !important;
    font-size: 0.855rem !important;
    font-weight: 400 !important;
    padding: 0.6rem 1rem !important;
    border-radius: 12px !important;
    text-align: left !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    transition: all 0.18s !important;
}
.sug-pill-wrap .stButton > button:hover {
    border-color: #111827 !important;
    color: #111827 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    background: #fafafa !important;
}

/* ============================================================
   INFO / WARNING BANNER
   ============================================================ */
.info-banner {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 12px;
    padding: 0.75rem 1rem;
    font-size: 0.84rem;
    color: #1d4ed8;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 500;
    animation: fadeIn 0.3s ease both;
}
.warn-banner {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-radius: 12px;
    padding: 0.8rem 1.1rem;
    font-size: 0.84rem;
    color: #92400e;
    margin-top: 1.2rem;
}

/* ============================================================
   DIVIDER
   ============================================================ */
.dm-divider {
    height: 1px;
    background: #f3f4f6;
    margin: 1.4rem 0;
}

/* ============================================================
   HEADER GRADIENT ACCENT
   ============================================================ */
.header-accent {
    height: 3px;
    width: 44px;
    background: linear-gradient(90deg, #111827, #6b7280);
    border-radius: 3px;
    margin: 0.7rem 0 2rem 0;
    animation: fadeIn 0.6s ease 0.2s both;
}

#MainMenu, footer, header { visibility: hidden; }
</style>

<script>
// ============================================================
// VOICE MIC — injected into chat input box (like ChatGPT)
// Uses browser Web Speech API. No external API needed.
// ============================================================
function injectVoiceIntoChat() {
    const chatInput = document.querySelector('[data-testid="stChatInput"]');
    if (!chatInput) return;

    const existing = chatInput.querySelector('#dm-mic-btn');
    if (existing) existing.remove();

    const micBtn = document.createElement('button');
    micBtn.id = 'dm-mic-btn';
    micBtn.type = 'button';
    micBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>';
    micBtn.title = 'Voice input (Chrome/Edge)';
    micBtn.style.cssText = `
        position: absolute;
        right: 52px; bottom: 9px;
        width: 32px; height: 32px;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        background: #f9fafb;
        color: #6b7280;
        font-size: 0.9rem;
        cursor: pointer;
        display: flex; align-items: center; justify-content: center;
        z-index: 999;
        transition: all 0.18s;
    `;

    chatInput.style.position = 'relative';
    chatInput.appendChild(micBtn);

    let recognition = null;
    let listening = false;

    micBtn.addEventListener('mouseenter', () => {
        if (!listening) { micBtn.style.background = '#f3f4f6'; micBtn.style.borderColor = '#d1d5db'; micBtn.style.color = '#374151'; }
    });
    micBtn.addEventListener('mouseleave', () => {
        if (!listening) { micBtn.style.background = '#f9fafb'; micBtn.style.borderColor = '#e5e7eb'; micBtn.style.color = '#6b7280'; }
    });

    micBtn.addEventListener('click', function(e) {
        e.preventDefault(); e.stopPropagation();

        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('Voice input requires Chrome or Edge browser.');
            return;
        }

        if (listening) {
            if (recognition) recognition.stop();
            return;
        }

        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SR();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
            listening = true;
            micBtn.style.background = '#fef2f2';
            micBtn.style.borderColor = '#fca5a5';
            micBtn.style.color = '#dc2626';
            micBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="#dc2626"><circle cx="12" cy="12" r="10"/></svg>';
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const textarea = chatInput.querySelector('textarea');
            if (textarea) {
                const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
                setter.call(textarea, transcript);
                textarea.dispatchEvent(new Event('input', { bubbles: true }));
                textarea.focus();
            }
        };

        recognition.onerror = (event) => { console.error('Speech error:', event.error); };

        recognition.onend = () => {
            listening = false;
            micBtn.style.background = '#f9fafb';
            micBtn.style.borderColor = '#e5e7eb';
            micBtn.style.color = '#6b7280';
            micBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>';
        };

        recognition.start();
    });
}

// Retry injection multiple times to handle Streamlit's delayed render
function tryInject(attempts) {
    if (attempts <= 0) return;
    const ci = document.querySelector('[data-testid="stChatInput"]');
    if (ci && !ci.querySelector('#dm-mic-btn')) {
        injectVoiceIntoChat();
    }
    setTimeout(() => tryInject(attempts - 1), 600);
}

document.addEventListener('DOMContentLoaded', () => tryInject(8));
setTimeout(() => tryInject(8), 500);

// Watch DOM for Streamlit rerenders
const _obs = new MutationObserver(() => {
    const ci = document.querySelector('[data-testid="stChatInput"]');
    if (ci && !ci.querySelector('#dm-mic-btn')) {
        injectVoiceIntoChat();
    }
});
_obs.observe(document.body, { childList: true, subtree: true });
</script>
"""