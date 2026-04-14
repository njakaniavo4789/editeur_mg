import React, { useRef } from 'react'
import useEditorStore from '../../store/editorStore'
import { analyserSentiment, detecterEntites, genererAudio } from '../../services/api'
import './Editor.css'

export default function Toolbar() {
  const texte = useEditorStore((s) => s.texte)
  const setSentiment = useEditorStore((s) => s.setSentiment)
  const setEntites = useEditorStore((s) => s.setEntites)
  const setAudioUrl = useEditorStore((s) => s.setAudioUrl)
  const setAudioLoading = useEditorStore((s) => s.setAudioLoading)
  const audioRef = useRef(null)

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

  const handleTTS = async () => {
    if (!texte.trim()) return
    setAudioLoading(true)

    // Stop previous audio
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }

    try {
      const res = await genererAudio(texte)
      const url = URL.createObjectURL(res.data)
      setAudioUrl(url)

      const audio = new Audio(url)
      audioRef.current = audio
      audio.play()
    } catch (err) {
      console.error('TTS error:', err)
    } finally {
      setAudioLoading(false)
    }
  }

  return (
    <div className="toolbar">
      <span className="toolbar-title">✍️ Mpanoratra Malagasy AI</span>
      <div className="toolbar-actions">
        <button className="toolbar-btn" onClick={handleTTS} title="Read aloud">
          🔊 Vakio
        </button>
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
