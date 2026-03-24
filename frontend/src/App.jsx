import React from 'react'
import EditorCore from './components/Editor/EditorCore'
import PanelCorrecteur from './components/Panels/PanelCorrecteur'
import PanelSentiment from './components/Panels/PanelSentiment'
import PanelNER from './components/Panels/PanelNER'
import PanelChatbot from './components/Panels/PanelChatbot'
import TTSPlayer from './components/TTS/TTSPlayer'
import './index.css'

function App() {
  return (
    <div className="app-container">
      <header>
        <h1>Mpanoratra Malagasy AI</h1>
      </header>
      <div className="main-layout">
        <div className="editor-section">
          <Toolbar />
          <EditorCore />
          <TTSPlayer />
        </div>
        <div className="panels-section">
          <PanelCorrecteur />
          <PanelSentiment />
          <PanelNER />
          <PanelChatbot />
        </div>
      </div>
    </div>
  )
}

export default App
