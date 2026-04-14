import React, { useState } from 'react'
import useEditorStore from '../../store/editorStore'
import { analyserSentiment } from '../../services/api'

const SENTIMENT_CONFIG = {
  POSITIF: { icon: '😊', color: '#22c55e', label: 'Positif' },
  NEGATIF: { icon: '😔', color: '#ef4444', label: 'Négatif' },
  NEUTRE:  { icon: '😐', color: '#94a3b8', label: 'Neutre' },
}

export default function PanelSentiment() {
  const texte = useEditorStore((s) => s.texte)
  const sentiment = useEditorStore((s) => s.sentiment)
  const setSentiment = useEditorStore((s) => s.setSentiment)
  const [loading, setLoading] = useState(false)

  const handleAnalyse = async () => {
    if (!texte.trim()) return
    setLoading(true)
    try {
      const res = await analyserSentiment(texte)
      setSentiment(res.data.resultat)
    } catch (err) {
      console.error('Sentiment error:', err)
    } finally {
      setLoading(false)
    }
  }

  const config = sentiment ? (SENTIMENT_CONFIG[sentiment.label] || SENTIMENT_CONFIG.NEUTRE) : null

  return (
    <div className="panel panel-sentiment">
      <div className="panel-header">
        <span className="panel-icon">😊</span>
        <h3>Sentiment</h3>
      </div>

      <div className="panel-body">
        {config ? (
          <div className="sentiment-result">
            <div
              className="sentiment-badge"
              style={{ borderColor: config.color, color: config.color }}
            >
              <span className="sentiment-icon">{config.icon}</span>
              <span className="sentiment-label">{config.label}</span>
            </div>
            <div className="sentiment-score">
              Score : <strong>{sentiment.score > 0 ? '+' : ''}{sentiment.score}</strong>
            </div>
          </div>
        ) : (
          <div className="panel-empty">
            <p>Tsindrio ny bokotra hanaovana ny fanadihadiana sentiment.</p>
          </div>
        )}

        <button
          className="panel-btn"
          onClick={handleAnalyse}
          disabled={loading || !texte.trim()}
        >
          {loading ? '⏳ Analyzing...' : '🔍 Analyser'}
        </button>
      </div>
    </div>
  )
}
