import React, { useRef } from 'react'
import useEditorStore from '../../store/editorStore'
import useTTS from '../../hooks/useTTS'

export default function TTSPlayer() {
  const texte = useEditorStore((s) => s.texte)
  const { audioUrl, loading, error, generateAudio } = useTTS()
  const audioRef = useRef(null)

  const handleGenerate = async () => {
    await generateAudio(texte)
    // auto-play when ready
    setTimeout(() => {
      if (audioRef.current) audioRef.current.play()
    }, 100)
  }

  return (
    <div className="tts-player">
      <button
        className="tts-btn"
        onClick={handleGenerate}
        disabled={loading || !texte.trim()}
        title="Hamakatra ny lahatsoratra"
      >
        {loading ? '⏳' : '🔊'} {loading ? 'Eo ampelatanana...' : 'Vakio (TTS)'}
      </button>

      {error && <span className="tts-error">{error}</span>}

      {audioUrl && (
        <audio
          ref={audioRef}
          className="tts-audio"
          controls
          src={audioUrl}
          key={audioUrl}
        />
      )}
    </div>
  )
}
