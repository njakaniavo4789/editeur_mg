import React, { useState, useRef, useEffect } from 'react'
import { chatbot } from '../../services/api'
import useEditorStore from '../../store/editorStore'

export default function PanelChatbot() {
  const texte = useEditorStore((s) => s.texte)
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Salama! Mba hanampy anao aho. Manontania rehetra momba ny teny Malagasy.' },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (messageText) => {
    const msg = (messageText || input).trim()
    if (!msg) return

    setMessages((prev) => [...prev, { role: 'user', text: msg }])
    setInput('')
    setLoading(true)

    try {
      const res = await chatbot(msg)
      const botReply = res.data.reponse || res.data.message || res.data.response || '...'
      setMessages((prev) => [...prev, { role: 'bot', text: botReply }])
    } catch {
      setMessages((prev) => [...prev, { role: 'bot', text: '❌ Tsy nahomby ny fangatahana.' }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  const useEditorContext = () => {
    if (!texte.trim()) return
    setInput(`Momba ity lahatsoratra ity: "${texte.slice(0, 200)}"`)
  }

  return (
    <div className="panel panel-chatbot">
      <div className="panel-header">
        <span className="panel-icon">💬</span>
        <h3>Chatbot Malagasy</h3>
      </div>

      <div className="chatbot-messages">
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble ${m.role === 'user' ? 'chat-user' : 'chat-bot'}`}>
            {m.role === 'bot' && <span className="chat-avatar">🤖</span>}
            <span className="chat-text">{m.text}</span>
            {m.role === 'user' && <span className="chat-avatar">👤</span>}
          </div>
        ))}
        {loading && (
          <div className="chat-bubble chat-bot">
            <span className="chat-avatar">🤖</span>
            <span className="chat-text typing">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="chatbot-input-area">
        <button
          className="context-btn"
          onClick={useEditorContext}
          title="Utiliser le texte de l'éditeur"
        >
          📝
        </button>
        <textarea
          className="chatbot-input"
          rows={2}
          placeholder="Soraty ny hafatra..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button
          className="send-btn"
          onClick={() => send()}
          disabled={loading || !input.trim()}
        >
          ➤
        </button>
      </div>
    </div>
  )
}
