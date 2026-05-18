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
    { icon: '📖', label: 'Reading your PDF...' },
    { icon: '✂️', label: 'Splitting into chunks...' },
    { icon: '🔢', label: 'Generating embeddings...' },
    { icon: '🗃️', label: 'Building vector index...' },
    { icon: '🧬', label: 'Analysing Document DNA...' },
    { icon: '✅', label: 'All done!' },
  ]

  const webSteps = [
    { icon: '🌐', label: 'Fetching the page...' },
    { icon: '🧹', label: 'Cleaning content...' },
    { icon: '🔢', label: 'Generating embeddings...' },
    { icon: '🗃️', label: 'Building vector index...' },
    { icon: '✅', label: 'All done!' },
  ]

  const ytSteps = [
    { icon: '▶', label: 'Fetching transcript...' },
    { icon: '✂️', label: 'Splitting into chunks...' },
    { icon: '🔢', label: 'Generating embeddings...' },
    { icon: '🗃️', label: 'Building vector index...' },
    { icon: '✅', label: 'All done!' },
  ]

  const simulateSteps = async (steps, apiCall) => {
    setLoading(true)
    setError('')
    setLoadingStep(0)

    // Simulate steps with timing
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
      setLoading(false)
      setLoadingStep(0)
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
    const fd = new FormData()
    fd.append('url', url)
    simulateSteps(webSteps, () => axios.post(`${API}/api/upload/web`, fd))
  }

  const handleYT = () => {
    if (!ytUrl) return
    const fd = new FormData()
    fd.append('url', ytUrl)
    simulateSteps(ytSteps, () => axios.post(`${API}/api/upload/youtube`, fd))
  }

  const activeSteps = activeTab === 'pdf' ? pdfSteps : activeTab === 'web' ? webSteps : ytSteps
  const progress = loading ? Math.round((loadingStep / (activeSteps.length - 1)) * 100) : 0

  const tabs = [
    { id: 'pdf', icon: '📄', label: 'Paige', sub: 'PDF' },
    { id: 'web', icon: '🌐', label: 'Webb', sub: 'Website' },
    { id: 'youtube', icon: '▶', label: 'Yuki', sub: 'YouTube' },
  ]

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'DM Sans', sans-serif; background: #f8f8f8; }

        .up-page {
          min-height: 100vh;
          background: #f8f8f8;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 40px 20px;
          position: relative;
        }

        .dot-bg {
          position: fixed;
          inset: 0;
          background-image: radial-gradient(circle, #d0d0d0 1px, transparent 1px);
          background-size: 28px 28px;
          opacity: 0.5;
          pointer-events: none;
        }

        .back-btn {
          position: fixed;
          top: 24px; left: 24px;
          background: #fff;
          border: 1px solid #e2e2e2;
          border-radius: 100px;
          padding: 8px 18px;
          font-size: 13px;
          font-weight: 500;
          color: #5a5a5a;
          cursor: pointer;
          font-family: 'DM Sans', sans-serif;
          transition: all 0.2s;
          z-index: 100;
          box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }
        .back-btn:hover { border-color: #0a0a0a; color: #0a0a0a; }

        .up-logo {
          font-family: 'Syne', sans-serif;
          font-weight: 800;
          font-size: 26px;
          color: #0a0a0a;
          margin-bottom: 6px;
          position: relative;
          z-index: 1;
        }
        .up-tagline {
          font-size: 15px;
          color: #a0a0a0;
          margin-bottom: 36px;
          position: relative;
          z-index: 1;
        }

        .up-card {
          background: #ffffff;
          border: 1px solid #e2e2e2;
          border-radius: 24px;
          padding: 36px;
          width: 100%;
          max-width: 500px;
          box-shadow: 0 8px 40px rgba(0,0,0,0.08);
          position: relative;
          z-index: 1;
        }

        .tab-row {
          display: grid;
          grid-template-columns: 1fr 1fr 1fr;
          gap: 6px;
          background: #f0f0f0;
          border-radius: 14px;
          padding: 4px;
          margin-bottom: 32px;
        }
        .tab-btn {
          border: none;
          border-radius: 10px;
          padding: 10px 6px;
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
        .tab-btn span { font-size: 20px; }

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
          margin-top: 4px;
        }
        .submit-btn:hover:not(:disabled) { background: #222; transform: translateY(-1px); box-shadow: 0 8px 24px rgba(0,0,0,0.15); }
        .submit-btn:disabled { background: #e2e2e2; color: #a0a0a0; cursor: not-allowed; }

        /* ── PROGRESS SECTION ── */
        .progress-section {
          margin-top: 20px;
          background: #f8f8f8;
          border: 1px solid #e2e2e2;
          border-radius: 16px;
          padding: 20px;
          animation: fadeUp 0.3s ease;
        }
        @keyframes fadeUp { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }

        .progress-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }
        .progress-label {
          font-size: 13px;
          font-weight: 600;
          color: #0a0a0a;
        }
        .progress-pct {
          font-size: 13px;
          font-weight: 700;
          color: #0a0a0a;
          font-family: 'Syne', sans-serif;
        }

        .progress-bar-track {
          height: 6px;
          background: #e2e2e2;
          border-radius: 3px;
          overflow: hidden;
          margin-bottom: 16px;
        }
        .progress-bar-fill {
          height: 100%;
          background: #0a0a0a;
          border-radius: 3px;
          transition: width 0.8s cubic-bezier(0.4,0,0.2,1);
        }

        .steps-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .step-row {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 13px;
          transition: all 0.3s;
        }
        .step-dot {
          width: 24px; height: 24px;
          border-radius: 50%;
          display: flex; align-items: center; justify-content: center;
          font-size: 12px;
          flex-shrink: 0;
          transition: all 0.3s;
        }
        .step-dot.done { background: #0a0a0a; color: white; }
        .step-dot.active { background: #f0f0f0; border: 2px solid #0a0a0a; animation: pulse 1.5s infinite; }
        .step-dot.pending { background: #f0f0f0; color: #c0c0c0; }
        @keyframes pulse { 0%,100%{box-shadow:0 0 0 0 rgba(10,10,10,0.2)} 50%{box-shadow:0 0 0 4px rgba(10,10,10,0.1)} }

        .step-label { transition: color 0.3s; }
        .step-label.done { color: #0a0a0a; font-weight: 500; }
        .step-label.active { color: #0a0a0a; font-weight: 600; }
        .step-label.pending { color: #c0c0c0; }

        .error-box {
          background: #fef2f2;
          border: 1px solid #fca5a5;
          border-radius: 10px;
          padding: 10px 14px;
          font-size: 13px;
          color: #dc2626;
          margin-top: 12px;
        }

        .up-footer {
          margin-top: 20px;
          font-size: 12px;
          color: #c0c0c0;
          text-align: center;
          position: relative;
          z-index: 1;
        }
      `}</style>

      <div className="up-page">
        <div className="dot-bg" />

        <button className="back-btn" onClick={() => navigate('/')}>← Back</button>

        <div className="up-logo">TalkDox 🧠</div>
        <p className="up-tagline">Choose your source to get started</p>

        <div className="up-card">

          {/* Tabs */}
          <div className="tab-row">
            {tabs.map(tab => (
              <button
                key={tab.id}
                className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => { setActiveTab(tab.id); setError(''); setLoading(false); setLoadingStep(0) }}
              >
                <span>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>

          {/* PDF */}
          {activeTab === 'pdf' && !loading && (
            <div>
              <div className="section-title">Upload PDF</div>
              <div className="section-sub">Drop one or more PDF files to chat with them instantly.</div>
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

          {/* Web */}
          {activeTab === 'web' && !loading && (
            <div>
              <div className="section-title">Paste Website URL</div>
              <div className="section-sub">Any article, blog post, documentation page, or website.</div>
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

          {/* YouTube */}
          {activeTab === 'youtube' && !loading && (
            <div>
              <div className="section-title">Paste YouTube Link</div>
              <div className="section-sub">Lectures, tutorials, interviews — any video with captions.</div>
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
                  <div className="yt-overlay">
                    <div className="yt-play-btn">▶</div>
                  </div>
                </div>
              )}
              <button className="submit-btn" onClick={handleYT} disabled={!ytUrl}>
                ▶ Extract Transcript & Index
              </button>
            </div>
          )}

          {/* Progress */}
          {loading && (
            <div className="progress-section">
              <div className="progress-header">
                <span className="progress-label">{activeSteps[loadingStep]?.label}</span>
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

          {/* Error */}
          {error && <div className="error-box">❌ {error}</div>}

        </div>

        <p className="up-footer">Powered by Google Gemini 2.5 Flash · FAISS Vector Search</p>
      </div>
    </>
  )
}