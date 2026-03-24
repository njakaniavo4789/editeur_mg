import { useEffect, useRef } from 'react'
import useEditorStore from '../store/editorStore'
import { correcterTexte } from '../services/api'

function debounce(fn, delay) {
  let timer
  return (...args) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
}

export default function useCorrecteur() {
  const texte = useEditorStore((s) => s.texte)
  const setCorrections = useEditorStore((s) => s.setCorrections)
  const corrections = useEditorStore((s) => s.corrections)
  const debouncedRef = useRef(null)

  useEffect(() => {
    if (!debouncedRef.current) {
      debouncedRef.current = debounce(async (text) => {
        if (!text.trim()) {
          setCorrections([])
          return
        }
        try {
          const res = await correcterTexte(text)
          setCorrections(res.data.resultats || [])
        } catch (err) {
          console.error('Correction error:', err)
        }
      }, 900)
    }
    debouncedRef.current(texte)
  }, [texte, setCorrections])

  return { corrections }
}
