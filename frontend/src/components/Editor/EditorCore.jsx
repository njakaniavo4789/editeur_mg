import React, { useEffect, useRef, useState, useCallback } from 'react'
import Quill from 'quill'
import 'quill/dist/quill.snow.css'
import useEditorStore from '../../store/editorStore'
import useCorrecteur from '../../hooks/useCorrecteur'
import useAutocomplete from '../../hooks/useAutocomplete'
import SuggestionDropdown from '../Autocomplete/SuggestionDropdown'
import RightClickMenu from '../ContextMenu/RightClickMenu'
import './Editor.css'

function debounce(fn, delay) {
  let timer
  return (...args) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
}

export default function EditorCore() {
  const editorRef = useRef(null)
  const quillRef = useRef(null)
  const setTexte = useEditorStore((s) => s.setTexte)

  const [lastWord, setLastWord] = useState('')
  const [dropdownPos, setDropdownPos] = useState({ top: 0, left: 0 })
  const [contextMenu, setContextMenu] = useState(null)
  const [selectedText, setSelectedText] = useState('')

  // hooks
  useCorrecteur()
  const { suggestions } = useAutocomplete(lastWord)

  useEffect(() => {
    if (quillRef.current) return

    const quill = new Quill(editorRef.current, {
      theme: 'snow',
      placeholder: 'Soraty eto ny lahatsoratra Malagasy...',
      modules: { toolbar: false },
    })
    quillRef.current = quill

    const debouncedSetText = debounce((text) => setTexte(text), 500)

    quill.on('text-change', (delta, oldDelta, source) => {
      if (source !== 'user') return

      const text = quill.getText()
      debouncedSetText(text)

      // Extract last word for autocomplete
      const sel = quill.getSelection()
      if (sel) {
        const textBefore = quill.getText(0, sel.index)
        const parts = textBefore.split(/[\s\n]+/)
        const word = parts[parts.length - 1]
        setLastWord(word)

        if (word.length >= 2) {
          const bounds = quill.getBounds(sel.index)
          const editorRect = editorRef.current.getBoundingClientRect()
          setDropdownPos({
            top: bounds.top + bounds.height + 4,
            left: bounds.left,
          })
        }
      }
    })

    // Close dropdown on click inside editor
    quill.root.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') setLastWord('')
    })

    return () => {
      // Cleanup is minimal; Quill doesn't have a destroy method in v2
    }
  }, [setTexte])

  const handleInsertSuggestion = useCallback((word) => {
    const quill = quillRef.current
    if (!quill) return
    const sel = quill.getSelection()
    if (!sel) return
    const textBefore = quill.getText(0, sel.index)
    const parts = textBefore.split(/[\s\n]+/)
    const lastW = parts[parts.length - 1]
    const deleteFrom = sel.index - lastW.length
    quill.deleteText(deleteFrom, lastW.length)
    quill.insertText(deleteFrom, word + ' ')
    quill.setSelection(deleteFrom + word.length + 1)
    setLastWord('')
  }, [])

  const handleContextMenu = useCallback((e) => {
    e.preventDefault()
    const quill = quillRef.current
    if (!quill) return
    const sel = quill.getSelection()
    const text = (sel && sel.length > 0) ? quill.getText(sel.index, sel.length) : ''
    setSelectedText(text)
    setContextMenu({ x: e.clientX, y: e.clientY })
  }, [])

  const closeContextMenu = useCallback(() => setContextMenu(null), [])

  const getFullText = useCallback(() => {
    return quillRef.current ? quillRef.current.getText() : ''
  }, [])

  const insertCorrectedWord = useCallback((original, corrected) => {
    const quill = quillRef.current
    if (!quill) return
    const text = quill.getText()
    const idx = text.indexOf(original)
    if (idx >= 0) {
      quill.deleteText(idx, original.length)
      quill.insertText(idx, corrected)
    }
  }, [])

  // expose insertCorrectedWord globally so panels can call it
  useEffect(() => {
    window.__quillInsertCorrection = insertCorrectedWord
    return () => { delete window.__quillInsertCorrection }
  }, [insertCorrectedWord])

  return (
    <div
      className="editor-core"
      onContextMenu={handleContextMenu}
      onClick={closeContextMenu}
    >
      <div ref={editorRef} className="quill-container" />

      {suggestions.length > 0 && lastWord.length >= 2 && (
        <SuggestionDropdown
          suggestions={suggestions}
          position={dropdownPos}
          onSelect={handleInsertSuggestion}
          onClose={() => setLastWord('')}
        />
      )}

      {contextMenu && (
        <RightClickMenu
          x={contextMenu.x}
          y={contextMenu.y}
          selectedText={selectedText}
          getFullText={getFullText}
          onClose={closeContextMenu}
        />
      )}
    </div>
  )
}
