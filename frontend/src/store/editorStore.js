import { create } from 'zustand'

const useEditorStore = create((set) => ({
  texte: '',
  corrections: [],
  sentiment: null,
  entites: [],
  suggestions: [],
  audioUrl: null,
  audioLoading: false,
  setTexte: (texte) => set({ texte }),
  setCorrections: (corrections) => set({ corrections }),
  setSentiment: (sentiment) => set({ sentiment }),
  setEntites: (entites) => set({ entites }),
  setSuggestions: (suggestions) => set({ suggestions }),
  setAudioUrl: (audioUrl) => set({ audioUrl }),
  setAudioLoading: (audioLoading) => set({ audioLoading }),
}))

export default useEditorStore
