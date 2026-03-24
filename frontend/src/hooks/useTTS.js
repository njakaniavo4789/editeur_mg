import { useState, useRef } from 'react'
import { genererAudio } from '../services/api'

export default function useTTS() {
  const [audioUrl, setAudioUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const prevUrlRef = useRef(null)

  const generateAudio = async (text) => {
    if (!text || !text.trim()) return
    setLoading(true)
    setError(null)

    // revoke previous object URL to avoid memory leaks
    if (prevUrlRef.current) {
      URL.revokeObjectURL(prevUrlRef.current)
      prevUrlRef.current = null
    }

    try {
      const res = await genererAudio(text)
      const url = URL.createObjectURL(res.data)
      prevUrlRef.current = url
      setAudioUrl(url)
    } catch (err) {
      setError('Tsy afaka namokatra feo.')
      console.error('TTS error:', err)
    } finally {
      setLoading(false)
    }
  }

  return { audioUrl, loading, error, generateAudio }
}
