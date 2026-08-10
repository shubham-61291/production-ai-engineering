import React, { useState } from 'react'

export default function App() {
  const [question, setQuestion] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState(null)
  const [uploadStatus, setUploadStatus] = useState('')

  const handleAsk = async (e) => {
    e.preventDefault()
    if (!question) return
    setLoading(true)
    try {
      const res = await fetch('/api/v1/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey || 'your-strong-api-key-here'
        },
        body: JSON.stringify({ question, top_k: 5 })
      })
      const data = await res.json()
      setResponse(data)
    } catch (err) {
      setResponse({ answer: 'Failed to connect to Magnetar AI backend.', sources: [] })
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setUploadStatus('Uploading and indexing document...')
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch('/api/v1/upload', {
        method: 'POST',
        headers: {
          'X-API-Key': apiKey || 'your-strong-api-key-here'
        },
        body: formData
      })
      const data = await res.json()
      if (res.ok) {
        setUploadStatus(`Uploaded: ${data.filename} (${data.chunks_created} chunks indexed)`)
      } else {
        setUploadStatus(`Upload failed: ${data.detail || 'Error'}`)
      }
    } catch (err) {
      setUploadStatus('Upload failed due to network error.')
    }
  }

  return (
    <div className="app-container">
      <header>
        <div className="brand">
          <div className="logo">M</div>
          <div>
            <h1>Magnetar AI</h1>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Enterprise RAG & Hybrid Intelligence Core</p>
          </div>
        </div>
        <div className="status-badge">
          <div className="status-dot"></div>
          System Online
        </div>
      </header>

      <div className="dashboard-grid">
        <main className="glass-panel">
          <form onSubmit={handleAsk} className="query-box">
            <label style={{ fontSize: '14px', fontWeight: 600 }}>Query Engine</label>
            <textarea
              placeholder="Ask a question or request intelligence analysis..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <input
                type="password"
                placeholder="API Key"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                style={{
                  background: 'rgba(10, 13, 20, 0.6)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  padding: '8px 12px',
                  color: '#fff',
                  width: '220px'
                }}
              />
              <button type="submit" className="btn-primary" disabled={loading}>
                {loading ? 'Processing...' : 'Run Query'}
              </button>
            </div>
          </form>

          {response && (
            <div className="response-panel">
              <h3 style={{ fontSize: '16px', color: 'var(--accent-cyan)' }}>Synthesis Result</h3>
              <div className="answer-card">
                {response.prompt_injection_detected && (
                  <p style={{ color: 'var(--accent-danger)', fontWeight: 600, marginBottom: '8px' }}>
                    🚨 Prompt Injection Shield Triggered
                  </p>
                )}
                <p>{response.answer}</p>
              </div>

              {response.sources && response.sources.length > 0 && (
                <div style={{ marginTop: '20px' }}>
                  <h4 style={{ fontSize: '14px', color: 'var(--text-muted)' }}>Context Sources ({response.sources.length})</h4>
                  <div className="sources-list">
                    {response.sources.map((src, idx) => (
                      <div key={idx} className="source-item">
                        <strong>[{src.source || 'RAG'}]</strong> {src.text}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </main>

        <aside className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <h3 style={{ fontSize: '16px', color: 'var(--accent-cyan)' }}>Knowledge Base Ingestion</h3>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
            Upload PDF, DOCX, or TXT documents to index into ChromaDB vector store and BM25 text ranker.
          </p>

          <label
            style={{
              display: 'block',
              padding: '24px',
              border: '2px dashed var(--border-color)',
              borderRadius: '12px',
              textAlign: 'center',
              cursor: 'pointer',
              background: 'rgba(10, 13, 20, 0.4)'
            }}
          >
            <span style={{ fontSize: '14px', color: 'var(--accent-blue)' }}>+ Choose Document</span>
            <input type="file" onChange={handleFileUpload} style={{ display: 'none' }} accept=".pdf,.docx,.txt" />
          </label>

          {uploadStatus && (
            <p style={{ fontSize: '12px', color: 'var(--accent-cyan)' }}>{uploadStatus}</p>
          )}

          <div style={{ marginTop: 'auto', paddingTop: '20px', borderTop: '1px solid var(--border-color)' }}>
            <h4 style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Architecture</h4>
            <ul style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '8px', paddingLeft: '16px' }}>
              <li>Vector: ChromaDB persist</li>
              <li>Keyword: BM25 Okapi</li>
              <li>Cache: Redis SHA256</li>
              <li>Guard: DeBERTa Injection Shield</li>
            </ul>
          </div>
        </aside>
      </div>
    </div>
  )
}
