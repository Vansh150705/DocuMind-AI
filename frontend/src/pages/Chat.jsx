import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

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
    axios.get('/api/state').then(r => {
      if (!r.data.processed) { navigate('/upload'); return }
      setState(r.data)
      setMessages(r.data.chat_history || [])
    })
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  useEffect(() => {
    if (activeTab === 'analytics') {
      axios.get('/api/analytics').then(r => setAnalytics(r.data))
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
      fd.append('question', question)
      fd.append('mode', mode)
      fd.append('persona', persona)
      const r = await axios.post('/api/chat', fd)
      setMessages(prev => [...prev, {role:'assistant', content:r.data.answer, sources:r.data.sources, confidence:r.data.confidence}])
    } catch(e) {
      setMessages(prev => [...prev, {role:'assistant', content:'❌ Error: ' + (e.response?.data?.error || 'Something went wrong')}])
    } finally { setLoading(false) }
  }

  const runTool = async (tool) => {
    setToolLoading(true); setToolResult('')
    try {
      const fd = new FormData(); fd.append('tool', tool)
      const r = await axios.post('/api/tools', fd)
      setToolResult(r.data.result)
    } catch(e) { setToolResult('❌ Tool failed.') }
    finally { setToolLoading(false) }
  }

  const extractTimeline = async () => {
    setTlLoading(true)
    try {
      const r = await axios.post('/api/timeline')
      setTimeline(r.data.timeline)
      setTlGenerated(true)
    } catch(e) {}
    finally { setTlLoading(false) }
  }

  const generateFlashcards = async () => {
    setFcLoading(true)
    try {
      const fd = new FormData(); fd.append('count', fcCount)
      const r = await axios.post('/api/flashcards', fd)
      setFlashcards(r.data.flashcards)
    } catch(e) {}
    finally { setFcLoading(false) }
  }

  const uploadCompare = async () => {
    if (!compareFile) return
    const fd = new FormData(); fd.append('files', compareFile)
    await axios.post('/api/compare/upload', fd)
    setCompareLoaded(true)
  }

  const sendCompare = async () => {
    const q = compareInput.trim(); if (!q) return
    setCompareInput('')
    setCompareMessages(prev => [...prev, {role:'user',content:q}])
    setCompareLoading(true)
    try {
      const fd = new FormData(); fd.append('question', q)
      const r = await axios.post('/api/compare/chat', fd)
      setCompareMessages(prev => [...prev, {role:'assistant',content:r.data.answer,sources_a:r.data.sources_a,sources_b:r.data.sources_b}])
    } catch(e) {}
    finally { setCompareLoading(false) }
  }

  const reset = async () => {
    await axios.post('/api/reset')
    navigate('/upload')
  }

  if (!state) return <div style={{display:'flex',alignItems:'center',justifyContent:'center',height:'100vh',fontFamily:'DM Sans,sans-serif',color:'#5a5a5a'}}>Loading...</div>

  const tabs = ['chat','dna','tools','analytics','compare','timeline','flashcards']
  const tabLabels = {chat:'💬 Chat',dna:'🧬 DNA',tools:'🛠 Tools',analytics:'📊 Analytics',compare:'🔀 Compare',timeline:'🕐 Timeline',flashcards:'🃏 Flashcards'}
  const pdfOnlyTabs = state.source_type === 'pdf' ? tabs : ['chat','timeline','flashcards']

  const confColor = (c) => c > 60 ? '#16a34a' : c > 30 ? '#d97706' : '#dc2626'
  const confLabel = (c) => c > 60 ? 'High' : c > 30 ? 'Medium' : 'Low'

  const tlColors = {deadline:{bg:'#fef2f2',border:'#fca5a5',dot:'#dc2626',label:'⏰ Deadline'},milestone:{bg:'#f0fdf4',border:'#86efac',dot:'#16a34a',label:'🏁 Milestone'},event:{bg:'#eff6ff',border:'#93c5fd',dot:'#2563eb',label:'📌 Event'},period:{bg:'#fefce8',border:'#fde68a',dot:'#d97706',label:'📆 Period'},announcement:{bg:'#faf5ff',border:'#d8b4fe',dot:'#9333ea',label:'📢 Announcement'},other:{bg:'#f9fafb',border:'#e5e7eb',dot:'#6b7280',label:'📋 Other'}}

  const diffStyles = {easy:{bg:'#f0fdf4',border:'#86efac',color:'#16a34a',label:'🟢 Easy'},medium:{bg:'#fefce8',border:'#fde68a',color:'#d97706',label:'🟡 Medium'},hard:{bg:'#fef2f2',border:'#fca5a5',color:'#dc2626',label:'🔴 Hard'}}

  return (
    <div style={{display:'grid',gridTemplateColumns:'260px 1fr',height:'100vh',fontFamily:'DM Sans,sans-serif',background:'#f8f8f8'}}>

      {/* Sidebar */}
      <div style={{background:'#fff',borderRight:'1px solid #e2e2e2',display:'flex',flexDirection:'column',padding:'24px 16px'}}>
        <div style={{fontFamily:'Syne,sans-serif',fontWeight:800,fontSize:20,marginBottom:8,padding:'0 8px'}}>TalkDox 🧠</div>

        {/* Source info */}
        <div style={{background:'#f8f8f8',border:'1px solid #e2e2e2',borderRadius:12,padding:12,marginBottom:24}}>
          <div style={{fontSize:11,fontWeight:600,textTransform:'uppercase',letterSpacing:'0.08em',color:'#a0a0a0',marginBottom:6}}>Source</div>
          <div style={{fontSize:13,fontWeight:500,color:'#0a0a0a'}}>
            {state.source_type==='pdf'?'📄':state.source_type==='web'?'🌐':'▶'} {(state.pdf_names[0]||'').slice(0,30)}
          </div>
          <div style={{display:'flex',gap:8,marginTop:8,flexWrap:'wrap'}}>
            <span style={{fontSize:11,background:'#f0f0f0',padding:'2px 8px',borderRadius:20,color:'#5a5a5a'}}>{state.total_chunks} chunks</span>
            {state.source_type==='pdf' && <span style={{fontSize:11,background:'#f0f0f0',padding:'2px 8px',borderRadius:20,color:'#5a5a5a'}}>{state.total_pages} pages</span>}
            {state.doc_language && state.doc_language!=='English' && <span style={{fontSize:11,background:'#eff6ff',padding:'2px 8px',borderRadius:20,color:'#2563eb'}}>🌐 {state.doc_language}</span>}
          </div>
        </div>

        {/* Nav */}
        <nav style={{flex:1}}>
          {pdfOnlyTabs.map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)} style={{
              width:'100%', textAlign:'left', padding:'10px 12px', borderRadius:10, border:'none',
              background: activeTab===tab ? '#0a0a0a' : 'transparent',
              color: activeTab===tab ? '#fff' : '#5a5a5a',
              fontSize:14, fontWeight:500, cursor:'pointer', marginBottom:4, transition:'all 0.15s',
              display:'flex', alignItems:'center', gap:8
            }}>
              {tabLabels[tab]}
            </button>
          ))}
        </nav>

        {/* Bottom buttons */}
        <div style={{borderTop:'1px solid #e2e2e2',paddingTop:16,display:'flex',flexDirection:'column',gap:8}}>
          <button onClick={() => navigate('/upload')} style={{background:'#f8f8f8',border:'1px solid #e2e2e2',borderRadius:10,padding:'10px 12px',fontSize:13,fontWeight:500,cursor:'pointer',color:'#5a5a5a',textAlign:'left'}}>
            ↑ New Source
          </button>
          <button onClick={reset} style={{background:'#fef2f2',border:'1px solid #fca5a5',borderRadius:10,padding:'10px 12px',fontSize:13,fontWeight:500,cursor:'pointer',color:'#dc2626',textAlign:'left'}}>
            ↺ Reset All
          </button>
        </div>
      </div>

      {/* Main */}
      <div style={{display:'flex',flexDirection:'column',overflow:'hidden'}}>

        {/* Header */}
        <div style={{background:'#fff',borderBottom:'1px solid #e2e2e2',padding:'16px 24px',display:'flex',alignItems:'center',gap:16}}>
          <h2 style={{fontFamily:'Syne,sans-serif',fontSize:20,fontWeight:700,flex:1}}>{tabLabels[activeTab]}</h2>
          {activeTab==='chat' && (
            <div style={{display:'flex',gap:8}}>
              <select value={mode} onChange={e=>setMode(e.target.value)} style={{border:'1px solid #e2e2e2',borderRadius:8,padding:'6px 10px',fontSize:13,fontFamily:'DM Sans,sans-serif',background:'#fff',cursor:'pointer'}}>
                <option value="qa">🎯 Standard Q&A</option>
                <option value="eli5">🧒 Explain Simply</option>
                <option value="executive">💼 Executive Brief</option>
                <option value="debate">⚖️ Devil's Advocate</option>
              </select>
              <select value={persona} onChange={e=>setPersona(e.target.value)} style={{border:'1px solid #e2e2e2',borderRadius:8,padding:'6px 10px',fontSize:13,fontFamily:'DM Sans,sans-serif',background:'#fff',cursor:'pointer'}}>
                <option value="default">🤖 Default</option>
                <option value="lawyer">⚖️ Lawyer</option>
                <option value="doctor">🩺 Doctor</option>
                <option value="financial">📈 Financial</option>
                <option value="teacher">📚 Teacher</option>
                <option value="journalist">📰 Journalist</option>
              </select>
            </div>
          )}
        </div>

        {/* Content */}
        <div style={{flex:1,overflow:'auto',padding:24}}>

          {/* ── CHAT TAB ── */}
          {activeTab==='chat' && (
            <div style={{display:'flex',flexDirection:'column',height:'100%'}}>
              <div style={{flex:1,overflow:'auto',display:'flex',flexDirection:'column',gap:16,paddingBottom:16}}>
                {messages.length===0 && (
                  <div>
                    <p style={{color:'#a0a0a0',fontSize:14,marginBottom:16}}>Try asking:</p>
                    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8}}>
                      {['What is the main topic?','Summarize the key points','What conclusions are drawn?','List the most important findings'].map(s=>(
                        <button key={s} onClick={()=>sendMessage(s)} style={{background:'#fff',border:'1px solid #e2e2e2',borderRadius:12,padding:'12px 16px',fontSize:13,textAlign:'left',cursor:'pointer',fontFamily:'DM Sans,sans-serif',transition:'all 0.2s',color:'#374151'}}>
                          {s}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                {messages.map((msg,i) => (
                  <div key={i}>
                    <div style={{display:'flex',justifyContent:msg.role==='user'?'flex-end':'flex-start'}}>
                      <div style={{maxWidth:'75%',padding:'12px 16px',borderRadius:msg.role==='user'?'18px 18px 4px 18px':'18px 18px 18px 4px',background:msg.role==='user'?'#0a0a0a':'#fff',color:msg.role==='user'?'#fff':'#0a0a0a',fontSize:14,lineHeight:1.7,border:msg.role==='assistant'?'1px solid #e2e2e2':'none',boxShadow:'0 2px 8px rgba(0,0,0,0.06)',whiteSpace:'pre-wrap'}}>
                        {msg.content}
                      </div>
                    </div>
                    {msg.role==='assistant' && msg.confidence != null && (
                      <div style={{display:'flex',justifyContent:'flex-start',marginTop:6}}>
                        <div style={{fontSize:12,color:'#a0a0a0',maxWidth:'75%'}}>
                          Confidence: <span style={{color:confColor(msg.confidence),fontWeight:600}}>{msg.confidence}% ({confLabel(msg.confidence)})</span>
                          <div style={{height:4,background:'#e2e2e2',borderRadius:2,marginTop:4,overflow:'hidden'}}>
                            <div style={{height:'100%',width:`${msg.confidence}%`,background:confColor(msg.confidence),borderRadius:2,transition:'width 0.7s'}}/>
                          </div>
                          {msg.sources?.length > 0 && (
                            <div style={{marginTop:6,display:'flex',gap:4,flexWrap:'wrap'}}>
                              {msg.sources.map(s=><span key={s} style={{background:'#f8f8f8',border:'1px solid #e2e2e2',borderRadius:20,padding:'2px 8px',fontSize:11,color:'#5a5a5a'}}>📄 {s}</span>)}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
                {loading && (
                  <div style={{display:'flex',gap:8}}>
                    <div style={{padding:'12px 16px',borderRadius:'18px 18px 18px 4px',background:'#fff',border:'1px solid #e2e2e2',display:'flex',gap:4,alignItems:'center'}}>
                      {[0,1,2].map(i=><span key={i} style={{width:6,height:6,background:'#e2e2e2',borderRadius:'50%',display:'block',animation:`dot 1.2s ease-in-out ${i*0.16}s infinite`}}/>)}
                      <span style={{fontSize:12,color:'#a0a0a0',marginLeft:4,fontStyle:'italic'}}>Thinking…</span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef}/>
              </div>

              {/* Input */}
              <div style={{background:'#fff',border:'1.5px solid #e2e2e2',borderRadius:16,padding:'12px 16px',display:'flex',gap:12,alignItems:'center',marginTop:'auto',boxShadow:'0 1px 4px rgba(0,0,0,0.06)'}}>
                <input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMessage()}}}
                  placeholder="Ask anything about your content..." disabled={loading}
                  style={{flex:1,border:'none',outline:'none',fontSize:15,fontFamily:'DM Sans,sans-serif',color:'#0a0a0a',background:'transparent'}}/>
                <button onClick={()=>sendMessage()} disabled={!input.trim()||loading} style={{background:'#0a0a0a',color:'#fff',border:'none',borderRadius:10,width:36,height:36,display:'flex',alignItems:'center',justifyContent:'center',cursor:input.trim()?'pointer':'not-allowed',fontSize:16,opacity:input.trim()?1:0.4}}>
                  →
                </button>
              </div>
            </div>
          )}

          {/* ── DNA TAB ── */}
          {activeTab==='dna' && (
            <div>
              {!state.dna ? (
                <div style={{textAlign:'center',padding:'40px 0',color:'#a0a0a0'}}>DNA analysis not available for this source type.</div>
              ) : (
                <div style={{display:'flex',flexDirection:'column',gap:16}}>
                  <div style={{background:'#fff',border:'1px solid #e2e2e2',borderRadius:16,padding:24}}>
                    <div style={{fontFamily:'Syne,sans-serif',fontSize:22,fontWeight:700,marginBottom:8}}>{state.dna.title || 'Document'}</div>
                    <p style={{fontSize:15,color:'#5a5a5a',lineHeight:1.7}}>{state.dna.one_line_summary}</p>
                  </div>
                  <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
                    <div style={{background:'#fff',border:'1px solid #e2e2e2',borderRadius:16,padding:24}}>
                      {[['Domain',state.dna.domain],['Tone',state.dna.tone],['Language',`🌐 ${state.dna.language}`]].map(([k,v])=>(
                        <div key={k} style={{marginBottom:16}}>
                          <div style={{fontSize:11,fontWeight:600,textTransform:'uppercase',letterSpacing:'0.1em',color:'#a0a0a0',marginBottom:4}}>{k}</div>
                          <div style={{fontSize:16,fontWeight:600}}>{v}</div>
                        </div>
                      ))}
                    </div>
                    <div style={{background:'#fff',border:'1px solid #e2e2e2',borderRadius:16,padding:24}}>
                      {[['Complexity',state.dna.complexity,'#0a0a0a'],['Sentiment',state.dna.sentiment,'#22c55e'],['Informativeness',state.dna.informativeness,'#6366f1']].map(([label,val,color])=>(
                        <div key={label} style={{marginBottom:16}}>
                          <div style={{fontSize:12,color:'#5a5a5a',marginBottom:4,fontWeight:500}}>{label} — {val}%</div>
                          <div style={{height:8,background:'#f0f0f0',borderRadius:4,overflow:'hidden'}}>
                            <div style={{height:'100%',width:`${val}%`,background:color,borderRadius:4,transition:'width 0.8s'}}/>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  {state.dna.key_themes?.length > 0 && (
                    <div style={{background:'#fff',border:'1px solid #e2e2e2',borderRadius:16,padding:24}}>
                      <div style={{fontSize:11,fontWeight:600,textTransform:'uppercase',letterSpacing:'0.1em',color:'#a0a0a0',marginBottom:12}}>Key Themes</div>
                      <div style={{display:'flex',flexWrap:'wrap',gap:8}}>
                        {state.dna.key_themes.map(t=><span key={t} style={{background:'#f8f8f8',border:'1px solid #e2e2e2',borderRadius:20,padding:'4px 12px',fontSize:13,color:'#374151'}}>#{t}</span>)}
                      </div>
                    </div>
                  )}
                  {state.dna.unusual_insight && (
                    <div style={{background:'#fff',border:'1px solid #e2e2e2',borderRadius:16,padding:24}}>
                      <div style={{fontSize:11,fontWeight:600,textTransform:'uppercase',letterSpacing:'0.1em',color:'#a0a0a0',marginBottom:8}}>💡 Unusual Insight</div>
                      <p style={{fontSize:15,color:'#374151',lineHeight:1.7}}>{state.dna.unusual_insight}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* ── TOOLS TAB ── */}
          {activeTab==='tools' && (
            <div>
              <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:12,marginBottom:24}}>
                {[
                  {id:'summary',icon:'📝',label:'Auto Summary'},
                  {id:'quiz',icon:'❓',label:'Generate Quiz'},
                  {id:'email',icon:'📧',label:'Draft Email'},
                  {id:'contradictions',icon:'🔍',label:'Find Contradictions'},
                  {id:'actions',icon:'📊',label:'Action Items'},
                ].map(tool=>(
                  <button key={tool.id} onClick={()=>runTool(tool.id)} disabled={toolLoading} style={{background:'#fff',border:'1.5px solid #e2e2e2',borderRadius:14,padding:20,textAlign:'center',cursor:'pointer',transition:'all 0.2s',fontFamily:'DM Sans,sans-serif'}}>
                    <div style={{fontSize:28,marginBottom:8}}>{tool.icon}</div>
                    <div style={{fontSize:14,fontWeight:600}}>{tool.label}</div>
                  </button>
                ))}
              </div>
              {toolLoading && <div style={{textAlign:'center',color:'#a0a0a0',fontSize:14,padding:20}}>Running tool...</div>}
              {toolResult && (
                <div style={{background:'#fff',border:'1px solid #e2e2e2',borderRadius:16,padding:24,fontSize:14,lineHeight:1.8,color:'#374151',whiteSpace:'pre-wrap'}}>
                  {toolResult}
                </div>
              )}
            </div>
          )}

          {/* ── ANALYTICS TAB ── */}
          {activeTab==='analytics' && analytics && (
            <div style={{display:'flex',flexDirection:'column',gap:16}}>
              <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:16}}>
                {[['Questions Asked',analytics.total_q],['Avg Confidence',`${analytics.avg_conf}%`],['High Confidence',analytics.high_conf]].map(([label,val])=>(
                  <div key={label} style={{background:'#fff',border:'1px solid #e2e2e2',borderRadius:16,padding:24,textAlign:'center'}}>
                    <div style={{fontFamily:'Syne,sans-serif',fontSize:40,fontWeight:800,lineHeight:1}}>{val}</div>
                    <div style={{fontSize:12,color:'#a0a0a0',textTransform:'uppercase',letterSpacing:'0.1em',marginTop:8}}>{label}</div>
                  </div>
                ))}
              </div>
              {analytics.confs?.length > 0 && (
                <div style={{background:'#fff',border:'1px solid #e2e2e2',borderRadius:16,padding:24}}>
                  <div style={{fontSize:11,fontWeight:600,textTransform:'uppercase',letterSpacing:'0.1em',color:'#a0a0a0',marginBottom:16}}>Confidence Per Answer</div>
                  {analytics.confs.map((c,i)=>(
                    <div key={i} style={{marginBottom:12}}>
                      <div style={{fontSize:12,color:'#5a5a5a',marginBottom:4}}>Answer {i+1} — <span style={{color:confColor(c),fontWeight:600}}>{confLabel(c)} ({c}%)</span></div>
                      <div style={{height:8,background:'#f0f0f0',borderRadius:4,overflow:'hidden'}}>
                        <div style={{height:'100%',width:`${c}%`,background:confColor(c),borderRadius:4}}/>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ── COMPARE TAB ── */}
          {activeTab==='compare' && (
            <div>
              {!compareLoaded ? (
                <div style={{background:'#fff',border:'1px solid #e2e2e2',borderRadius:16,padding:32}}>
                  <h3 style={{fontFamily:'Syne,sans-serif',fontSize:20,fontWeight:700,marginBottom:8}}>Upload Second Document</h3>
                  <p style={{fontSize:14,color:'#5a5a5a',marginBottom:20}}>Upload a second PDF to compare against your primary document.</p>
                  <label style={{display:'block',border:'2px dashed #e2e2e2',borderRadius:12,padding:24,textAlign:'center',cursor:'pointer',background:'#f8f8f8'}}>
                    <input type="file" accept=".pdf" style={{display:'none'}} onChange={e=>setCompareFile(e.target.files[0])}/>
                    <div style={{fontSize:14,color:'#5a5a5a'}}>{compareFile ? `✅ ${compareFile.name}` : '📄 Click to upload PDF'}</div>
                  </label>
                  <button onClick={uploadCompare} disabled={!compareFile} style={{width:'100%',background:compareFile?'#0a0a0a':'#e2e2e2',color:compareFile?'#fff':'#a0a0a0',border:'none',borderRadius:12,padding:16,fontSize:15,fontWeight:600,marginTop:16,cursor:compareFile?'pointer':'not-allowed'}}>
                    ⚡ Index Second Document
                  </button>
                </div>
              ) : (
                <div style={{display:'flex',flexDirection:'column',height:'calc(100vh - 160px)'}}>
                  <div style={{display:'flex',gap:8,marginBottom:16}}>
                    <span style={{background:'#f0fdf4',border:'1px solid #bbf7d0',borderRadius:20,padding:'4px 12px',fontSize:13,color:'#15803d'}}>📄 A: {state.pdf_names[0]?.slice(0,25)}</span>
                    <span style={{color:'#a0a0a0',fontSize:14,alignSelf:'center'}}>vs</span>
                    <span style={{background:'#eff6ff',border:'1px solid #bfdbfe',borderRadius:20,padding:'4px 12px',fontSize:13,color:'#1d4ed8'}}>📄 B: {compareFile?.name?.slice(0,25)}</span>
                  </div>
                  <div style={{flex:1,overflow:'auto',display:'flex',flexDirection:'column',gap:12,paddingBottom:16}}>
                    {compareMessages.length===0 && (
                      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8}}>
                        {['What are the key differences?','What do both agree on?','Which is more comprehensive?','What is in A but missing in B?'].map(q=>(
                          <button key={q} onClick={()=>{setCompareInput(q);setTimeout(sendCompare,100)}} style={{background:'#fff',border:'1px solid #e2e2e2',borderRadius:12,padding:'12px 16px',fontSize:13,textAlign:'left',cursor:'pointer',fontFamily:'DM Sans,sans-serif'}}>
                            {q}
                          </button>
                        ))}
                      </div>
                    )}
                    {compareMessages.map((msg,i)=>(
                      <div key={i}>
                        <div style={{display:'flex',justifyContent:msg.role==='user'?'flex-end':'flex-start'}}>
                          <div style={{maxWidth:'75%',padding:'12px 16px',borderRadius:msg.role==='user'?'18px 18px 4px 18px':'18px 18px 18px 4px',background:msg.role==='user'?'#0a0a0a':'#fff',color:msg.role==='user'?'#fff':'#0a0a0a',fontSize:14,lineHeight:1.7,border:msg.role==='assistant'?'1px solid #e2e2e2':'none',whiteSpace:'pre-wrap'}}>
                            {msg.content}
                          </div>
                        </div>
                        {msg.role==='assistant' && (msg.sources_a?.length>0||msg.sources_b?.length>0) && (
                          <div style={{display:'flex',gap:4,marginTop:6,flexWrap:'wrap'}}>
                            {msg.sources_a?.map(s=><span key={s} style={{background:'#f0fdf4',border:'1px solid #bbf7d0',borderRadius:20,padding:'2px 8px',fontSize:11,color:'#15803d'}}>A: {s}</span>)}
                            {msg.sources_b?.map(s=><span key={s} style={{background:'#eff6ff',border:'1px solid #bfdbfe',borderRadius:20,padding:'2px 8px',fontSize:11,color:'#1d4ed8'}}>B: {s}</span>)}
                          </div>
                        )}
                      </div>
                    ))}
                    {compareLoading && <div style={{padding:'12px 16px',borderRadius:'18px 18px 18px 4px',background:'#fff',border:'1px solid #e2e2e2',fontSize:13,color:'#a0a0a0',width:'fit-content'}}>Comparing...</div>}
                  </div>
                  <div style={{background:'#fff',border:'1.5px solid #e2e2e2',borderRadius:16,padding:'12px 16px',display:'flex',gap:12}}>
                    <input value={compareInput} onChange={e=>setCompareInput(e.target.value)} onKeyDown={e=>{if(e.key==='Enter')sendCompare()}} placeholder="Ask anything about both documents..." style={{flex:1,border:'none',outline:'none',fontSize:15,fontFamily:'DM Sans,sans-serif'}}/>
                    <button onClick={sendCompare} style={{background:'#0a0a0a',color:'#fff',border:'none',borderRadius:10,width:36,height:36,display:'flex',alignItems:'center',justifyContent:'center',cursor:'pointer'}}>→</button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ── TIMELINE TAB ── */}
          {activeTab==='timeline' && (
            <div>
              {!tlGenerated ? (
                <button onClick={extractTimeline} disabled={tlLoading} style={{background:'#0a0a0a',color:'#fff',border:'none',borderRadius:12,padding:'14px 28px',fontSize:15,fontWeight:600,cursor:'pointer'}}>
                  {tlLoading ? 'Extracting...' : '🕐 Extract Timeline'}
                </button>
              ) : (
                <div>
                  <button onClick={()=>{setTlGenerated(false);setTimeline([])}} style={{background:'#f8f8f8',border:'1px solid #e2e2e2',borderRadius:10,padding:'8px 16px',fontSize:13,cursor:'pointer',marginBottom:20}}>↺ Re-extract</button>
                  {timeline.length===0 ? <p style={{color:'#a0a0a0'}}>No dates found in this document.</p> : (
                    <div style={{position:'relative',paddingLeft:32}}>
                      <div style={{position:'absolute',left:7,top:4,bottom:4,width:2,background:'#e2e2e2',borderRadius:2}}/>
                      {timeline.map((event,i)=>{
                        const tc = tlColors[event.type]||tlColors.other
                        return (
                          <div key={i} style={{position:'relative',marginBottom:12}}>
                            <div style={{position:'absolute',left:-1.65*16,top:14,width:13,height:13,borderRadius:'50%',background:tc.dot,border:'2px solid #fff',boxShadow:`0 0 0 3px ${tc.dot}33`}}/>
                            <div style={{background:tc.bg,border:`1px solid ${tc.border}`,borderRadius:12,padding:'12px 16px'}}>
                              <div style={{display:'flex',justifyContent:'space-between',marginBottom:4}}>
                                <span style={{fontSize:11,fontWeight:700,textTransform:'uppercase',letterSpacing:'0.08em',color:tc.dot}}>{tc.label}</span>
                                <span style={{fontSize:11,color:'#a0a0a0'}}>{event.importance==='high'?'⬆ High':event.importance==='medium'?'— Medium':'↓ Low'}</span>
                              </div>
                              <div style={{fontSize:13,fontWeight:700,color:'#0a0a0a',marginBottom:4}}>📅 {event.date}</div>
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

          {/* ── FLASHCARDS TAB ── */}
          {activeTab==='flashcards' && (
            <div>
              <div style={{display:'flex',gap:12,marginBottom:20,alignItems:'center'}}>
                <select value={fcCount} onChange={e=>setFcCount(Number(e.target.value))} style={{border:'1px solid #e2e2e2',borderRadius:8,padding:'8px 12px',fontSize:14,fontFamily:'DM Sans,sans-serif',background:'#fff'}}>
                  {[5,8,10,15,20].map(n=><option key={n} value={n}>{n} flashcards</option>)}
                </select>
                <button onClick={generateFlashcards} disabled={fcLoading} style={{background:'#0a0a0a',color:'#fff',border:'none',borderRadius:12,padding:'10px 24px',fontSize:14,fontWeight:600,cursor:'pointer'}}>
                  {fcLoading ? 'Generating...' : '🃏 Generate'}
                </button>
                {flashcards.length>0 && (
                  <button onClick={()=>setFlashcards([])} style={{background:'#f8f8f8',border:'1px solid #e2e2e2',borderRadius:10,padding:'10px 16px',fontSize:13,cursor:'pointer'}}>↺ New Cards</button>
                )}
              </div>
              <div style={{display:'flex',flexDirection:'column',gap:12}}>
                {flashcards.map((card,i)=>{
                  const ds = diffStyles[card.difficulty]||diffStyles.medium
                  return (
                    <div key={i}>
                      <div style={{background:ds.bg,border:`1.5px solid ${ds.border}`,borderRadius:14,padding:'16px 20px',marginBottom:6}}>
                        <div style={{display:'flex',justifyContent:'space-between',marginBottom:8}}>
                          <span style={{fontSize:11,fontWeight:700,color:ds.color,textTransform:'uppercase',letterSpacing:'0.09em'}}>{ds.label}</span>
                          <span style={{fontSize:11,color:'#a0a0a0',textTransform:'uppercase',letterSpacing:'0.07em'}}>{card.topic}</span>
                        </div>
                        <div style={{fontSize:15,fontWeight:600,color:'#0a0a0a',lineHeight:1.55}}>{card.question}</div>
                      </div>
                      <details style={{background:'#fff',border:'1px solid #e2e2e2',borderRadius:12,overflow:'hidden'}}>
                        <summary style={{padding:'12px 16px',cursor:'pointer',fontSize:13,fontWeight:500,color:'#5a5a5a',listStyle:'none'}}>👁 Reveal Answer</summary>
                        <div style={{background:'#0a0a0a',padding:'16px 20px'}}>
                          <div style={{fontSize:10,fontWeight:600,color:'#5a5a5a',textTransform:'uppercase',letterSpacing:'0.1em',marginBottom:8}}>Answer</div>
                          <div style={{fontSize:14,color:'#f3f4f6',lineHeight:1.65}}>{card.answer}</div>
                        </div>
                      </details>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

        </div>
      </div>

      <style>{`
        @keyframes dot { 0%,80%,100%{opacity:0.3;transform:scale(0.8)} 40%{opacity:1;transform:scale(1.1)} }
        details summary::-webkit-details-marker { display:none; }
      `}</style>
    </div>
  )
}