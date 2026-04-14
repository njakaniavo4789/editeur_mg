import React, { useEffect, useRef } from 'react'
import { lemmatiser, traduire, correcterMot } from '../../services/api'

export default function RightClickMenu({ x, y, selectedText, getFullText, onClose }) {
  const ref = useRef(null)
  const [result, setResult] = React.useState(null)
  const [loading, setLoading] = React.useState(false)

  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) onClose()
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [onClose])

  const word = selectedText.trim() || getFullText().trim().split(/\s+/).pop() || ''

  const handle = async (fn) => {
    if (!word) return
    setLoading(true)
    setResult(null)
    try {
      const res = await fn(word)
      setResult(res.data)
    } catch {
      setResult({ error: 'Tsy nahomby' })
    } finally {
      setLoading(false)
    }
  }

  // Keep menu inside viewport
  const style = {
    position: 'fixed',
    top: Math.min(y, window.innerHeight - 220),
    left: Math.min(x, window.innerWidth - 220),
    zIndex: 9999,
  }

  return (
    <div ref={ref} className="context-menu" style={style}>
      <div className="context-menu-header">
        {word ? `"${word.slice(0, 20)}"` : 'Tsy misy teny'}
      </div>

      <button className="context-menu-item" onClick={() => handle(lemmatiser)}>
        🌱 Lemmatiser
      </button>
      <button className="context-menu-item" onClick={() => handle(traduire)}>
        🌐 Traduire (MG→FR)
      </button>
      <button className="context-menu-item" onClick={() => handle(correcterMot)}>
        ✏️ Corriger le mot
      </button>

      {loading && <div className="context-menu-result loading">⏳ Eo ampelatanana...</div>}

      {result && !loading && (
        <div className="context-menu-result">
          {result.error && <span className="error-text">{result.error}</span>}
          {result.lemme && <span>🌱 {result.lemme}</span>}
          {result.traduction && <span>🌐 {result.traduction}</span>}
          {result.suggestions && result.suggestions.length > 0 && (
            <span>✏️ {result.suggestions.slice(0, 3).join(', ')}</span>
          )}
          {result.suggestions && result.suggestions.length === 0 && (
            <span className="ok-text">✅ Correct</span>
          )}
        </div>
      )}
    </div>
  )
}
