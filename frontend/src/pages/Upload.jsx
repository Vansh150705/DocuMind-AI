import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function Upload() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('pdf')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [files, setFiles] = useState([])
  const [url, setUrl] = useState('')
  const [ytUrl, setYtUrl] = useState('')
  const [videoId, setVideoId] = useState('')

  const extractVideoId = (url) => {
    const m = url.match(/(?:v=|youtu\.be\/|embed\/|shorts\/)([a-zA-Z0-9_-]{11})/)
    return m ? m[1] : null
  }

  const handleYtUrlChange = (val) => {
    setYtUrl(val)
    const vid = extractVideoId(val)
    setVideoId(vid || '')
  }

  const handlePDF = async () => {
    if (!files.length) return
    setLoading(true); setError('')
    try {
      const fd = new FormData()
      files.forEach(f => fd.append('files', f))
      await axios.post('/api/upload/pdf', fd)
      navigate('/chat')
    } catch(e) {
      setError(e.response?.data?.error || 'Upload failed.')
    } finally { setLoading(false) }
  }

  const handleWeb = async () => {
    if (!url) return
    setLoading(true); setError('')
    try {
      const fd = new FormData()
      fd.append('url', url)
      await axios.post('/api/upload/web', fd)
      navigate('/chat')
    } catch(e) {
      setError(e.response?.data?.error || 'Failed to scrape page.')
    } finally { setLoading(false) }
  }

  const handleYT = async () => {
    if (!ytUrl) return
    setLoading(true); setError('')
    try {
      const fd = new FormData()
      fd.append('url', ytUrl)
      await axios.post('/api/upload/youtube', fd)
      navigate('/chat')
    } catch(e) {
      setError(e.response?.data?.error || 'Failed to fetch transcript.')
    } finally { setLoading(false) }
  }

  const tabs = [
    {id:'pdf', icon:'📄', label:'PDF Upload', char:'Paige'},
    {id:'web', icon:'🌐', label:'Website URL', char:'Webb'},
    {id:'youtube', icon:'▶', label:'YouTube Video', char:'Yuki'},
  ]

  return (
    <div style={{minHeight:'100vh',background:'#f8f8f8',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',padding:40}}>
      {/* Back */}
      <div style={{position:'fixed',top:24,left:24}}>
        <button onClick={() => navigate('/')} style={{background:'#fff',border:'1px solid #e2e2e2',borderRadius:100,padding:'8px 16px',fontSize:14,fontWeight:500,color:'#5a5a5a',cursor:'pointer'}}>
          ← Back
        </button>
      </div>

      {/* Logo */}
      <div style={{textAlign:'center',marginBottom:40}}>
        <div style={{fontFamily:'Syne,sans-serif',fontWeight:800,fontSize:28,marginBottom:8}}>TalkDox 🧠</div>
        <p style={{fontSize:16,color:'#5a5a5a'}}>Choose your source to get started</p>
      </div>

      {/* Card */}
      <div style={{background:'#fff',border:'1px solid #e2e2e2',borderRadius:24,padding:40,width:'100%',maxWidth:560,boxShadow:'0 8px 40px rgba(0,0,0,0.08)'}}>

        {/* Tab Switcher */}
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:8,marginBottom:32,background:'#f8f8f8',borderRadius:14,padding:4}}>
          {tabs.map(tab => (
            <button key={tab.id} onClick={() => {setActiveTab(tab.id);setError('')}} style={{
              background: activeTab===tab.id ? '#fff' : 'transparent',
              border: activeTab===tab.id ? '1px solid #e2e2e2' : '1px solid transparent',
              borderRadius: 10, padding:'10px 8px', fontSize:13, fontWeight:600,
              cursor:'pointer', transition:'all 0.2s', color: activeTab===tab.id ? '#0a0a0a' : '#a0a0a0',
              display:'flex', flexDirection:'column', alignItems:'center', gap:4
            }}>
              <span style={{fontSize:20}}>{tab.icon}</span>
              <span>{tab.char}</span>
            </button>
          ))}
        </div>

        {/* PDF Tab */}
        {activeTab === 'pdf' && (
          <div>
            <h3 style={{fontFamily:'Syne,sans-serif',fontSize:22,fontWeight:700,marginBottom:8}}>Upload PDF</h3>
            <p style={{fontSize:14,color:'#5a5a5a',marginBottom:20}}>Upload one or more PDF files to chat with them.</p>
            <label style={{display:'block',border:'2px dashed #e2e2e2',borderRadius:16,padding:32,textAlign:'center',cursor:'pointer',transition:'all 0.2s',background:'#f8f8f8'}}>
              <input type="file" accept=".pdf" multiple style={{display:'none'}} onChange={e => setFiles([...e.target.files])}/>
              <div style={{fontSize:32,marginBottom:8}}>📄</div>
              <div style={{fontSize:14,fontWeight:500,color:'#5a5a5a'}}>Click to upload or drag & drop</div>
              <div style={{fontSize:12,color:'#a0a0a0',marginTop:4}}>PDF files only</div>
            </label>
            {files.length > 0 && (
              <div style={{marginTop:12}}>
                {[...files].map(f => (
                  <div key={f.name} style={{background:'#f0fdf4',border:'1px solid #bbf7d0',borderRadius:8,padding:'6px 12px',fontSize:13,color:'#15803d',marginBottom:6}}>
                    ✅ {f.name}
                  </div>
                ))}
              </div>
            )}
            <button onClick={handlePDF} disabled={!files.length || loading} style={{width:'100%',background:files.length?'#0a0a0a':'#e2e2e2',color:files.length?'#fff':'#a0a0a0',border:'none',borderRadius:12,padding:'16px',fontSize:16,fontWeight:600,marginTop:20,cursor:files.length?'pointer':'not-allowed',transition:'all 0.2s'}}>
              {loading ? 'Processing...' : '⚡ Process & Index PDF'}
            </button>
          </div>
        )}

        {/* Web Tab */}
        {activeTab === 'web' && (
          <div>
            <h3 style={{fontFamily:'Syne,sans-serif',fontSize:22,fontWeight:700,marginBottom:8}}>Paste Website URL</h3>
            <p style={{fontSize:14,color:'#5a5a5a',marginBottom:20}}>Any article, blog post, documentation page, or website.</p>
            <input value={url} onChange={e=>setUrl(e.target.value)} placeholder="https://example.com/article" style={{width:'100%',border:'1.5px solid #e2e2e2',borderRadius:12,padding:'14px 16px',fontSize:15,outline:'none',transition:'border-color 0.2s',fontFamily:'DM Sans,sans-serif'}}
              onFocus={e=>e.target.style.borderColor='#0a0a0a'} onBlur={e=>e.target.style.borderColor='#e2e2e2'}/>
            <button onClick={handleWeb} disabled={!url || loading} style={{width:'100%',background:url?'#0a0a0a':'#e2e2e2',color:url?'#fff':'#a0a0a0',border:'none',borderRadius:12,padding:'16px',fontSize:16,fontWeight:600,marginTop:16,cursor:url?'pointer':'not-allowed',transition:'all 0.2s'}}>
              {loading ? 'Scraping...' : '🌐 Scrape & Index Page'}
            </button>
          </div>
        )}

        {/* YouTube Tab */}
        {activeTab === 'youtube' && (
          <div>
            <h3 style={{fontFamily:'Syne,sans-serif',fontSize:22,fontWeight:700,marginBottom:8}}>Paste YouTube Link</h3>
            <p style={{fontSize:14,color:'#5a5a5a',marginBottom:20}}>Lectures, tutorials, interviews, podcasts — any video with captions.</p>
            <input value={ytUrl} onChange={e=>handleYtUrlChange(e.target.value)} placeholder="https://www.youtube.com/watch?v=..." style={{width:'100%',border:'1.5px solid #e2e2e2',borderRadius:12,padding:'14px 16px',fontSize:15,outline:'none',transition:'border-color 0.2s',fontFamily:'DM Sans,sans-serif'}}
              onFocus={e=>e.target.style.borderColor='#0a0a0a'} onBlur={e=>e.target.style.borderColor='#e2e2e2'}/>
            {videoId && (
              <div style={{marginTop:16,borderRadius:12,overflow:'hidden',border:'1px solid #e2e2e2'}}>
                <img src={`https://img.youtube.com/vi/${videoId}/hqdefault.jpg`} alt="thumbnail" style={{width:'100%',display:'block'}}/>
              </div>
            )}
            <button onClick={handleYT} disabled={!ytUrl || loading} style={{width:'100%',background:ytUrl?'#0a0a0a':'#e2e2e2',color:ytUrl?'#fff':'#a0a0a0',border:'none',borderRadius:12,padding:'16px',fontSize:16,fontWeight:600,marginTop:16,cursor:ytUrl?'pointer':'not-allowed',transition:'all 0.2s'}}>
              {loading ? 'Fetching transcript...' : '▶ Extract Transcript & Index'}
            </button>
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{marginTop:16,background:'#fef2f2',border:'1px solid #fca5a5',borderRadius:10,padding:'10px 14px',fontSize:13,color:'#dc2626'}}>
            ❌ {error}
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div style={{marginTop:16,display:'flex',alignItems:'center',gap:8,color:'#5a5a5a',fontSize:14}}>
            <div style={{display:'flex',gap:3}}>
              {[0,1,2].map(i=><span key={i} style={{width:6,height:6,background:'#a0a0a0',borderRadius:'50%',display:'block',animation:`dot 1.2s ease-in-out ${i*0.2}s infinite`}}/>)}
            </div>
            Indexing your content with Gemini...
          </div>
        )}
      </div>
    </div>
  )
}