import React from 'react'
import useEditorStore from '../../store/editorStore'
import { analyserSentiment, detecterEntites } from '../../services/api'
import './Editor.css'

export default function Toolbar() {
  const texte = useEditorStore((s) => s.texte)
  const setSentiment = useEditorStore((s) => s.setSentiment)
  const setEntites = useEditorStore((s) => s.setEntites)

  const handleSentiment = async () => {
    if (!texte.trim()) return
    try {
      const res = await analyserSentiment(texte)
      setSentiment(res.data.resultat)
    } catch (err) {
      console.error('Sentiment error:', err)
    }
  }

  const handleNER = async () => {
    if (!texte.trim()) return
    try {
      const res = await detecterEntites(texte)
      setEntites(res.data.entites || [])
    } catch (err) {
      console.error('NER error:', err)
    }
  }

  return (
    <div className="toolbar">
      <span className="toolbar-title">✍️ Mpanoratra Malagasy AI</span>
      <div className="toolbar-actions">
        <button className="toolbar-btn" onClick={handleSentiment} title="Analize sentiment">
          😊 Sentiment
        </button>
        <button className="toolbar-btn" onClick={handleNER} title="Detect entities">
          🏷️ NER
        </button>
      </div>
    </div>
  )
}
