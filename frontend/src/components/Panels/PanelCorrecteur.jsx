import React from 'react'
import useEditorStore from '../../store/editorStore'

const RULE_LABELS = {
  FORBID_NB:       'Règle phonotactique',
  FORBID_MK:       'Règle phonotactique',
  FORBID_DT:       'Règle phonotactique',
  FORBID_BP:       'Règle phonotactique',
  FORBID_SZ:       'Règle phonotactique',
  FORBID_START_NK: 'Début de mot interdit',
  END_CONSONANT:   'Fin de mot invalide',
  DOUBLE_CONSONANT:'Gémination interdite',
  TRIPLE_CONSONANT:'Groupe consonantique',
}

export default function PanelCorrecteur() {
  const corrections = useEditorStore((s) => s.corrections)

  const applyFix = (original, suggestion) => {
    if (window.__quillInsertCorrection) {
      window.__quillInsertCorrection(original, suggestion)
    }
  }

  return (
    <div className="panel panel-correcteur">
      <div className="panel-header">
        <span className="panel-icon">✏️</span>
        <h3>Correcteur</h3>
        {corrections.length > 0 && (
          <span className="badge badge-error">{corrections.length}</span>
        )}
      </div>

      <div className="panel-body">
        {corrections.length === 0 ? (
          <div className="panel-empty">
            <span>✅</span>
            <p>Tsy misy hadisoana hita</p>
          </div>
        ) : (
          <ul className="correction-list">
            {corrections.map((err, i) => (
              <li key={i} className="correction-item">
                <div className="correction-top">
                  <span className="correction-word">❌ {err.mot}</span>
                  {err.erreur_phonotactique && (
                    <span className="correction-tag phono">
                      {RULE_LABELS[err.erreur_phonotactique] || 'Phonotactique'}
                    </span>
                  )}
                </div>

                {err.suggestions && err.suggestions.length > 0 && (
                  <div className="correction-suggestions">
                    <span className="correction-label">Suggestions :</span>
                    <div className="suggestion-chips">
                      {err.suggestions.map((s, j) => (
                        <button
                          key={j}
                          className="chip chip-suggestion"
                          onClick={() => applyFix(err.mot, s)}
                          title={`Remplacer par "${s}"`}
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {err.erreur_phonotactique && (
                  <div className="correction-phono-msg">
                    <small>Règle : {err.erreur_phonotactique}</small>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
