import axios from 'axios'

const API = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000' })

export const correcterMot    = (mot)    => API.post('/api/correct/mot', { mot })
export const correcterTexte  = (texte)  => API.post('/api/correct/texte', { texte })
export const lemmatiser      = (mot)    => API.post('/api/lemma', { mot })
export const autocomplete    = (mot, n) => API.post('/api/complete', { mot, n })
export const analyserSentiment = (texte) => API.post('/api/sentiment', { texte })
export const traduire        = (mot)    => API.post('/api/translate', { mot })
export const detecterEntites = (texte)  => API.post('/api/ner', { texte })
export const genererAudio    = (texte)  => API.post('/api/tts', { texte }, { responseType: 'blob' })
export const chatbot         = (message) => API.post('/api/chat', { message })
