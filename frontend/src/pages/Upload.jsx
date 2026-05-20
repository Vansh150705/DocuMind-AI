import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL || ''

export default function Upload() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('pdf')
  const [loading, setLoading] = useState(false)
  const [loadingStep, setLoadingStep] = useState(0)
  const [error, setError] = useState('')
  const [files, setFiles] = useState([])
  const [url, setUrl] = useState('')
  const [ytUrl, setYtUrl] = useState('')
  const [videoId, setVideoId] = useState('')
  const [dragOver, setDragOver] = useState(false)

  const extractVideoId = (url) => {
    const m = url.match(/(?:v=|youtu\.be\/|embed\/|shorts\/)([a-zA-Z0-9_-]{11})/)
    return m ? m[1] : null
  }

  const handleYtUrlChange = (val) => {
    setYtUrl(val)
    setVideoId(extractVideoId(val) || '')
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const dropped = [...e.dataTransfer.files].filter(f => f.type === 'application/pdf')
    if (dropped.length) setFiles(dropped)
  }

  const pdfSteps = [
    { icon: '📖', label: 'Reading your PDF' },
    { icon: '✂️', label: 'Splitting into chunks' },
    { icon: '🔢', label: 'Generating embeddings' },
    { icon: '🗃️', label: 'Building vector index' },
    { icon: '🧬', label: 'Analysing Document DNA' },
    { icon: '✅', label: 'All done' },
  ]
  const webSteps = [
    { icon: '🌐', label: 'Fetching the page' },
    { icon: '🧹', label: 'Cleaning content' },
    { icon: '🔢', label: 'Generating embeddings' },
    { icon: '🗃️', label: 'Building vector index' },
    { icon: '✅', label: 'All done' },
  ]
  const ytSteps = [
    { icon: '▶', label: 'Fetching transcript' },
    { icon: '✂️', label: 'Splitting into chunks' },
    { icon: '🔢', label: 'Generating embeddings' },
    { icon: '🗃️', label: 'Building vector index' },
    { icon: '✅', label: 'All done' },
  ]

  const simulateSteps = async (steps, apiCall) => {
    setLoading(true); setError(''); setLoadingStep(0)
    for (let i = 0; i < steps.length - 1; i++) {
      setLoadingStep(i)
      await new Promise(r => setTimeout(r, i === 0 ? 800 : 1200))
    }
    try {
      await apiCall()
      setLoadingStep(steps.length - 1)
      await new Promise(r => setTimeout(r, 500))
      navigate('/chat')
    } catch(e) {
      setError(e.response?.data?.error || 'Something went wrong.')
      setLoading(false); setLoadingStep(0)
    }
  }

  const handlePDF = () => {
    if (!files.length) return
    const fd = new FormData()
    files.forEach(f => fd.append('files', f))
    simulateSteps(pdfSteps, () => axios.post(`${API}/api/upload/pdf`, fd))
  }
  const handleWeb = () => {
    if (!url) return
    const fd = new FormData(); fd.append('url', url)
    simulateSteps(webSteps, () => axios.post(`${API}/api/upload/web`, fd))
  }
  const handleYT = () => {
    if (!ytUrl) return
    const fd = new FormData(); fd.append('url', ytUrl)
    simulateSteps(ytSteps, () => axios.post(`${API}/api/upload/youtube`, fd))
  }

  const activeSteps = activeTab === 'pdf' ? pdfSteps : activeTab === 'web' ? webSteps : ytSteps
  const progress = loading ? Math.round((loadingStep / (activeSteps.length - 1)) * 100) : 0

  // SVG Characters from landing page
  const PaigeSVG = (
    <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="100" cy="85" r="38" fill="#fef3c7"/>
      <ellipse cx="100" cy="52" rx="30" ry="14" fill="#1a1a1a"/>
      <rect x="70" y="52" width="60" height="10" rx="5" fill="#1a1a1a"/>
      <circle cx="88" cy="82" r="5" fill="#1a1a1a"/><circle cx="112" cy="82" r="5" fill="#1a1a1a"/>
      <circle cx="90" cy="80" r="2" fill="white"/><circle cx="114" cy="80" r="2" fill="white"/>
      <path d="M88 96 Q100 106 112 96" stroke="#1a1a1a" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
      <circle cx="78" cy="92" r="7" fill="#fca5a5" opacity="0.5"/><circle cx="122" cy="92" r="7" fill="#fca5a5" opacity="0.5"/>
      <path d="M62 135 Q62 118 100 118 Q138 118 138 135 L142 170 Q100 175 58 170 Z" fill="#ef4444"/>
      <path d="M62 125 L42 145" stroke="#fef3c7" strokeWidth="12" strokeLinecap="round"/>
      <path d="M138 125 L158 145" stroke="#fef3c7" strokeWidth="12" strokeLinecap="round"/>
      <rect x="20" y="138" width="30" height="38" rx="4" fill="white" stroke="#e5e7eb" strokeWidth="1.5"/>
      <rect x="24" y="144" width="22" height="2.5" rx="1.5" fill="#e5e7eb"/>
      <rect x="24" y="150" width="18" height="2.5" rx="1.5" fill="#e5e7eb"/>
      <rect x="24" y="156" width="20" height="2.5" rx="1.5" fill="#e5e7eb"/>
      <rect x="82" y="168" width="14" height="28" rx="7" fill="#1a1a1a"/><rect x="104" y="168" width="14" height="28" rx="7" fill="#1a1a1a"/>
      <ellipse cx="89" cy="196" rx="12" ry="6" fill="#0a0a0a"/><ellipse cx="111" cy="196" rx="12" ry="6" fill="#0a0a0a"/>
    </svg>
  )
  const WebbSVG = (
    <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="100" cy="85" r="38" fill="#dbeafe"/>
      <ellipse cx="100" cy="52" rx="28" ry="12" fill="#f59e0b"/>
      <rect x="72" y="48" width="56" height="16" rx="8" fill="#f59e0b"/>
      <ellipse cx="72" cy="68" rx="8" ry="14" fill="#f59e0b"/><ellipse cx="128" cy="68" rx="8" ry="14" fill="#f59e0b"/>
      <circle cx="88" cy="82" r="9" stroke="#1a1a1a" strokeWidth="2" fill="none"/><circle cx="112" cy="82" r="9" stroke="#1a1a1a" strokeWidth="2" fill="none"/>
      <line x1="97" y1="82" x2="103" y2="82" stroke="#1a1a1a" strokeWidth="2"/>
      <circle cx="88" cy="82" r="2" fill="white"/><circle cx="112" cy="82" r="2" fill="white"/>
      <path d="M86 96 Q100 108 114 96" stroke="#1a1a1a" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
      <path d="M62 135 Q62 118 100 118 Q138 118 138 135 L142 170 Q100 175 58 170 Z" fill="#2563eb"/>
      <circle cx="100" cy="144" r="10" stroke="white" strokeWidth="1.5" fill="none"/>
      <path d="M100 134 Q106 144 100 154 Q94 144 100 134" stroke="white" strokeWidth="1.5" fill="none"/>
      <line x1="90" y1="144" x2="110" y2="144" stroke="white" strokeWidth="1.5"/>
      <path d="M62 125 L42 148" stroke="#dbeafe" strokeWidth="12" strokeLinecap="round"/>
      <path d="M138 125 L158 148" stroke="#dbeafe" strokeWidth="12" strokeLinecap="round"/>
      <rect x="140" y="142" width="32" height="22" rx="4" fill="#1a1a1a"/>
      <rect x="142" y="144" width="28" height="16" rx="2" fill="#3b82f6"/>
      <rect x="136" y="163" width="40" height="3" rx="1.5" fill="#1a1a1a"/>
      <rect x="82" y="168" width="14" height="28" rx="7" fill="#1a1a1a"/><rect x="104" y="168" width="14" height="28" rx="7" fill="#1a1a1a"/>
      <ellipse cx="89" cy="196" rx="12" ry="6" fill="#0a0a0a"/><ellipse cx="111" cy="196" rx="12" ry="6" fill="#0a0a0a"/>
    </svg>
  )
  const YukiSVG = (
    <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="100" cy="85" r="38" fill="#fce7f3"/>
      <ellipse cx="100" cy="54" rx="32" ry="16" fill="#7c3aed"/>
      <path d="M68 75 Q68 50 100 50 Q132 50 132 75" stroke="#7c3aed" strokeWidth="6" fill="none" strokeLinecap="round"/>
      <rect x="60" y="72" width="14" height="18" rx="7" fill="#7c3aed"/><rect x="126" y="72" width="14" height="18" rx="7" fill="#7c3aed"/>
      <circle cx="88" cy="82" r="5" fill="#1a1a1a"/><circle cx="112" cy="82" r="5" fill="#1a1a1a"/>
      <circle cx="90" cy="80" r="2" fill="white"/><circle cx="114" cy="80" r="2" fill="white"/>
      <path d="M88 97 Q100 107 112 97" stroke="#1a1a1a" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
      <circle cx="78" cy="91" r="7" fill="#f9a8d4" opacity="0.6"/><circle cx="122" cy="91" r="7" fill="#f9a8d4" opacity="0.6"/>
      <path d="M62 135 Q62 118 100 118 Q138 118 138 135 L142 170 Q100 175 58 170 Z" fill="#dc2626"/>
      <rect x="88" y="134" width="24" height="18" rx="4" fill="white"/>
      <path d="M95 139 L108 143 L95 147 Z" fill="#dc2626"/>
      <path d="M62 125 L38 140" stroke="#fce7f3" strokeWidth="12" strokeLinecap="round"/>
      <path d="M138 125 L162 140" stroke="#fce7f3" strokeWidth="12" strokeLinecap="round"/>
      <rect x="22" y="130" width="22" height="32" rx="4" fill="#1a1a1a"/>
      <rect x="24" y="133" width="18" height="22" rx="2" fill="#ef4444"/>
      <path d="M29 140 L38 144 L29 148 Z" fill="white"/>
      <rect x="82" y="168" width="14" height="28" rx="7" fill="#1a1a1a"/><rect x="104" y="168" width="14" height="28" rx="7" fill="#1a1a1a"/>
      <ellipse cx="89" cy="196" rx="12" ry="6" fill="#0a0a0a"/><ellipse cx="111" cy="196" rx="12" ry="6" fill="#0a0a0a"/>
    </svg>
  )

  const currentChar = activeTab === 'pdf' ? PaigeSVG : activeTab === 'web' ? WebbSVG : YukiSVG
  const charName = activeTab === 'pdf' ? 'Paige' : activeTab === 'web' ? 'Webb' : 'Yuki'
  const charRole = activeTab === 'pdf' ? 'the PDF Reader' : activeTab === 'web' ? 'the Web Surfer' : 'the Video Nerd'
  const charLine = activeTab === 'pdf'
    ? 'Drop any PDF and I will read it cover to cover.'
    : activeTab === 'web' ? 'Paste any URL and I will scrape it for you.'
    : 'Share a YouTube link and I will get the full transcript.'

  const tabs = [
    { id: 'pdf', icon: '📄', label: 'Paige', sub: 'PDF' },
    { id: 'web', icon: '🌐', label: 'Webb', sub: 'Website' },
    { id: 'youtube', icon: '▶', label: 'Yuki', sub: 'YouTube' },
  ]

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@400;500;600&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'DM Sans', sans-serif; background: #ffffff; }

        .up-shell {
          min-height: 100vh;
          background: #ffffff;
          position: relative;
          overflow-x: hidden;
        }
        .up-bg {
          position: fixed; inset: 0;
          background-image: radial-gradient(circle, #e0e0e0 1px, transparent 1px);
          background-size: 28px 28px;
          opacity: 0.5;
          pointer-events: none;
        }
        .up-glow {
          position: fixed;
          top: 50%; left: 50%;
          transform: translate(-50%, -50%);
          width: 800px; height: 800px;
          background: radial-gradient(circle, rgba(255,255,255,1) 0%, rgba(255,255,255,0) 65%);
          pointer-events: none;
        }

        .up-nav {
          position: fixed;
          top: 24px; left: 0; right: 0;
          padding: 0 32px;
          z-index: 100;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        .nav-back {
          background: rgba(255,255,255,0.85);
          backdrop-filter: blur(12px);
          border: 1px solid #e2e2e2;
          border-radius: 100px;
          padding: 9px 18px;
          font-size: 13px;
          font-weight: 500;
          color: #5a5a5a;
          cursor: pointer;
          font-family: 'DM Sans', sans-serif;
          transition: all 0.2s;
          box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        }
        .nav-back:hover { border-color: #0a0a0a; color: #0a0a0a; }
        .nav-logo {
          font-family: 'Syne', sans-serif;
          font-weight: 800;
          font-size: 20px;
          color: #0a0a0a;
        }

        .up-main {
          min-height: 100vh;
          display: grid;
          grid-template-columns: 1fr 1.1fr;
          gap: 60px;
          align-items: center;
          max-width: 1280px;
          margin: 0 auto;
          padding: 100px 60px 60px;
          position: relative;
          z-index: 1;
        }

        /* ── LEFT — Character + Pitch ── */
        .left-side {
          display: flex;
          flex-direction: column;
          align-items: flex-start;
        }
        .badge {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          background: #f8f8f8;
          border: 1px solid #e2e2e2;
          border-radius: 100px;
          padding: 6px 14px;
          font-size: 11px;
          font-weight: 600;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          color: #5a5a5a;
          margin-bottom: 24px;
        }
        .badge-dot { width:6px; height:6px; background:#22c55e; border-radius:50%; animation:pulse 2s infinite; display:block; }
        @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(1.3)} }

        .left-heading {
          font-family: 'Syne', sans-serif;
          font-size: 52px;
          font-weight: 800;
          line-height: 1.0;
          letter-spacing: -0.04em;
          color: #0a0a0a;
          margin-bottom: 18px;
        }
        .left-heading em { font-style: italic; font-weight: 300; color: #5a5a5a; }
        .left-sub {
          font-size: 16px;
          color: #5a5a5a;
          line-height: 1.7;
          margin-bottom: 36px;
          max-width: 420px;
        }

        .char-wrap {
          width: 220px;
          margin-bottom: 24px;
          animation: charBob 4s ease-in-out infinite;
        }
        @keyframes charBob { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }
        .char-wrap svg { width: 100%; height: auto; }
        .char-card-info {
          background: #f8f8f8;
          border: 1px solid #e2e2e2;
          border-radius: 16px;
          padding: 16px 20px;
          max-width: 360px;
        }
        .char-name-row {
          font-family: 'Syne', sans-serif;
          font-size: 18px;
          font-weight: 800;
          color: #0a0a0a;
          margin-bottom: 4px;
        }
        .char-name-row em { font-style:italic; font-weight: 400; color: #5a5a5a; margin-left: 6px; }
        .char-quote {
          font-size: 14px;
          color: #5a5a5a;
          line-height: 1.5;
          font-style: italic;
        }

        /* ── RIGHT — Upload Card ── */
        .right-side {
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .up-card {
          background: #ffffff;
          border: 1.5px solid #e2e2e2;
          border-radius: 24px;
          padding: 32px;
          width: 100%;
          max-width: 500px;
          box-shadow: 0 24px 80px rgba(0,0,0,0.08);
        }

        .tab-row {
          display: grid;
          grid-template-columns: 1fr 1fr 1fr;
          gap: 6px;
          background: #f0f0f0;
          border-radius: 14px;
          padding: 4px;
          margin-bottom: 28px;
        }
        .tab-btn {
          border: none;
          border-radius: 10px;
          padding: 11px 6px;
          font-family: 'DM Sans', sans-serif;
          font-size: 13px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 3px;
          background: transparent;
          color: #a0a0a0;
        }
        .tab-btn.active {
          background: #ffffff;
          color: #0a0a0a;
          box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .tab-btn .tab-emoji { font-size: 18px; }
        .tab-btn .tab-sub { font-size: 9px; font-weight:500; color:#c0c0c0; letter-spacing:0.06em; text-transform: uppercase; }
        .tab-btn.active .tab-sub { color:#5a5a5a; }

        .section-title {
          font-family: 'Syne', sans-serif;
          font-size: 22px;
          font-weight: 700;
          color: #0a0a0a;
          margin-bottom: 6px;
        }
        .section-sub {
          font-size: 14px;
          color: #a0a0a0;
          margin-bottom: 20px;
          line-height: 1.6;
        }

        .drop-zone {
          border: 2px dashed #e2e2e2;
          border-radius: 16px;
          padding: 28px 20px;
          text-align: center;
          cursor: pointer;
          transition: all 0.25s;
          background: #fafafa;
          margin-bottom: 12px;
          display: block;
        }
        .drop-zone:hover, .drop-zone.over {
          border-color: #0a0a0a;
          background: #f5f5f5;
        }
        .drop-emoji { font-size: 36px; display: block; margin-bottom: 10px; }
        .drop-main { font-size: 14px; font-weight: 600; color: #374151; }
        .drop-hint { font-size: 12px; color: #c0c0c0; margin-top: 4px; }

        .file-badge {
          display: flex;
          align-items: center;
          gap: 8px;
          background: #f0fdf4;
          border: 1px solid #bbf7d0;
          border-radius: 10px;
          padding: 10px 14px;
          font-size: 13px;
          color: #15803d;
          font-weight: 500;
          margin-bottom: 8px;
        }

        .url-input {
          width: 100%;
          border: 1.5px solid #e2e2e2;
          border-radius: 12px;
          padding: 14px 16px;
          font-size: 15px;
          font-family: 'DM Sans', sans-serif;
          color: #0a0a0a;
          outline: none;
          transition: all 0.2s;
          background: #fafafa;
          margin-bottom: 14px;
        }
        .url-input:focus { border-color: #0a0a0a; background: #fff; box-shadow: 0 0 0 3px rgba(10,10,10,0.05); }
        .url-input::placeholder { color: #c0c0c0; }

        .yt-preview {
          position: relative;
          border-radius: 12px;
          overflow: hidden;
          margin-bottom: 14px;
          border: 1px solid #e2e2e2;
        }
        .yt-preview img { width: 100%; display: block; }
        .yt-overlay {
          position: absolute; inset: 0;
          background: rgba(0,0,0,0.3);
          display: flex; align-items: center; justify-content: center;
        }
        .yt-play-btn {
          width: 52px; height: 52px;
          background: rgba(255,255,255,0.95);
          border-radius: 50%;
          display: flex; align-items: center; justify-content: center;
          font-size: 20px;
          box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        }

        .submit-btn {
          width: 100%;
          background: #0a0a0a;
          color: white;
          border: none;
          border-radius: 12px;
          padding: 16px;
          font-size: 15px;
          font-weight: 600;
          font-family: 'DM Sans', sans-serif;
          cursor: pointer;
          transition: all 0.25s;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
        }
        .submit-btn:hover:not(:disabled) { background: #222; transform: translateY(-1px); box-shadow: 0 8px 24px rgba(0,0,0,0.15); }
        .submit-btn:disabled { background: #e2e2e2; color: #a0a0a0; cursor: not-allowed; }

        .progress-section {
          background: #fafafa;
          border: 1px solid #e2e2e2;
          border-radius: 16px;
          padding: 22px;
          animation: fadeUp 0.3s ease;
        }
        @keyframes fadeUp { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
        .progress-header { display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px; }
        .progress-label { font-size: 13px; font-weight: 600; color: #0a0a0a; }
        .progress-pct { font-size: 14px; font-weight: 800; color: #0a0a0a; font-family: 'Syne', sans-serif; }
        .progress-bar-track { height:6px; background:#e2e2e2; border-radius:3px; overflow:hidden; margin-bottom:18px; }
        .progress-bar-fill { height:100%; background: linear-gradient(90deg, #0a0a0a 0%, #444 100%); border-radius:3px; transition: width 0.8s cubic-bezier(0.4,0,0.2,1); }
        .steps-list { display: flex; flex-direction: column; gap: 10px; }
        .step-row { display: flex; align-items: center; gap: 12px; font-size: 13px; transition: all 0.3s; }
        .step-dot {
          width: 26px; height: 26px;
          border-radius: 50%;
          display: flex; align-items: center; justify-content: center;
          font-size: 12px;
          flex-shrink: 0;
          transition: all 0.3s;
        }
        .step-dot.done { background: #0a0a0a; color: white; }
        .step-dot.active { background: #f0f0f0; border: 2px solid #0a0a0a; animation: stepPulse 1.5s infinite; }
        .step-dot.pending { background: #f0f0f0; color: #c0c0c0; }
        @keyframes stepPulse { 0%,100%{box-shadow:0 0 0 0 rgba(10,10,10,0.25)} 50%{box-shadow:0 0 0 6px rgba(10,10,10,0)} }
        .step-label.done { color: #0a0a0a; font-weight: 500; }
        .step-label.active { color: #0a0a0a; font-weight: 600; }
        .step-label.pending { color: #c0c0c0; }

        .error-box { background: #fef2f2; border: 1px solid #fca5a5; border-radius: 10px; padding: 10px 14px; font-size: 13px; color: #dc2626; margin-top: 12px; }

        .powered-by {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          margin-top: 20px;
          font-size: 11px;
          color: #c0c0c0;
        }
        .pb-dot { width: 3px; height: 3px; background: #c0c0c0; border-radius: 50%; }

@media (max-width: 1024px) {
  .up-main { grid-template-columns: 1fr; padding: 100px 24px 40px; gap: 40px; }
  .left-side { align-items: center; text-align: center; }
  .left-sub { max-width: 100%; }
  .left-heading { font-size: 40px; }
  .char-card-info { margin: 0 auto; }
}

@media (max-width: 768px) {
  .up-nav { padding: 0 16px; top: 16px; }
  .nav-back { padding: 7px 14px; font-size: 12px; }
  .nav-logo { font-size: 18px; }

  .up-main { padding: 80px 16px 40px; gap: 30px; }
  .left-heading { font-size: 32px; }
  .left-sub { font-size: 14px; }
  .badge { font-size: 10px; padding: 5px 12px; }

  .char-wrap { width: 160px; }
  .char-card-info { padding: 14px 16px; }

  .up-card { padding: 24px; border-radius: 20px; }
  .section-title { font-size: 18px; }
  .section-sub { font-size: 13px; margin-bottom: 16px; }

  .tab-btn { font-size: 12px; padding: 9px 4px; }
  .tab-btn .tab-emoji { font-size: 16px; }
  .tab-btn .tab-sub { font-size: 8px; }

  .drop-zone { padding: 22px 16px; }
  .drop-emoji { font-size: 30px; }

  .submit-btn { padding: 14px; font-size: 14px; }

  .progress-section { padding: 18px; }
  .progress-label { font-size: 12px; }

  .step-row { font-size: 12px; }
  .step-dot { width: 22px; height: 22px; font-size: 11px; }
}

@media (max-width: 480px) {
  .left-heading { font-size: 26px; }
  .char-wrap { width: 140px; }
  .up-card { padding: 20px; }
}
      `}</style>

      <div className="up-shell">
        <div className="up-bg" />
        <div className="up-glow" />

        <nav className="up-nav">
          <button className="nav-back" onClick={() => navigate('/')}>← Back to home</button>
          <div className="nav-logo">TalkDox 🧠</div>
        </nav>

        <div className="up-main">

          {/* LEFT */}
          <div className="left-side">
            <div className="badge">
              <span className="badge-dot" />
              Powered by Gemini 2.5 Flash
            </div>
            <h1 className="left-heading">
              Choose your<br/>
              <em>reading</em> buddy.
            </h1>
            <p className="left-sub">
              Three sources, one AI. Upload a PDF, paste any website, or drop a YouTube link —
              your dedicated AI buddy will read it for you.
            </p>

            <div className="char-wrap">{currentChar}</div>
            <div className="char-card-info">
              <div className="char-name-row">{charName}<em>{charRole}</em></div>
              <div className="char-quote">"{charLine}"</div>
            </div>
          </div>

          {/* RIGHT */}
          <div className="right-side">
            <div className="up-card">

              <div className="tab-row">
                {tabs.map(tab => (
                  <button
                    key={tab.id}
                    className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                    onClick={() => { setActiveTab(tab.id); setError(''); setLoading(false); setLoadingStep(0) }}
                  >
                    <span className="tab-emoji">{tab.icon}</span>
                    <span>{tab.label}</span>
                    <span className="tab-sub">{tab.sub}</span>
                  </button>
                ))}
              </div>

              {activeTab === 'pdf' && !loading && (
                <div>
                  <div className="section-title">Upload PDF</div>
                  <div className="section-sub">Drop one or more PDFs and start chatting in seconds.</div>
                  <label
                    className={`drop-zone ${dragOver ? 'over' : ''}`}
                    onDragOver={e => { e.preventDefault(); setDragOver(true) }}
                    onDragLeave={() => setDragOver(false)}
                    onDrop={handleDrop}
                  >
                    <input type="file" accept=".pdf" multiple style={{ display: 'none' }} onChange={e => setFiles([...e.target.files])} />
                    <span className="drop-emoji">📄</span>
                    <div className="drop-main">Click to upload or drag & drop</div>
                    <div className="drop-hint">PDF files only</div>
                  </label>
                  {[...files].map(f => (
                    <div key={f.name} className="file-badge">✅ {f.name}</div>
                  ))}
                  <button className="submit-btn" onClick={handlePDF} disabled={!files.length}>
                    ⚡ Process & Index PDF
                  </button>
                </div>
              )}

              {activeTab === 'web' && !loading && (
                <div>
                  <div className="section-title">Paste Website URL</div>
                  <div className="section-sub">Any article, blog, documentation, or page on the web.</div>
                  <input
                    className="url-input"
                    value={url}
                    onChange={e => setUrl(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter' && url) handleWeb() }}
                    placeholder="https://example.com/article"
                  />
                  <button className="submit-btn" onClick={handleWeb} disabled={!url}>
                    🌐 Scrape & Index Page
                  </button>
                </div>
              )}

{activeTab === 'youtube' && !loading && (
  <div>
    <div className="section-title">Paste YouTube Link</div>
    <div className="section-sub">Lectures, tutorials, interviews — any video with captions.</div>
    <div style={{
      background:'#fffbea',
      border:'1px solid #fde68a',
      borderRadius:10,
      padding:'10px 14px',
      fontSize:12,
      color:'#92400e',
      lineHeight:1.55,
      marginBottom:14,
      display:'flex',
      alignItems:'flex-start',
      gap:8
    }}>
      <span style={{fontSize:14,flexShrink:0}}>💡</span>
      <span><strong>Tip:</strong> Some videos may not work due to region restrictions, age limits, or disabled captions. If you hit an error, try a different video.</span>
    </div>
                  <input
                    className="url-input"
                    value={ytUrl}
                    onChange={e => handleYtUrlChange(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter' && ytUrl) handleYT() }}
                    placeholder="https://www.youtube.com/watch?v=..."
                  />
                  {videoId && (
                    <div className="yt-preview">
                      <img src={`https://img.youtube.com/vi/${videoId}/hqdefault.jpg`} alt="thumbnail" />
                      <div className="yt-overlay"><div className="yt-play-btn">▶</div></div>
                    </div>
                  )}
                  <button className="submit-btn" onClick={handleYT} disabled={!ytUrl}>
                    ▶ Extract Transcript & Index
                  </button>
                </div>
              )}

              {loading && (
                <div className="progress-section">
                  <div className="progress-header">
                    <span className="progress-label">{activeSteps[loadingStep]?.label}...</span>
                    <span className="progress-pct">{progress}%</span>
                  </div>
                  <div className="progress-bar-track">
                    <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
                  </div>
                  <div className="steps-list">
                    {activeSteps.map((step, i) => {
                      const status = i < loadingStep ? 'done' : i === loadingStep ? 'active' : 'pending'
                      return (
                        <div key={i} className="step-row">
                          <div className={`step-dot ${status}`}>
                            {status === 'done' ? '✓' : step.icon}
                          </div>
                          <span className={`step-label ${status}`}>{step.label}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {error && <div className="error-box">❌ {error}</div>}

              <div className="powered-by">
                <span>Gemini 2.5 Flash</span>
                <span className="pb-dot" />
                <span>FAISS Vector Search</span>
                <span className="pb-dot" />
                <span>3 Agentic Layers</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </>
  )
}