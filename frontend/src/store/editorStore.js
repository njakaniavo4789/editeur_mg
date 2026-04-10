import { create } from 'zustand'

const useEditorStore = create((set) => ({
  texte: '',
  corrections: [],
  sentiment: null,
  entites: [],
  suggestions: [],
  setTexte: (texte) => set({ texte }),
  setCorrections: (corrections) => set({ corrections }),
  setSentiment: (sentiment) => set({ sentiment }),
  setEntites: (entites) => set({ entites }),
  setSuggestions: (suggestions) => set({ suggestions }),
}))

export default useEditorStore
