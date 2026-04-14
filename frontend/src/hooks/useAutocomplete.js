import { useState, useEffect, useRef } from 'react'
import { autocomplete } from '../services/api'

function debounce(fn, delay) {
  let timer
  return (...args) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
}

export default function useAutocomplete(word) {
  const [suggestions, setSuggestions] = useState([])
  const [loading, setLoading] = useState(false)
  const debouncedRef = useRef(null)

  useEffect(() => {
    if (!debouncedRef.current) {
      debouncedRef.current = debounce(async (w) => {
        if (!w || w.length < 2) {
          setSuggestions([])
          return
        }
        setLoading(true)
        try {
          const res = await autocomplete(w, 5)
          // suggestions can be array of strings or array of {word, probability}
          const raw = res.data.suggestions || []
          setSuggestions(raw)
        } catch {
          setSuggestions([])
        } finally {
          setLoading(false)
        }
      }, 350)
    }
    debouncedRef.current(word)
  }, [word])

  return { suggestions, loading }
}
