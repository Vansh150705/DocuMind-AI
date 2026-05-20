import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL || ''

export default function Chat() {
  const navigate = useNavigate()
  const [state, setState] = useState(null)
  const [activeTab, setActiveTab] = useState('chat')
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState('qa')
  const [persona, setPersona] = useState('default')
  const [toolResult, setToolResult] = useState('')
  const [toolLoading, setToolLoading] = useState(false)
  const [selectedTool, setSelectedTool] = useState('')
  const [timeline, setTimeline] = useState([])
  const [tlLoading, setTlLoading] = useState(false)
  const [tlGenerated, setTlGenerated] = useState(false)
  const [flashcards, setFlashcards] = useState([])
  const [fcLoading, setFcLoading] = useState(false)
  const [fcCount, setFcCount] = useState(10)
  const [compareFile, setCompareFile] = useState(null)
  const [compareLoaded, setCompareLoaded] = useState(false)
  const [compareMessages, setCompareMessages] = useState([])
  const [compareInput, setCompareInput] = useState('')
  const [compareLoading, setCompareLoading] = useState(false)
  const [analytics, setAnalytics] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    axios.get(`${API}/api/state`).then(r => {
      if (!r.data.processed) { navigate('/upload'); return }
      setState(r.data)
      setMessages(r.data.chat_history || [])
    }).catch(() => navigate('/upload'))
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  useEffect(() => {
    if (activeTab === 'analytics') {
      axios.get(`${API}/api/analytics`).then(r => setAnalytics(r.data))
    }
  }, [activeTab])

  const sendMessage = async (q) => {
    const question = q || input.trim()
    if (!question) return
    setInput('')
    setMessages(prev => [...prev, {role:'user', content:question}])
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('question', question); fd.append('mode', mode); fd.append('persona', persona)
      const r = await axios.post(`${API}/api/chat`, fd)
      setMessages(prev => [...prev, {role:'assistant', content:r.data.answer, sources:r.data.sources, confidence:r.data.confidence}])
    } catch(e) {
      setMessages(prev => [...prev, {role:'assistant', content:'❌ Error: ' + (e.response?.data?.error || 'Something went wrong')}])
    } finally { setLoading(false) }
  }

  const runTool = async (tool) => {
    setSelectedTool(tool); setToolLoading(true); setToolResult('')
    try {
      const fd = new FormData(); fd.append('tool', tool)
      const r = await axios.post(`${API}/api/tools`, fd)
      setToolResult(r.data.result)
    } catch(e) { setToolResult('❌ Tool failed.') }
    finally { setToolLoading(false) }
  }

  const extractTimeline = async () => {
    setTlLoading(true)
    try { const r = await axios.post(`${API}/api/timeline`); setTimeline(r.data.timeline); setTlGenerated(true) }
    catch(e) {} finally { setTlLoading(false) }
  }

  const generateFlashcards = async () => {
    setFcLoading(true)
    try { const fd = new FormData(); fd.append('count', fcCount); const r = await axios.post(`${API}/api/flashcards`, fd); setFlashcards(r.data.flashcards) }
    catch(e) {} finally { setFcLoading(false) }
  }

  const uploadCompare = async () => {
    if (!compareFile) return
    const fd = new FormData(); fd.append('files', compareFile)
    await axios.post(`${API}/api/compare/upload`, fd)
    setCompareLoaded(true)
  }

  const sendCompare = async () => {
    const q = compareInput.trim(); if (!q) return
    setCompareInput('')
    setCompareMessages(prev => [...prev, {role:'user',content:q}])
    setCompareLoading(true)
    try {
      const fd = new FormData(); fd.append('question', q)
      const r = await axios.post(`${API}/api/compare/chat`, fd)
      setCompareMessages(prev => [...prev, {role:'assistant',content:r.data.answer,sources_a:r.data.sources_a,sources_b:r.data.sources_b}])
    } catch(e) {} finally { setCompareLoading(false) }
  }

  const reset = async () => {
    await axios.post(`${API}/api/reset`)
    navigate('/upload')
  }

  if (!state) return (
    <div style={{display:'flex',alignItems:'center',justifyContent:'center',height:'100vh',fontFamily:'DM Sans,sans-serif',color:'#5a5a5a',background:'#fff'}}>
      <div style={{display:'flex',gap:6,alignItems:'center'}}>
        <div className="ldot"/><div className="ldot"/><div className="ldot"/>
        <span style={{marginLeft:8}}>Loading your session...</span>
      </div>
      <style>{`.ldot{width:6px;height:6px;background:#0a0a0a;border-radius:50%;animation:lblink 1.2s ease-in-out infinite}.ldot:nth-child(2){animation-delay:0.2s}.ldot:nth-child(3){animation-delay:0.4s}@keyframes lblink{0%,80%,100%{opacity:0.3}40%{opacity:1}}`}</style>
    </div>
  )

  const tabs = ['chat','dna','tools','analytics','compare','timeline','flashcards']
  const tabIcons = {chat:'💬',dna:'🧬',tools:'🛠',analytics:'📊',compare:'🔀',timeline:'🕐',flashcards:'🃏'}
  const tabNames = {chat:'Chat',dna:'Document DNA',tools:'Smart Tools',analytics:'Analytics',compare:'Compare',timeline:'Timeline',flashcards:'Flashcards'}
  const availableTabs = state.source_type === 'pdf' ? tabs : ['chat','timeline','flashcards']

  const confColor = (c) => c > 60 ? '#16a34a' : c > 30 ? '#d97706' : '#dc2626'
  const confLabel = (c) => c > 60 ? 'High' : c > 30 ? 'Medium' : 'Low'

  const tlColors = {deadline:{bg:'#fef2f2',border:'#fca5a5',dot:'#dc2626',label:'⏰ Deadline'},milestone:{bg:'#f0fdf4',border:'#86efac',dot:'#16a34a',label:'🏁 Milestone'},event:{bg:'#eff6ff',border:'#93c5fd',dot:'#2563eb',label:'📌 Event'},period:{bg:'#fefce8',border:'#fde68a',dot:'#d97706',label:'📆 Period'},announcement:{bg:'#faf5ff',border:'#d8b4fe',dot:'#9333ea',label:'📢 Announcement'},other:{bg:'#f9fafb',border:'#e5e7eb',dot:'#6b7280',label:'📋 Other'}}
  const diffStyles = {easy:{bg:'#f0fdf4',border:'#86efac',color:'#16a34a',label:'🟢 Easy'},medium:{bg:'#fefce8',border:'#fde68a',color:'#d97706',label:'🟡 Medium'},hard:{bg:'#fef2f2',border:'#fca5a5',color:'#dc2626',label:'🔴 Hard'}}

  const sourceIcon = state.source_type==='pdf'?'📄':state.source_type==='web'?'🌐':'▶'
  const sourceLabel = state.source_type==='pdf'?'PDF Document':state.source_type==='web'?'Website':'YouTube Video'

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@400;500;600&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'DM Sans', sans-serif; background: #fff; overflow: hidden; }

        .chat-shell {
          display: grid;
          grid-template-columns: 280px 1fr;
          height: 100vh;
          background: #fff;
          position: relative;
        }
        .chat-bg {
          position: fixed; inset: 0;
          background-image: radial-gradient(circle, #e8e8e8 1px, transparent 1px);
          background-size: 28px 28px;
          opacity: 0.4;
          pointer-events: none;
          z-index: 0;
        }

        /* ── SIDEBAR ── */
        .sidebar {
          background: #fafafa;
          border-right: 1px solid #e2e2e2;
          display: flex;
          flex-direction: column;
          padding: 24px 16px;
          position: relative;
          z-index: 1;
          overflow-y: auto;
        }
        .sidebar-logo {
          font-family: 'Syne', sans-serif;
          font-weight: 800;
          font-size: 22px;
          color: #0a0a0a;
          padding: 0 8px;
          margin-bottom: 28px;
        }

        .source-card {
          background: #fff;
          border: 1px solid #e2e2e2;
          border-radius: 14px;
          padding: 14px;
          margin-bottom: 24px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }
        .source-label {
          font-size: 10px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.1em;
          color: #a0a0a0;
          margin-bottom: 8px;
        }
        .source-name {
          font-family: 'Syne', sans-serif;
          font-size: 14px;
          font-weight: 700;
          color: #0a0a0a;
          line-height: 1.4;
          word-break: break-word;
          margin-bottom: 4px;
        }
        .source-meta {
          font-size: 11px;
          color: #5a5a5a;
          line-height: 1.5;
          margin-bottom: 10px;
        }
        .source-pills {
          display: flex;
          gap: 6px;
          flex-wrap: wrap;
        }
        .src-pill {
          font-size: 10px;
          font-weight: 600;
          padding: 3px 9px;
          border-radius: 20px;
          background: #f0f0f0;
          color: #5a5a5a;
        }

        .nav-section-label {
          font-size: 10px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.12em;
          color: #c0c0c0;
          padding: 0 12px;
          margin-bottom: 8px;
        }
        .nav-list {
          display: flex; flex-direction: column;
          gap: 2px;
          flex: 1;
        }
        .nav-btn {
          width: 100%;
          text-align: left;
          padding: 10px 12px;
          border-radius: 10px;
          border: none;
          background: transparent;
          color: #5a5a5a;
          font-family: 'DM Sans', sans-serif;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.15s;
          display: flex;
          align-items: center;
          gap: 10px;
        }
        .nav-btn:hover { background: #f0f0f0; color: #0a0a0a; }
        .nav-btn.active {
          background: #0a0a0a;
          color: #fff;
        }
        .nav-btn-icon { font-size: 15px; width: 20px; text-align: center; }

        .sidebar-footer {
          border-top: 1px solid #e2e2e2;
          padding-top: 16px;
          margin-top: 16px;
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        .footer-btn {
          background: #fff;
          border: 1px solid #e2e2e2;
          border-radius: 10px;
          padding: 10px 12px;
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          color: #5a5a5a;
          text-align: left;
          font-family: 'DM Sans', sans-serif;
          transition: all 0.15s;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .footer-btn:hover { border-color: #0a0a0a; color: #0a0a0a; }
        .footer-btn.danger { color: #dc2626; border-color: #fca5a5; background: #fef2f2; }
        .footer-btn.danger:hover { background: #fee2e2; border-color: #dc2626; }

        .sb-credits {
          font-size: 10px;
          color: #c0c0c0;
          text-align: center;
          margin-top: 10px;
          padding-top: 10px;
          border-top: 1px solid #f0f0f0;
        }

        /* ── MAIN ── */
        .main-area {
          display: flex;
          flex-direction: column;
          overflow: hidden;
          position: relative;
          z-index: 1;
        }

        .top-bar {
          background: rgba(255,255,255,0.85);
          backdrop-filter: blur(12px);
          border-bottom: 1px solid #e2e2e2;
          padding: 16px 28px;
          display: flex;
          align-items: center;
          gap: 16px;
          z-index: 10;
        }
        .top-title {
          font-family: 'Syne', sans-serif;
          font-size: 22px;
          font-weight: 800;
          color: #0a0a0a;
          letter-spacing: -0.02em;
          flex: 1;
        }
        .top-title em { font-style: italic; font-weight: 400; color: #a0a0a0; margin-left: 6px; font-size: 14px; }

        .top-select {
          border: 1px solid #e2e2e2;
          border-radius: 100px;
          padding: 7px 14px;
          font-size: 13px;
          font-family: 'DM Sans', sans-serif;
          background: #fff;
          cursor: pointer;
          color: #0a0a0a;
          font-weight: 500;
          transition: border-color 0.2s;
        }
        .top-select:hover, .top-select:focus { border-color: #0a0a0a; outline: none; }

        .content-area {
          flex: 1;
          overflow: auto;
          padding: 24px 28px;
        }
        .content-inner {
          max-width: 920px;
          margin: 0 auto;
        }

        /* ── CHAT MESSAGES ── */
        .messages-list {
          display: flex;
          flex-direction: column;
          gap: 18px;
          padding-bottom: 20px;
        }
        .msg-wrap { display: flex; }
        .msg-wrap.user { justify-content: flex-end; }
        .msg-bubble {
          max-width: 75%;
          padding: 13px 18px;
          font-size: 14.5px;
          line-height: 1.65;
          white-space: pre-wrap;
          animation: msgIn 0.3s ease;
        }
        @keyframes msgIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
        .msg-bubble.user {
          background: #0a0a0a;
          color: #fff;
          border-radius: 20px 20px 4px 20px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .msg-bubble.assistant {
          background: #fff;
          color: #0a0a0a;
          border: 1px solid #e2e2e2;
          border-radius: 20px 20px 20px 4px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }

        .msg-meta {
          margin-top: 8px;
          max-width: 75%;
          font-size: 12px;
          color: #a0a0a0;
        }
        .conf-row {
          display: flex; align-items: center;
          gap: 10px;
        }
        .conf-text { font-size: 11px; color: #a0a0a0; white-space: nowrap; }
        .conf-bar {
          flex: 1;
          height: 4px;
          background: #f0f0f0;
          border-radius: 2px;
          overflow: hidden;
          max-width: 120px;
        }
        .conf-fill { height: 100%; border-radius: 2px; transition: width 0.7s; }

        .source-chips {
          display: flex; gap: 5px; flex-wrap: wrap;
          margin-top: 8px;
        }
        .src-chip {
          background: #f8f8f8;
          border: 1px solid #e2e2e2;
          border-radius: 100px;
          padding: 3px 10px;
          font-size: 11px;
          color: #5a5a5a;
        }

        /* Suggestions */
        .suggestions-wrap {
          padding: 40px 0;
          text-align: center;
        }
        .empty-emoji { font-size: 48px; margin-bottom: 16px; }
        .empty-title {
          font-family: 'Syne', sans-serif;
          font-size: 24px;
          font-weight: 700;
          color: #0a0a0a;
          margin-bottom: 8px;
        }
        .empty-sub { font-size: 14px; color: #a0a0a0; margin-bottom: 28px; }
        .sug-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 10px;
          max-width: 600px;
          margin: 0 auto;
        }
        .sug-card {
          background: #fff;
          border: 1.5px solid #e2e2e2;
          border-radius: 14px;
          padding: 14px 18px;
          font-size: 13.5px;
          text-align: left;
          cursor: pointer;
          color: #374151;
          font-family: 'DM Sans', sans-serif;
          font-weight: 500;
          transition: all 0.2s;
          line-height: 1.5;
        }
        .sug-card:hover {
          border-color: #0a0a0a;
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        }

        /* Typing indicator */
        .typing-indicator {
          padding: 14px 18px;
          border-radius: 20px 20px 20px 4px;
          background: #fff;
          border: 1px solid #e2e2e2;
          display: inline-flex;
          gap: 5px;
          align-items: center;
          width: fit-content;
        }
        .typing-indicator span {
          width: 7px; height: 7px;
          background: #c0c0c0;
          border-radius: 50%;
          display: block;
          animation: tdot 1.3s ease-in-out infinite;
        }
        .typing-indicator span:nth-child(2) { animation-delay: 0.15s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.3s; }
        .typing-indicator .typing-text { font-size: 12px; color: #a0a0a0; margin-left: 4px; }
        @keyframes tdot { 0%,80%,100%{opacity:0.3;transform:scale(0.8)} 40%{opacity:1;transform:scale(1.1)} }

        /* Input */
        .input-wrap {
          padding: 16px 28px 24px;
          background: linear-gradient(to top, #fff 80%, transparent);
        }
        .input-inner {
          max-width: 920px;
          margin: 0 auto;
          background: #fff;
          border: 1.5px solid #e2e2e2;
          border-radius: 18px;
          padding: 4px 4px 4px 18px;
          display: flex;
          align-items: center;
          gap: 8px;
          box-shadow: 0 4px 20px rgba(0,0,0,0.06);
          transition: border-color 0.2s, box-shadow 0.2s;
        }
        .input-inner:focus-within {
          border-color: #0a0a0a;
          box-shadow: 0 0 0 3px rgba(10,10,10,0.05), 0 4px 20px rgba(0,0,0,0.06);
        }
        .input-field {
          flex: 1;
          border: none;
          outline: none;
          font-size: 15px;
          font-family: 'DM Sans', sans-serif;
          color: #0a0a0a;
          background: transparent;
          padding: 14px 0;
        }
        .input-field::placeholder { color: #c0c0c0; }
        .send-btn {
          background: #0a0a0a;
          color: #fff;
          border: none;
          border-radius: 14px;
          width: 42px; height: 42px;
          display: flex; align-items: center; justify-content: center;
          font-size: 18px;
          cursor: pointer;
          transition: all 0.2s;
          flex-shrink: 0;
        }
        .send-btn:hover:not(:disabled) { background: #222; transform: scale(1.05); }
        .send-btn:disabled { opacity: 0.3; cursor: not-allowed; }

        /* ── DNA TAB ── */
        .dna-grid { display: flex; flex-direction: column; gap: 14px; }
        .dna-card {
          background: #fff;
          border: 1px solid #e2e2e2;
          border-radius: 18px;
          padding: 24px;
          transition: all 0.25s;
        }
        .dna-card:hover { box-shadow: 0 6px 24px rgba(0,0,0,0.06); }
        .dna-title { font-family: 'Syne',sans-serif; font-size: 22px; font-weight: 700; margin-bottom: 8px; color: #0a0a0a; }
        .dna-summary { font-size: 15px; color: #5a5a5a; line-height: 1.7; }
        .dna-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
        .dna-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #a0a0a0; margin-bottom: 4px; }
        .dna-value { font-size: 16px; font-weight: 600; color: #0a0a0a; margin-bottom: 14px; }
        .dna-bar-label { font-size: 12px; color: #5a5a5a; margin-bottom: 4px; font-weight: 500; display: flex; justify-content: space-between; }
        .dna-bar-track { height: 8px; background: #f0f0f0; border-radius: 4px; overflow: hidden; margin-bottom: 14px; }
        .dna-bar-fill { height: 100%; border-radius: 4px; transition: width 0.8s; }
        .dna-tag {
          display: inline-block;
          background: #f8f8f8;
          border: 1px solid #e2e2e2;
          border-radius: 100px;
          padding: 5px 14px;
          font-size: 13px;
          color: #374151;
          margin: 4px;
          font-weight: 500;
          transition: all 0.2s;
        }
        .dna-tag:hover { background: #0a0a0a; color: #fff; border-color: #0a0a0a; }

        /* ── TOOLS ── */
        .tools-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
          gap: 12px;
          margin-bottom: 24px;
        }
        .tool-card {
          background: #fff;
          border: 1.5px solid #e2e2e2;
          border-radius: 16px;
          padding: 24px 16px;
          text-align: center;
          cursor: pointer;
          transition: all 0.25s;
          font-family: 'DM Sans', sans-serif;
        }
        .tool-card:hover:not(:disabled) {
          border-color: #0a0a0a;
          transform: translateY(-3px);
          box-shadow: 0 10px 30px rgba(0,0,0,0.08);
          background: #0a0a0a;
          color: #fff;
        }
        .tool-card:disabled { opacity: 0.5; cursor: not-allowed; }
        .tool-card.active {
          background: #0a0a0a;
          color: #fff;
          border-color: #0a0a0a;
        }
        .tool-icon { font-size: 30px; margin-bottom: 10px; display: block; }
        .tool-label { font-size: 13px; font-weight: 600; }
        .tool-result {
          background: #fff;
          border: 1px solid #e2e2e2;
          border-radius: 18px;
          padding: 24px;
          font-size: 14px;
          line-height: 1.85;
          color: #374151;
          white-space: pre-wrap;
          animation: fadeUp 0.3s;
        }
        @keyframes fadeUp { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }

        /* ── ANALYTICS ── */
        .stats-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 14px; margin-bottom: 16px; }
        .stat-card {
          background: #fff;
          border: 1px solid #e2e2e2;
          border-radius: 18px;
          padding: 28px 20px;
          text-align: center;
          transition: all 0.25s;
        }
        .stat-card:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(0,0,0,0.08); }
        .stat-num { font-family: 'Syne',sans-serif; font-size: 44px; font-weight: 800; line-height: 1; color: #0a0a0a; letter-spacing: -0.03em; }
        .stat-label { font-size: 11px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 0.12em; margin-top: 10px; font-weight: 600; }

        /* ── TIMELINE ── */
        .timeline-wrap {
          position: relative;
          padding-left: 30px;
          margin-top: 10px;
        }
        .timeline-line {
          position: absolute;
          left: 7px; top: 8px; bottom: 8px;
          width: 2px;
          background: #e2e2e2;
          border-radius: 2px;
        }
        .tl-item { position: relative; margin-bottom: 14px; }
        .tl-dot {
          position: absolute;
          left: -27px; top: 14px;
          width: 14px; height: 14px;
          border-radius: 50%;
          border: 2px solid #fff;
        }
        .tl-card { border-radius: 14px; padding: 14px 18px; }

        /* ── FLASHCARDS ── */
        .fc-card {
          border-radius: 16px;
          padding: 18px 22px;
          margin-bottom: 6px;
          border-width: 1.5px;
          border-style: solid;
        }
        .fc-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 10px;
        }
        .fc-diff { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
        .fc-topic { font-size: 11px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 0.07em; font-weight: 500; }
        .fc-question { font-size: 15px; font-weight: 600; color: #0a0a0a; line-height: 1.55; }
        .fc-answer-wrap {
          background: #fff;
          border: 1px solid #e2e2e2;
          border-radius: 14px;
          overflow: hidden;
          margin-bottom: 14px;
        }
        .fc-answer-wrap summary {
          padding: 12px 18px;
          cursor: pointer;
          font-size: 13px;
          font-weight: 500;
          color: #5a5a5a;
          list-style: none;
        }
        .fc-answer-wrap summary::-webkit-details-marker { display: none; }
        .fc-answer-wrap summary:hover { color: #0a0a0a; }
        .fc-answer-body {
          background: #0a0a0a;
          padding: 18px 22px;
        }
        .fc-answer-body .fa-label { font-size:10px; font-weight: 700; color:#5a5a5a; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px; }
        .fc-answer-body .fa-text { font-size: 14px; color: #f3f4f6; line-height: 1.7; }

        /* ── COMPARE ── */
        .cmp-tags {
          display: flex; gap: 10px; align-items: center;
          margin-bottom: 18px;
        }
        .cmp-tag {
          background: #f0fdf4;
          border: 1px solid #bbf7d0;
          border-radius: 100px;
          padding: 6px 14px;
          font-size: 13px;
          color: #15803d;
          font-weight: 500;
        }
        .cmp-tag.b { background:#eff6ff; border-color:#bfdbfe; color: #1d4ed8; }
        .cmp-vs { color: #a0a0a0; font-size: 13px; font-weight: 600; }

        /* Empty state */
        .empty-state {
          text-align: center;
          padding: 60px 20px;
        }
        .empty-state .es-icon { font-size: 56px; margin-bottom: 16px; }
        .empty-state .es-title { font-family:'Syne',sans-serif; font-size: 26px; font-weight: 700; color: #0a0a0a; margin-bottom: 10px; }
        .empty-state .es-sub { font-size: 15px; color: #a0a0a0; line-height: 1.6; max-width: 360px; margin: 0 auto 28px; }
        .es-btn {
          background: #0a0a0a;
          color: #fff;
          border: none;
          border-radius: 100px;
          padding: 14px 30px;
          font-size: 14px;
          font-weight: 600;
          font-family: 'DM Sans', sans-serif;
          cursor: pointer;
          transition: all 0.2s;
        }
        .es-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.15); }

        @media (max-width: 880px) {
          .chat-shell { grid-template-columns: 1fr; }
          .sidebar { display: none; }
        }
      `}</style>

      <div className="chat-shell">
        <div className="chat-bg" />

        {/* SIDEBAR */}
        <aside className="sidebar">
          <div className="sidebar-logo">TalkDox 🧠</div>

          <div className="source-card">
            <div className="source-label">Currently chatting with</div>
            <div className="source-name">{sourceIcon} {(state.pdf_names[0]||'').slice(0,40)}</div>
            <div className="source-meta">{sourceLabel}</div>
            <div className="source-pills">
              <span className="src-pill">{state.total_chunks} chunks</span>
              {state.source_type==='pdf' && <span className="src-pill">{state.total_pages} pages</span>}
              {state.doc_language && state.doc_language!=='English' && <span className="src-pill">🌐 {state.doc_language}</span>}
            </div>
          </div>

          <div className="nav-section-label">Workspace</div>
          <nav className="nav-list">
            {availableTabs.map(tab => (
              <button key={tab} onClick={() => setActiveTab(tab)} className={`nav-btn ${activeTab===tab?'active':''}`}>
                <span className="nav-btn-icon">{tabIcons[tab]}</span>
                {tabNames[tab]}
              </button>
            ))}
          </nav>

          <div className="sidebar-footer">
            <button className="footer-btn" onClick={() => navigate('/upload')}>↑ New Source</button>
            <button className="footer-btn danger" onClick={reset}>↺ Reset All</button>
          </div>
          <div className="sb-credits">
            Powered by Gemini 2.5 Flash<br/>
            Built by Vansh Mahajan
          </div>
        </aside>

        {/* MAIN */}
        <main className="main-area">
          <div className="top-bar">
            <h1 className="top-title">
              {tabIcons[activeTab]} {tabNames[activeTab]}
              {activeTab==='chat' && <em>{messages.length} messages</em>}
            </h1>
            {activeTab==='chat' && (
              <>
                <select className="top-select" value={mode} onChange={e=>setMode(e.target.value)}>
                  <option value="qa">🎯 Standard</option>
                  <option value="eli5">🧒 ELI5</option>
                  <option value="executive">💼 Executive</option>
                  <option value="debate">⚖️ Devil's Advocate</option>
                </select>
                <select className="top-select" value={persona} onChange={e=>setPersona(e.target.value)}>
                  <option value="default">🤖 Default</option>
                  <option value="lawyer">⚖️ Lawyer</option>
                  <option value="doctor">🩺 Doctor</option>
                  <option value="financial">📈 Financial</option>
                  <option value="teacher">📚 Teacher</option>
                  <option value="journalist">📰 Journalist</option>
                </select>
              </>
            )}
          </div>

          <div className="content-area">
            <div className="content-inner">

              {/* CHAT */}
              {activeTab==='chat' && (
                <div className="messages-list">
                  {messages.length===0 && (
                    <div className="suggestions-wrap">
                      <div className="empty-emoji">💬</div>
                      <div className="empty-title">Start the conversation</div>
                      <div className="empty-sub">Ask anything about your content — I'll find the answers grounded in the source.</div>
                      <div className="sug-grid">
                        {['What is the main topic?','Summarize the key points','What conclusions are drawn?','List the most important findings'].map(s=>(
                          <button key={s} className="sug-card" onClick={()=>sendMessage(s)}>{s}</button>
                        ))}
                      </div>
                    </div>
                  )}
                  {messages.map((msg,i) => (
                    <div key={i}>
                      <div className={`msg-wrap ${msg.role}`}>
                        <div className={`msg-bubble ${msg.role}`}>{msg.content}</div>
                      </div>
                      {msg.role==='assistant' && msg.confidence != null && (
                        <div className="msg-meta">
                          <div className="conf-row">
                            <span className="conf-text">Confidence <strong style={{color:confColor(msg.confidence)}}>{msg.confidence}% · {confLabel(msg.confidence)}</strong></span>
                            <div className="conf-bar">
                              <div className="conf-fill" style={{width:`${msg.confidence}%`,background:confColor(msg.confidence)}}/>
                            </div>
                          </div>
                          {msg.sources?.length > 0 && (
                            <div className="source-chips">
                              {msg.sources.map(s=><span key={s} className="src-chip">📄 {s}</span>)}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                  {loading && (
                    <div className="msg-wrap">
                      <div className="typing-indicator"><span/><span/><span/><span className="typing-text">Thinking...</span></div>
                    </div>
                  )}
                  <div ref={messagesEndRef}/>
                </div>
              )}

              {/* DNA */}
              {activeTab==='dna' && (
                <div>
                  {!state.dna ? (
                    <div className="empty-state">
                      <div className="es-icon">🧬</div>
                      <div className="es-title">DNA not available</div>
                      <div className="es-sub">Document DNA only generates for PDFs. Upload a PDF to see fingerprint analysis.</div>
                    </div>
                  ) : (
                    <div className="dna-grid">
                      <div className="dna-card">
                        <div className="dna-title">{state.dna.title || 'Document'}</div>
                        <p className="dna-summary">{state.dna.one_line_summary}</p>
                      </div>
                      <div className="dna-grid-2">
                        <div className="dna-card">
                          {[['Domain',state.dna.domain],['Tone',state.dna.tone],['Language',`🌐 ${state.dna.language}`]].map(([k,v])=>(
                            <div key={k}>
                              <div className="dna-label">{k}</div>
                              <div className="dna-value">{v}</div>
                            </div>
                          ))}
                        </div>
                        <div className="dna-card">
                          {[['Complexity',state.dna.complexity,'#0a0a0a'],['Sentiment',state.dna.sentiment,'#22c55e'],['Informativeness',state.dna.informativeness,'#6366f1']].map(([label,val,color])=>(
                            <div key={label}>
                              <div className="dna-bar-label"><span>{label}</span><strong>{val}%</strong></div>
                              <div className="dna-bar-track"><div className="dna-bar-fill" style={{width:`${val}%`,background:color}}/></div>
                            </div>
                          ))}
                        </div>
                      </div>
                      {state.dna.key_themes?.length > 0 && (
                        <div className="dna-card">
                          <div className="dna-label" style={{marginBottom:14}}>Key Themes</div>
                          <div>{state.dna.key_themes.map(t=><span key={t} className="dna-tag">#{t}</span>)}</div>
                        </div>
                      )}
                      {state.dna.key_entities?.length > 0 && (
                        <div className="dna-card">
                          <div className="dna-label" style={{marginBottom:14}}>Key Entities</div>
                          <div>{state.dna.key_entities.map(t=><span key={t} className="dna-tag">🏷 {t}</span>)}</div>
                        </div>
                      )}
                      {state.dna.unusual_insight && (
                        <div className="dna-card" style={{background:'#fafafa'}}>
                          <div className="dna-label" style={{marginBottom:10}}>💡 Unusual Insight</div>
                          <p style={{fontSize:15,color:'#374151',lineHeight:1.7,fontStyle:'italic'}}>{state.dna.unusual_insight}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* TOOLS */}
              {activeTab==='tools' && (
                <div>
                  <div className="tools-grid">
                    {[{id:'summary',icon:'📝',label:'Auto Summary'},{id:'quiz',icon:'❓',label:'Generate Quiz'},{id:'email',icon:'📧',label:'Draft Email'},{id:'contradictions',icon:'🔍',label:'Find Contradictions'},{id:'actions',icon:'📊',label:'Action Items'}].map(tool=>(
                      <button key={tool.id} onClick={()=>runTool(tool.id)} disabled={toolLoading} className={`tool-card ${selectedTool===tool.id && toolResult?'active':''}`}>
                        <span className="tool-icon">{tool.icon}</span>
                        <span className="tool-label">{tool.label}</span>
                      </button>
                    ))}
                  </div>
                  {toolLoading && (
                    <div style={{textAlign:'center',padding:30}}>
                      <div className="typing-indicator" style={{display:'inline-flex'}}>
                        <span/><span/><span/><span className="typing-text">Running tool...</span>
                      </div>
                    </div>
                  )}
                  {toolResult && <div className="tool-result">{toolResult}</div>}
                </div>
              )}

              {/* ANALYTICS */}
              {activeTab==='analytics' && analytics && (
                <div>
                  {analytics.total_q === 0 ? (
                    <div className="empty-state">
                      <div className="es-icon">📊</div>
                      <div className="es-title">No data yet</div>
                      <div className="es-sub">Start asking questions in the Chat tab to see your analytics here.</div>
                    </div>
                  ) : (
                    <>
                      <div className="stats-grid">
                        {[['Questions Asked',analytics.total_q],['Avg Confidence',`${analytics.avg_conf}%`],['High Confidence',analytics.high_conf]].map(([label,val])=>(
                          <div key={label} className="stat-card">
                            <div className="stat-num">{val}</div>
                            <div className="stat-label">{label}</div>
                          </div>
                        ))}
                      </div>
                      {analytics.confs?.length > 0 && (
                        <div className="dna-card">
                          <div className="dna-label" style={{marginBottom:16}}>Confidence Per Answer</div>
                          {analytics.confs.map((c,i)=>(
                            <div key={i} style={{marginBottom:14}}>
                              <div className="dna-bar-label"><span>Answer {i+1}</span><strong style={{color:confColor(c)}}>{confLabel(c)} · {c}%</strong></div>
                              <div className="dna-bar-track"><div className="dna-bar-fill" style={{width:`${c}%`,background:confColor(c)}}/></div>
                            </div>
                          ))}
                        </div>
                      )}
                    </>
                  )}
                </div>
              )}

              {/* COMPARE */}
              {activeTab==='compare' && (
                <div>
                  {!compareLoaded ? (
                    <div className="empty-state">
                      <div className="es-icon">🔀</div>
                      <div className="es-title">Compare two documents</div>
                      <div className="es-sub">Upload a second PDF to compare it side by side with your primary document.</div>
                      <label style={{display:'inline-block',border:'2px dashed #e2e2e2',borderRadius:16,padding:'24px 40px',cursor:'pointer',background:'#fafafa',marginBottom:16,minWidth:300}}>
                        <input type="file" accept=".pdf" style={{display:'none'}} onChange={e=>setCompareFile(e.target.files[0])}/>
                        <div style={{fontSize:14,color:'#5a5a5a'}}>{compareFile ? `✅ ${compareFile.name}` : '📄 Click to upload second PDF'}</div>
                      </label>
                      <br/>
                      <button className="es-btn" onClick={uploadCompare} disabled={!compareFile}>⚡ Index Second Document</button>
                    </div>
                  ) : (
                    <div>
                      <div className="cmp-tags">
                        <span className="cmp-tag">📄 A: {state.pdf_names[0]?.slice(0,30)}</span>
                        <span className="cmp-vs">vs</span>
                        <span className="cmp-tag b">📄 B: {compareFile?.name?.slice(0,30)}</span>
                      </div>
                      <div className="messages-list">
                        {compareMessages.length===0 && (
                          <div className="sug-grid" style={{marginTop:20}}>
                            {['What are the key differences?','What do both agree on?','Which is more comprehensive?','What is in A but missing in B?'].map(q=>(
                              <button key={q} className="sug-card" onClick={()=>{setCompareInput(q);setTimeout(sendCompare,100)}}>{q}</button>
                            ))}
                          </div>
                        )}
                        {compareMessages.map((msg,i)=>(
                          <div key={i}>
                            <div className={`msg-wrap ${msg.role}`}>
                              <div className={`msg-bubble ${msg.role}`}>{msg.content}</div>
                            </div>
                            {msg.role==='assistant' && (msg.sources_a?.length>0||msg.sources_b?.length>0) && (
                              <div className="msg-meta">
                                <div className="source-chips">
                                  {msg.sources_a?.map(s=><span key={s} className="src-chip" style={{background:'#f0fdf4',borderColor:'#bbf7d0',color:'#15803d'}}>A: {s}</span>)}
                                  {msg.sources_b?.map(s=><span key={s} className="src-chip" style={{background:'#eff6ff',borderColor:'#bfdbfe',color:'#1d4ed8'}}>B: {s}</span>)}
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                        {compareLoading && <div className="msg-wrap"><div className="typing-indicator"><span/><span/><span/><span className="typing-text">Comparing...</span></div></div>}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* TIMELINE */}
              {activeTab==='timeline' && (
                <div>
                  {!tlGenerated ? (
                    <div className="empty-state">
                      <div className="es-icon">🕐</div>
                      <div className="es-title">Extract timeline events</div>
                      <div className="es-sub">Pull out every date, deadline, milestone, and event from your content into a visual timeline.</div>
                      <button className="es-btn" onClick={extractTimeline} disabled={tlLoading}>
                        {tlLoading ? 'Extracting...' : '🕐 Extract Timeline'}
                      </button>
                    </div>
                  ) : (
                    <div>
                      <button onClick={()=>{setTlGenerated(false);setTimeline([])}} style={{background:'#f8f8f8',border:'1px solid #e2e2e2',borderRadius:100,padding:'8px 18px',fontSize:13,cursor:'pointer',marginBottom:20,fontFamily:'DM Sans,sans-serif'}}>↺ Re-extract</button>
                      {timeline.length===0 ? <p style={{color:'#a0a0a0',textAlign:'center',padding:30}}>No dates found in this content.</p> : (
                        <div className="timeline-wrap">
                          <div className="timeline-line"/>
                          {timeline.map((event,i)=>{
                            const tc = tlColors[event.type]||tlColors.other
                            return (
                              <div key={i} className="tl-item">
                                <div className="tl-dot" style={{background:tc.dot,boxShadow:`0 0 0 3px ${tc.dot}33`}}/>
                                <div className="tl-card" style={{background:tc.bg,border:`1px solid ${tc.border}`}}>
                                  <div style={{display:'flex',justifyContent:'space-between',marginBottom:6}}>
                                    <span style={{fontSize:11,fontWeight:700,textTransform:'uppercase',letterSpacing:'0.08em',color:tc.dot}}>{tc.label}</span>
                                    <span style={{fontSize:11,color:'#a0a0a0',fontWeight:500}}>{event.importance==='high'?'⬆ High':event.importance==='medium'?'— Medium':'↓ Low'}</span>
                                  </div>
                                  <div style={{fontSize:13,fontWeight:700,color:'#0a0a0a',marginBottom:6}}>📅 {event.date}</div>
                                  <div style={{fontSize:14,color:'#374151',lineHeight:1.55}}>{event.event}</div>
                                </div>
                              </div>
                            )
                          })}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* FLASHCARDS */}
              {activeTab==='flashcards' && (
                <div>
                  {flashcards.length === 0 ? (
                    <div className="empty-state">
                      <div className="es-icon">🃏</div>
                      <div className="es-title">Generate study flashcards</div>
                      <div className="es-sub">Auto-generate Q&A flashcards from your content with varying difficulty levels.</div>
                      <div style={{display:'flex',gap:10,justifyContent:'center',alignItems:'center'}}>
                        <select value={fcCount} onChange={e=>setFcCount(Number(e.target.value))} className="top-select">
                          {[5,8,10,15,20].map(n=><option key={n} value={n}>{n} flashcards</option>)}
                        </select>
                        <button className="es-btn" onClick={generateFlashcards} disabled={fcLoading}>
                          {fcLoading ? 'Generating...' : '🃏 Generate'}
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div style={{display:'flex',gap:10,marginBottom:20,alignItems:'center'}}>
                        <select value={fcCount} onChange={e=>setFcCount(Number(e.target.value))} className="top-select">
                          {[5,8,10,15,20].map(n=><option key={n} value={n}>{n} flashcards</option>)}
                        </select>
                        <button onClick={generateFlashcards} disabled={fcLoading} className="es-btn" style={{padding:'10px 22px',fontSize:13}}>
                          {fcLoading ? 'Generating...' : '🃏 Regenerate'}
                        </button>
                        <button onClick={()=>setFlashcards([])} style={{background:'#f8f8f8',border:'1px solid #e2e2e2',borderRadius:100,padding:'10px 18px',fontSize:13,cursor:'pointer',fontFamily:'DM Sans,sans-serif'}}>↺ Clear</button>
                      </div>
                      {flashcards.map((card,i)=>{
                        const ds = diffStyles[card.difficulty]||diffStyles.medium
                        return (
                          <div key={i}>
                            <div className="fc-card" style={{background:ds.bg,borderColor:ds.border}}>
                              <div className="fc-header">
                                <span className="fc-diff" style={{color:ds.color}}>{ds.label}</span>
                                <span className="fc-topic">{card.topic}</span>
                              </div>
                              <div className="fc-question">{card.question}</div>
                            </div>
                            <details className="fc-answer-wrap">
                              <summary>👁 Reveal Answer</summary>
                              <div className="fc-answer-body">
                                <div className="fa-label">Answer</div>
                                <div className="fa-text">{card.answer}</div>
                              </div>
                            </details>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>
              )}

            </div>
          </div>

          {/* CHAT INPUT */}
          {activeTab === 'chat' && (
            <div className="input-wrap">
              <div className="input-inner">
                <input className="input-field" value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMessage()}}} placeholder="Ask anything about your content..." disabled={loading}/>
                <button className="send-btn" onClick={()=>sendMessage()} disabled={!input.trim()||loading}>→</button>
              </div>
            </div>
          )}

          {activeTab === 'compare' && compareLoaded && (
            <div className="input-wrap">
              <div className="input-inner">
                <input className="input-field" value={compareInput} onChange={e=>setCompareInput(e.target.value)} onKeyDown={e=>{if(e.key==='Enter')sendCompare()}} placeholder="Ask anything about both documents..."/>
                <button className="send-btn" onClick={sendCompare}>→</button>
              </div>
            </div>
          )}

        </main>
      </div>
    </>
  )
}