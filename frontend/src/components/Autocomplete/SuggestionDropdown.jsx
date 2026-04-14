import React, { useEffect, useRef } from 'react'

export default function SuggestionDropdown({ suggestions, position, onSelect, onClose }) {
  const ref = useRef(null)

  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) {
        onClose()
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [onClose])

  if (!suggestions || suggestions.length === 0) return null

  return (
    <div
      ref={ref}
      className="suggestion-dropdown"
      style={{ top: position.top, left: position.left }}
    >
      {suggestions.map((item, i) => {
        // item can be string or {word, probability}
        const word = typeof item === 'string' ? item : item.word
        const prob = typeof item === 'object' && item.probability != null
          ? ` ${(item.probability * 100).toFixed(0)}%`
          : ''
        return (
          <div
            key={i}
            className="suggestion-item"
            onMouseDown={(e) => {
              e.preventDefault() // don't blur editor
              onSelect(word)
            }}
          >
            <span className="suggestion-word">{word}</span>
            {prob && <span className="suggestion-prob">{prob}</span>}
          </div>
        )
      })}
    </div>
  )
}
