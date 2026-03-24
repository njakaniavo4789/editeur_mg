import React, { useState } from 'react'
import useEditorStore from '../../store/editorStore'
import { detecterEntites } from '../../services/api'

const TYPE_COLORS = {
  PER:  '#6366f1',
  ORG:  '#f59e0b',
  LOC:  '#10b981',
  DATE: '#3b82f6',
  MISC: '#8b5cf6',
}

function getColor(type) {
  return TYPE_COLORS[type?.toUpperCase()] || '#64748b'
}

export default function PanelNER() {
  const texte = useEditorStore((s) => s.texte)
  const entites = useEditorStore((s) => s.entites)
  const setEntites = useEditorStore((s) => s.setEntites)
  const [loading, setLoading] = useState(false)

  const handleDetect = async () => {
    if (!texte.trim()) return
    setLoading(true)
    try {
      const res = await detecterEntites(texte)
      setEntites(res.data.entites || [])
    } catch (err) {
      console.error('NER error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="panel panel-ner">
      <div className="panel-header">
        <span className="panel-icon">🏷️</span>
        <h3>Entités (NER)</h3>
        {entites.length > 0 && (
          <span className="badge badge-info">{entites.length}</span>
        )}
      </div>

      <div className="panel-body">
        {entites.length === 0 ? (
          <div className="panel-empty">
            <p>Tsindrio ny bokotra hanokafana ny entité.</p>
          </div>
        ) : (
          <div className="ner-list">
            {entites.map((ent, i) => {
              const text = ent.text || ent.mot || ent
              const type = ent.type || ent.label || 'MISC'
              const color = getColor(type)
              return (
                <div key={i} className="ner-item">
                  <span className="ner-text">{text}</span>
                  <span
                    className="ner-tag"
                    style={{ background: color + '22', color, borderColor: color }}
                  >
                    {type}
                  </span>
                </div>
              )
            })}
          </div>
        )}

        <button
          className="panel-btn"
          onClick={handleDetect}
          disabled={loading || !texte.trim()}
        >
          {loading ? '⏳ Detection...' : '🔍 Détecter'}
        </button>
      </div>
    </div>
  )
}
