import { useState, useEffect, useRef, useCallback } from "react";

// ─── Quill loader ─────────────────────────────────────────────────────────────
function useQuill(containerRef) {
  const quillRef = useRef(null);
  const [ready, setReady] = useState(false);
  const [isWriting, setIsWriting] = useState(false);

  useEffect(() => {
    if (quillRef.current) return;
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "https://cdnjs.cloudflare.com/ajax/libs/quill/1.3.7/quill.snow.min.css";
    document.head.appendChild(link);
    const script = document.createElement("script");
    script.src = "https://cdnjs.cloudflare.com/ajax/libs/quill/1.3.7/quill.min.js";
    script.onload = () => {
      if (!containerRef.current) return;
      quillRef.current = new window.Quill(containerRef.current, {
        theme: "snow",
        placeholder: "Andehana manoratra eto...",
        modules: { toolbar: "#ql-toolbar-custom" },
      });
      const saved = localStorage.getItem("scriptura_content");
      if (saved) quillRef.current.root.innerHTML = saved;

      // Écouter les changements dans l'éditeur
      quillRef.current.on('text-change', () => {
        setIsWriting(true);
      });

      setReady(true);
    };
    document.body.appendChild(script);
  }, []);

  const getText = useCallback(() => quillRef.current?.getText() || "", []);
  const reset = useCallback(() => { if (quillRef.current) quillRef.current.setText(""); }, []);
  const save = useCallback(() => {
    if (quillRef.current) localStorage.setItem("scriptura_content", quillRef.current.root.innerHTML);
  }, []);

  return { getText, reset, save, ready, isWriting, setIsWriting };
}

// ─── Claude API ───────────────────────────────────────────────────────────────
async function callClaude(messages, system = "") {
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model: "claude-sonnet-4-20250514", max_tokens: 1000, system, messages }),
  });
  const d = await res.json();
  return d.content?.map(b => b.text || "").join("") || "";
}

// ─── SVG Icons ────────────────────────────────────────────────────────────────
const ICONS = {
  pen:      "M12 20h9M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z",
  save:     "M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2zM17 21v-8H7v8M7 3v5h8",
  smile:    "M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10zM8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01",
  bot:      "M12 8V5m0 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM3 14a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-5zM8 17h.01M16 17h.01",
  moon:     "M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z",
  close:    "M18 6 6 18M6 6l12 12",
  send:     "M22 2 11 13M22 2 15 22 11 13 2 9l20-7z",
  trash:    "M3 6h18M8 6V4h8v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6M10 11v6M14 11v6",
  publish:  "M22 2 11 13M22 2 15 22 11 13 2 9l20-7z",
  image:    "M21 15l-5-5L5 21M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 5h6M19 2v6",
  mic:      "M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3zM19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8M12 16a4 4 0 1 1 0 8 4 4 0 0 1 0-8z",
  book:     "M12 20h9M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z",
  lightbulb: "M15 14c.2-1 .2-2 0-3-.2-1-.6-1.8-1-2.5C13.2 7.2 12 7 12 7s-1.2.2-1.2.2H9c-.6 0-1-.2-1-.6 0-.4.2-.6.6-.8.3-.2.7-.4 1.2-.4h2.2c.5 0 .9.2 1.2.4.4.2.6.4.6.8 0 .4-.2.6-.6.8H11c-.2 0-.4.2-.4.6 0 .4.2.6.4.8h2.6c.2 0 .4-.2.4-.6 0-.4-.2-.6-.4-.8h-1c-.1 0-.3.1-.4.2-.1.1-.2.3-.2.6 0 .3.1.5.2.6.1.1.3.2.6.2.3 0 .5-.1.7-.4.4-.3.7-.7.7-1.3 0-.2-.1-.4-.3-.5-.6-.1-.2-.1-.4-.2-.6-.1-.3-.1-.5-.2-.7-.1-.4-.1-.6-.2-.8-.1-.3-.1-.5-.2-.7-.1-.4-.1-.6-.2-.8-.1",
  star:     "M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z",
  translate: "M3 5h12M3 12h18M3 19h12M12 2a2 2 0 0 1 2 2 2 2 0 0 1-2 2H7a2 2 0 0 1-2-2 2 2 0 0 1 2-2h5zm7 15H7a2 2 0 0 1-2-2 2 2 0 0 1 2-2h5zm7-8H7a2 2 0 0 1-2-2 2 2 0 0 1 2-2h12a2 2 0 0 1 2 2 2 2 0 0 1-2 2z",
};

const Ico = ({ n, s = 16, color }) => (
  <svg width={s} height={s} viewBox="0 0 24 24" fill="none"
    stroke={color || "currentColor"} strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
    <path d={ICONS[n]} />
  </svg>
);

// ─── Synthèse Vocale Panel ────────────────────────────────────────────────────────────
function SyntheseVocalePanel({ onClose }) {
  const [isListening, setIsListening] = useState(false);
  const [text, setText] = useState("");

  const startListening = () => {
    setIsListening(true);
    setText("Mandeha ny fanoratra feo...");
    // Logique de reconnaissance vocale à implémenter ici
  };

  const stopListening = () => {
    setIsListening(false);
    setText("Feo voatahiry.");
  };

  return (
    <div style={{ display:"flex", flexDirection:"column", height:"100%", background:"#0d1626", borderLeft:`1px solid #1e2d42`, animation:"slideIn .22s ease" }}>
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"14px 16px", borderBottom:`1px solid #1e2d42`, flexShrink:0 }}>
        <div style={{ display:"flex", alignItems:"center", gap:9 }}>
          <div style={{ width:30, height:30, borderRadius:9, background:"linear-gradient(135deg,#f59e0b,#f97316)", display:"flex", alignItems:"center", justifyContent:"center" }}>
            <Ico n="mic" s={14} color="#fff" />
          </div>
          <span style={{ fontWeight:700, fontSize:13, color:"#e2e8f0", fontFamily:"'Playfair Display',serif" }}>Fanoratra Feo</span>
        </div>
        <button onClick={onClose} style={{ background:"#131f35", border:"none", borderRadius:7, width:26, height:26, display:"flex", alignItems:"center", justifyContent:"center", cursor:"pointer", color:"#94a3b8" }}>
          <Ico n="close" s={12} />
        </button>
      </div>
      <div style={{ flex:1, padding:20, display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", gap:20 }}>
        <button
          onClick={isListening ? stopListening : startListening}
          style={{
            width:120, height:120, borderRadius:"50%", border:"none", cursor:"pointer",
            background: isListening ? "#f43f5e" : "linear-gradient(135deg,#3b82f6,#1d4ed8)",
            display:"flex", alignItems:"center", justifyContent:"center", boxShadow:"0 8px 24px rgba(0,0,0,0.2)",
            transition:"all .2s"
          }}
          onMouseEnter={e=>e.currentTarget.style.transform="scale(1.05)"}
          onMouseLeave={e=>e.currentTarget.style.transform="scale(1)"}
        >
          <Ico n="mic" s={32} color="#fff" />
        </button>
        <p style={{ color:"#94a3b8", fontSize:12, textAlign:"center", fontFamily:"'DM Sans',sans-serif" }}>
          {isListening ? "Mandeha ny fanoratra feo..." : "Tsindrio mba handeha ny fanoratra feo"}
        </p>
        {text && (
          <div style={{ background:"#131f35", borderRadius:12, padding:16, width:"100%", maxWidth:300 }}>
            <p style={{ color:"#e2e8f0", fontSize:13, fontFamily:"'Lora',serif" }}>{text}</p>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Sentiment Modal ──────────────────────────────────────────────────────────
function SentimentModal({ getText, onClose }) {
  const [phase, setPhase] = useState("loading");
  const [result, setResult] = useState(null);

  useEffect(() => {
    (async () => {
      const text = getText().trim();
      if (!text) {
        setResult({ error: "Tsy misy afaka anoritsoritana — soraty azafady." });
        setPhase("done"); return;
      }
      try {
        const raw = await callClaude(
          [{ role: "user", content: `Analyze the sentiment of this text:\n"${text.slice(0, 3000)}"` }],
          `You are a sentiment analysis engine. Reply ONLY with valid JSON (no markdown):
{"label":"Positive"|"Negative"|"Neutral"|"Mixed","score":0.0-1.0,"emoji":"🟢"|"🔴"|"⚪"|"🟡","summary":"one sentence","highlights":["phrase1","phrase2","phrase3"]}`
        );
        setResult(JSON.parse(raw.replace(/```json|```/g, "").trim()));
      } catch { setResult({ error: "Nisy olana ny fanadihana. Avereno indray." }); }
      setPhase("done");
    })();
  }, []);

  const PAL = {
    Positive: { a: "#10b981", bg: "rgba(16,185,129,0.1)"  },
    Negative: { a: "#f43f5e", bg: "rgba(244,63,94,0.1)"   },
    Neutral:  { a: "#94a3b8", bg: "rgba(148,163,184,0.1)" },
    Mixed:    { a: "#f59e0b", bg: "rgba(245,158,11,0.1)"  },
  };
  const p = result?.label ? PAL[result.label] : PAL.Neutral;

  return (
    <div style={{ position:"fixed", inset:0, zIndex:99, display:"flex", alignItems:"center", justifyContent:"center", padding:24, background:"rgba(0,0,0,0.75)", backdropFilter:"blur(12px)" }}>
      <div style={{ background: "#0d1626", border:`1px solid #1e2d42`, borderRadius:22, padding:28, width:"100%", maxWidth:430, boxShadow:"0 40px 100px rgba(0,0,0,0.45)", animation:"modalIn .28s cubic-bezier(.34,1.56,.64,1)" }}>
        <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:22 }}>
          <div style={{ display:"flex", alignItems:"center", gap:10 }}>
            <div style={{ width:34, height:34, borderRadius:10, background:"linear-gradient(135deg,#6366f1,#a78bfa)", display:"flex", alignItems:"center", justifyContent:"center" }}>
              <Ico n="smile" s={16} color="#fff" />
            </div>
            <span style={{ fontFamily:"'Playfair Display',serif", fontWeight:700, fontSize:16, color: "#f1f5f9" }}>Toetran-dahatsoratra</span>
          </div>
          <button onClick={onClose} style={{ background: "#1e293b", border:"none", borderRadius:8, width:28, height:28, display:"flex", alignItems:"center", justifyContent:"center", cursor:"pointer", color: "#94a3b8" }}>
            <Ico n="close" s={13} />
          </button>
        </div>

        {phase === "loading" && (
          <div style={{ display:"flex", flexDirection:"column", alignItems:"center", padding:"28px 0", gap:14 }}>
            <div style={{ width:38, height:38, borderRadius:"50%", border:"3px solid #6366f1", borderTopColor:"transparent", animation:"spin 0.75s linear infinite" }} />
            <p style={{ color:"#94a3b8", fontSize:13, fontFamily:"'DM Sans',sans-serif" }}>Fanadihana...</p>
          </div>
        )}

        {phase === "done" && result?.error && (
          <p style={{ color:"#f43f5e", fontSize:13, textAlign:"center", padding:"20px 0" }}>{result.error}</p>
        )}

        {phase === "done" && !result?.error && (
          <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
            <div style={{ background:p.bg, borderRadius:14, padding:"16px 18px", border:`1px solid ${p.a}30` }}>
              <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:10 }}>
                <div style={{ display:"flex", alignItems:"center", gap:8 }}>
                  <span style={{ fontSize:24 }}>{result.emoji}</span>
                  <span style={{ fontWeight:700, fontSize:20, color:p.a, fontFamily:"'Playfair Display',serif" }}>{result.label}</span>
                </div>
                <span style={{ fontWeight:800, fontSize:16, color:p.a }}>{Math.round((result.score||0)*100)}%</span>
              </div>
              <div style={{ height:5, borderRadius:99, background:"#1e293b" }}>
                <div style={{ height:5, borderRadius:99, background:p.a, width:`${(result.score||0)*100}%`, transition:"width 0.8s ease" }} />
              </div>
            </div>
            <p style={{ fontSize:13, lineHeight:1.75, color: "#94a3b8", fontFamily:"'Lora',serif" }}>{result.summary}</p>
            {result.highlights?.length > 0 && (
              <div style={{ display:"flex", flexWrap:"wrap", gap:6 }}>
                {result.highlights.map((h,i)=>(
                  <span key={i} style={{ padding:"3px 10px", borderRadius:99, fontSize:11, fontWeight:600, background:p.bg, color:p.a, border:`1px solid ${p.a}35`, fontFamily:"'DM Sans',sans-serif" }}>"{h}"</span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Chatbot Panel ────────────────────────────────────────────────────────────
function ChatbotPanel({ getText, onClose }) {
  const [msgs, setMsgs] = useState([
    { role:"assistant", text:"Salama! Nahita ny lahatsoratrao. Azafady mifanitsy amiko — ovay ny antokony, manolotra hevitra, na jereo ny tonony." }
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const endRef = useRef(null);
  useEffect(() => endRef.current?.scrollIntoView({ behavior:"smooth" }), [msgs]);

  const send = async () => {
    const q = input.trim();
    if (!q || busy) return;
    const doc = getText().trim().slice(0, 3000);
    const next = [...msgs, { role:"user", text:q }];
    setMsgs(next); setInput(""); setBusy(true);
    try {
      const reply = await callClaude(
        next.map(m => ({ role: m.role === "assistant" ? "assistant" : "user", content: m.text })),
        `You are a writing assistant. The user's document:\n\n---\n${doc}\n---\nBe concise, helpful and creative.`
      );
      setMsgs(p => [...p, { role:"assistant", text:reply }]);
    } catch {
      setMsgs(p => [...p, { role:"assistant", text:"Nisy olana. Avereno indray azafady." }]);
    }
    setBusy(false);
  };

  return (
    <div style={{ display:"flex", flexDirection:"column", height:"100%", background:"#0d1626", borderLeft:`1px solid #1e2d42`, animation:"slideIn .22s ease" }}>
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"14px 16px", borderBottom:`1px solid #1e2d42`, flexShrink:0 }}>
        <div style={{ display:"flex", alignItems:"center", gap:9 }}>
          <div style={{ width:30, height:30, borderRadius:9, background:"linear-gradient(135deg,#06b6d4,#3b82f6)", display:"flex", alignItems:"center", justifyContent:"center" }}>
            <Ico n="bot" s={14} color="#fff" />
          </div>
          <div>
            <div style={{ fontWeight:700, fontSize:12.5, color:"#e2e8f0", fontFamily:"'Playfair Display',serif" }}>Mpanolotsaina avo</div>
            <div style={{ fontSize:10, color:"#94a3b8" }}>Tamin'ny Claude</div>
          </div>
        </div>
        <button onClick={onClose} style={{ background:"#131f35", border:`1px solid #1e2d42`, borderRadius:7, width:26, height:26, display:"flex", alignItems:"center", justifyContent:"center", cursor:"pointer", color:"#94a3b8" }}>
          <Ico n="close" s={12} />
        </button>
      </div>

      <div style={{ flex:1, overflowY:"auto", padding:"14px 12px", display:"flex", flexDirection:"column", gap:9 }}>
        {msgs.map((m,i) => (
          <div key={i} style={{ display:"flex", justifyContent: m.role==="user"?"flex-end":"flex-start" }}>
            <div style={{
              maxWidth:"88%", padding:"9px 13px", fontSize:12.5, lineHeight:1.65, fontFamily:"'Lora',Georgia,serif",
              borderRadius: m.role==="user" ? "14px 14px 4px 14px" : "14px 14px 14px 4px",
              background: m.role==="user" ? "linear-gradient(135deg,#6366f1,#8b5cf6)" : "#131f35",
              color: m.role==="user" ? "#fff" : "#e2e8f0",
              border: m.role==="user" ? "none" : `1px solid #1e2d42`,
            }}>{m.text}</div>
          </div>
        ))}
        {busy && (
          <div style={{ display:"flex", gap:5, padding:"10px 12px", background:"#131f35", borderRadius:"14px 14px 14px 4px", width:"fit-content", border:`1px solid #1e2d42` }}>
            {[0,1,2].map(i => <div key={i} style={{ width:6, height:6, borderRadius:"50%", background:"#475569", animation:`bounce 0.9s ${i*0.2}s infinite` }} />)}
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div style={{ padding:"10px 12px", borderTop:`1px solid #1e2d42`, flexShrink:0 }}>
        <div style={{ display:"flex", gap:8, alignItems:"flex-end", background:"#131f35", border:`1px solid #1e2d42`, borderRadius:12, padding:"8px 10px" }}>
          <textarea value={input} onChange={e=>setInput(e.target.value)}
            onKeyDown={e=>{ if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();send();} }}
            placeholder="Mifanitsy amiko momba ny lahatsoratrao..." rows={1}
            style={{ flex:1, background:"transparent", border:"none", outline:"none", resize:"none", fontSize:12.5, color:"#e2e8f0", fontFamily:"'Lora',Georgia,serif", lineHeight:1.5, minHeight:20, maxHeight:80 }} />
          <button onClick={send} disabled={!input.trim()||busy}
            style={{ width:28, height:28, borderRadius:8, background:"linear-gradient(135deg,#6366f1,#8b5cf6)", border:"none", display:"flex", alignItems:"center", justifyContent:"center", cursor:"pointer", opacity:(!input.trim()||busy)?0.4:1, transition:"opacity .2s", flexShrink:0 }}>
            <Ico n="send" s={12} color="#fff" />
          </button>
        </div>
        <p style={{ fontSize:10, color:"#94a3b8", textAlign:"center", marginTop:6, fontFamily:"'DM Sans',sans-serif" }}>Enter hanalefa · Shift+Enter hanoratra vaovao</p>
      </div>
    </div>
  );
}

// ─── Suggestions Panel ────────────────────────────────────────────────────────────
function SuggestionsPanel({ getText, isWriting }) {
  const [suggestions, setSuggestions] = useState([
    { word: "fahitana", definition: "Fahitana dia zava azo jerena amin'ny maso, na azo fantarina amin'ny saina." },
    { word: "fahafahana", definition: "Toetra na hery azo ampiasaina hanatanteraka zava iray." },
    { word: "fahatsiarovana", definition: "Fahatsiarovana na fahafantarana indray zava efa nisy taloha." },
    { word: "fahasembana", definition: "Toetra manondro ny fahafaham-po na ny fahafinaretana." },
    { word: "fahamendrehana", definition: "Fahamendrehana dia toetra manondro ny fahafahana manao zava tsara sy marina." },
    { word: "fahazavana", definition: "Fahazavana dia toetra manondro ny fahafinaretana na ny fahasahiana." },
  ]);

  // Mise à jour dynamique des suggestions en fonction du texte
  useEffect(() => {
    const text = getText().toLowerCase();
    if (text.includes("fahitana")) {
      setSuggestions(prev => prev.map(s =>
        s.word === "fahitana" ? { ...s, definition: "Fahitana dia zava azo fantarina amin'ny alalan'ny maso na ny saina." } : s
      ));
    }
  }, [getText]);

  if (!isWriting) return null;

  return (
    <div style={{
      width: 280,
      background: "#080e1c",
      borderLeft: `1px solid #16243a`,
      padding: "16px 12px",
      display: "flex",
      flexDirection: "column",
      height: "100vh",
      overflowY: "auto",
    }}>
      <div style={{ padding: "0 8px 16px", borderBottom: `1px solid #16243a`, marginBottom: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Ico n="lightbulb" s={18} color="#f59e0b" />
          <span style={{ fontWeight: 600, fontSize: 14, color: "#dde4f0", fontFamily: "'Playfair Display',serif" }}>Fanoratra Fanampiana</span>
        </div>
        <p style={{ fontSize: 10, color: "#64748b", marginTop: 4, fontFamily: "'DM Sans',sans-serif" }}>Teny sy hevitra hanampy anao</p>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {suggestions.map((suggestion, index) => (
          <div
            key={index}
            style={{
              background: "#0d1626",
              borderRadius: 10,
              padding: 12,
              border: `1px solid #1e2d42`,
              transition: "all 0.2s ease",
              cursor: "pointer",
              display: "flex",
              flexDirection: "column",
              gap: 4,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.2)";
              e.currentTarget.style.borderColor = "#3b82f6";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.boxShadow = "none";
              e.currentTarget.style.borderColor = "#1e2d42";
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Ico n="star" s={14} color="#f59e0b" />
              <span style={{ fontWeight: 500, color: "#dde4f0", fontSize: 13, fontFamily: "'DM Sans',sans-serif" }}>{suggestion.word}</span>
            </div>
            <p style={{ fontSize: 11, color: "#94a3b8", marginLeft: 22, fontFamily: "'Lora',serif", lineHeight: 1.5 }}>{suggestion.definition}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Left Sidebar ─────────────────────────────────────────────────────────────
function Sidebar({ active, setActive, onSave, onReset, saved, docTitle, setDocTitle, author, onPublish }) {
  const [editTitle, setEditTitle] = useState(false);

  const bg = "#080e1c";
  const bord = "#16243a";
  const mute = "#3d5068";
  const txt = "#dde4f0";
  const surf = "#0d1828";

  const NAV = [
    { id: "sentiment", icon: "smile", label: "Toetran-dahatsoratra", color: "#8b5cf6" },
    { id: "chatbot", icon: "bot", label: "Mpanolo-tsaina", color: "#06b6d4" },
    { id: "synthese", icon: "mic", label: "Famakian-teny", color: "#f59e0b" },
  ];

  return (
    <div style={{ width: 230, flexShrink: 0, height: "100%", display: "flex", flexDirection: "column", background: bg, borderRight: `1px solid ${bord}` }}>
      {/* Brand logo */}
      <div style={{ padding: "18px 16px 14px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 36, height: 36, borderRadius: 11, background: "linear-gradient(140deg,#4f46e5,#7c3aed)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, boxShadow: "0 4px 14px rgba(99,102,241,0.4)" }}>
            <Ico n="pen" s={17} color="#fff" />
          </div>
          <div>
            <div style={{ fontFamily: "'Playfair Display',serif", fontWeight: 700, fontSize: 17, color: "#f0f4ff", letterSpacing: "-0.3px" }}>Scriptura</div>
            <div style={{ fontSize: 10, color: mute, fontFamily: "'DM Sans',sans-serif" }}>Éditeur v2.1</div>
          </div>
        </div>
      </div>

      {/* Document card */}
      <div style={{ padding: "0 12px 14px", borderBottom: `1px solid ${bord}` }}>
        <div style={{ background: surf, borderRadius: 13, padding: "12px 13px", border: `1px solid ${bord}`, boxShadow: "none" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <div style={{ width: 30, height: 30, borderRadius: "50%", background: "linear-gradient(135deg,#f59e0b,#ef4444)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 700, color: "#fff", flexShrink: 0 }}>
              {author[0].toUpperCase()}
            </div>
            <div>
              <div style={{ fontSize: 11.5, fontWeight: 600, color: txt, fontFamily: "'DM Sans',sans-serif" }}>{author}</div>
              <div style={{ fontSize: 10, color: mute }}>Nohavaozina taloha</div>
            </div>
          </div>
          {/* Editable title */}
          {editTitle ? (
            <input autoFocus value={docTitle} onChange={e => setDocTitle(e.target.value)}
              onBlur={() => setEditTitle(false)} onKeyDown={e => e.key === "Enter" && setEditTitle(false)}
              style={{ width: "100%", fontSize: 12, fontWeight: 600, color: txt, background: "transparent", border: "none", borderBottom: "1.5px solid #6366f1", outline: "none", fontFamily: "'DM Sans',sans-serif", padding: "2px 0", boxSizing: "border-box" }} />
          ) : (
            <div onClick={() => setEditTitle(true)} style={{ fontSize: 12, fontWeight: 600, color: txt, cursor: "text", lineHeight: 1.4, display: "flex", alignItems: "flex-start", gap: 4 }}>
              <span style={{ flex: 1 }}>{docTitle}</span>
              <span style={{ fontSize: 9, color: mute, paddingTop: 1, flexShrink: 0 }}>✏️</span>
            </div>
          )}
          {/* Saved dot */}
          <div style={{ display: "flex", alignItems: "center", gap: 5, marginTop: 9 }}>
            <div style={{ width: 5, height: 5, borderRadius: "50%", background: saved ? "#10b981" : "#2a3f58", transition: "background .4s" }} />
            <span style={{ fontSize: 10, color: saved ? "#10b981" : mute, transition: "color .4s", fontFamily: "'DM Sans',sans-serif" }}>
              {saved ? "Voatahiry" : "Tsy voatahiry"}
            </span>
          </div>
        </div>
      </div>

      {/* Nav tools */}
      <div style={{ padding: "12px 8px 8px" }}>
        <p style={{ fontSize: 9, fontWeight: 700, letterSpacing: "0.1em", color: mute, padding: "0 8px", marginBottom: 6, textTransform: "uppercase", fontFamily: "'DM Sans',sans-serif" }}>Fitaovana IA</p>
        {NAV.map(({ id, icon, label, color }) => {
          const isActive = active === id;
          return (
            <button key={id} onClick={() => setActive(isActive ? null : id)}
              style={{
                display: "flex", alignItems: "center", gap: 10, width: "100%", padding: "9px 10px",
                borderRadius: 10, border: "none", cursor: "pointer",
                background: isActive ? `${color}18` : "transparent",
                color: isActive ? color : mute,
                fontFamily: "'DM Sans',sans-serif", fontSize: 12.5, fontWeight: isActive ? 600 : 400,
                transition: "all .15s", textAlign: "left",
              }}
              onMouseEnter={e => { if (!isActive) { e.currentTarget.style.background = `${color}10`; e.currentTarget.style.color = color; } }}
              onMouseLeave={e => { if (!isActive) { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = mute; } }}>
              <Ico n={icon} s={15} />
              <span style={{ flex: 1 }}>{label}</span>
              {isActive && <div style={{ width: 5, height: 5, borderRadius: "50%", background: color, flexShrink: 0 }} />}
            </button>
          );
        })}
      </div>

      <div style={{ flex: 1 }} />

      {/* Bottom actions */}
      <div style={{ padding: "10px 8px 18px", borderTop: `1px solid ${bord}`, display: "flex", flexDirection: "column", gap: 4 }}>
        <button onClick={onSave}
          style={{ display: "flex", alignItems: "center", gap: 9, width: "100%", padding: "8px 10px", borderRadius: 10, border: `1px solid ${bord}`, cursor: "pointer", background: "transparent", color: mute, fontSize: 12, fontFamily: "'DM Sans',sans-serif", transition: "all .15s" }}
          onMouseEnter={e => { e.currentTarget.style.background = surf; e.currentTarget.style.color = txt; }}
          onMouseLeave={e => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = mute; }}>
          <Ico n="save" s={14} /> Hitahiry
          <span style={{ marginLeft: "auto", fontSize: 10, opacity: .6 }}>⌘S</span>
        </button>

        <button onClick={onPublish}
          style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 7, width: "100%", padding: "10px 14px", borderRadius: 11, border: "none", cursor: "pointer", background: "linear-gradient(135deg,#3b82f6,#1d4ed8)", color: "#fff", fontSize: 12.5, fontWeight: 700, fontFamily: "'DM Sans',sans-serif", boxShadow: "0 4px 16px rgba(59,130,246,0.4)", marginTop: 4, transition: "all .2s" }}
          onMouseEnter={e => e.currentTarget.style.boxShadow = "0 6px 20px rgba(59,130,246,0.55)"}
          onMouseLeave={e => e.currentTarget.style.boxShadow = "0 4px 16px rgba(59,130,246,0.4)"}>
          <Ico n="publish" s={13} color="#fff" /> Hizara
        </button>
      </div>
    </div>
  );
}

// ─── Quill Toolbar ────────────────────────────────────────────────────────────
function EditorToolbar() {
  return (
    <div id="ql-toolbar-custom" style={{ background: "#0b1525", borderBottom: `1px solid #16243a`, padding: "7px 20px", display: "flex", flexWrap: "wrap", gap: 2, alignItems: "center", flexShrink: 0 }}>
      <select className="ql-header" defaultValue="">
        <option value="1">Lohateny 1</option><option value="2">Lohateny 2</option><option value="3">Lohateny 3</option><option value="">Teny</option>
      </select>
      <span className="ql-formats">
        <button className="ql-bold" /><button className="ql-italic" /><button className="ql-underline" /><button className="ql-strike" />
      </span>
      <span className="ql-formats">
        <button className="ql-list" value="ordered" /><button className="ql-list" value="bullet" />
      </span>
      <span className="ql-formats">
        <button className="ql-link" /><button className="ql-blockquote" /><button className="ql-code-block" />
      </span>
      <span className="ql-formats"><button className="ql-clean" /></span>
    </div>
  );
}

// ─── App Root ─────────────────────────────────────────────────────────────────
export default function App() {
  const [active, setActive] = useState(null);
  const [saved, setSaved] = useState(false);
  const [docTitle, setDocTitle] = useState("Tantaran'ny X_AE_A-22, Loharano 2");
  const [author] = useState("X_AE_B-221");
  const quillRef = useRef(null);
  const { getText, reset, save, isWriting, setIsWriting } = useQuill(quillRef);

  const handleSave = useCallback(() => {
    save(); setSaved(true); setTimeout(() => setSaved(false), 2500);
  }, [save]);

  const handleReset = () => {
    if (confirm("Hanafoana ny lahatsoratra ve? Tsy azo averina intsony izany.")) reset();
  };

  // Ctrl/Cmd+S shortcut
  useEffect(() => {
    const fn = e => { if ((e.ctrlKey || e.metaKey) && e.key === "s") { e.preventDefault(); handleSave(); } };
    window.addEventListener("keydown", fn);
    return () => window.removeEventListener("keydown", fn);
  }, [handleSave]);

  // Global styles
  useEffect(() => {
    const s = document.createElement("style");
    s.textContent = `
      @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Lora:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@400;500;600;700&display=swap');
      *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
      @keyframes spin    {to{transform:rotate(360deg)}}
      @keyframes bounce  {0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
      @keyframes modalIn {from{opacity:0;transform:scale(0.93) translateY(12px)}to{opacity:1;transform:scale(1) translateY(0)}}
      @keyframes slideIn {from{opacity:0;transform:translateX(16px)}to{opacity:1;transform:translateX(0)}}
      @keyframes fadeUp  {from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
      .ql-toolbar.ql-snow{border:none!important;}
      .ql-container.ql-snow{border:none!important;}
      .ql-toolbar{background:#0b1525!important;}
      .ql-container{font-family:'Lora',Georgia,serif!important;font-size:17.5px!important;line-height:1.9!important;background:#07111f!important;}
      .ql-editor{padding:44px 56px 80px!important;max-width:820px!important;color:#dde4f0!important;animation:fadeUp .35s ease;}
      .ql-editor.ql-blank::before{color:#2a3f58!important;font-style:italic;left:56px!important;}
      .ql-editor h1{font-family:'Playfair Display',serif!important;font-size:2.3em!important;line-height:1.2!important;color:#f0f4ff!important;margin-bottom:.5em!important;letter-spacing:-0.5px!important;}
      .ql-editor h2{font-family:'Playfair Display',serif!important;font-size:1.65em!important;color:#e2e8f0!important;margin-bottom:.35em!important;}
      .ql-editor h3{font-family:'Playfair Display',serif!important;color:#94a3b8!important;margin-bottom:.25em!important;}
      .ql-editor p{margin-bottom:1em!important;}
      .ql-editor a{color:#6366f1!important;text-decoration:underline!important;text-underline-offset:2px!important;}
      .ql-editor blockquote{border-left:3px solid #6366f1!important;padding-left:18px!important;color:#94a3b8!important;font-style:italic!important;margin:1em 0!important;}
      .ql-snow .ql-stroke{stroke:#3d5068!important;}
      .ql-snow .ql-fill{fill:#3d5068!important;}
      .ql-snow button:hover .ql-stroke,.ql-snow button.ql-active .ql-stroke{stroke:#6366f1!important;}
      .ql-snow button:hover .ql-fill,.ql-snow button.ql-active .ql-fill{fill:#6366f1!important;}
      .ql-snow .ql-picker-label{color:#3d5068!important;}
      .ql-snow .ql-picker-options{background:#0d1828!important;border-color:#1e2d42!important;border-radius:9px!important;box-shadow:0 8px 24px rgba(0,0,0,0.25)!important;}
      ::-webkit-scrollbar{width:4px;height:4px;}
      ::-webkit-scrollbar-track{background:transparent;}
      ::-webkit-scrollbar-thumb{background:#1e2d42;border-radius:99px;}
    `;
    document.head.appendChild(s);
    return () => s.remove();
  }, []);

  return (
    <div style={{ display: "flex", height: "100vh", overflow: "hidden", fontFamily: "'DM Sans',sans-serif" }}>

      {/* LEFT SIDEBAR */}
      <Sidebar
        active={active}
        setActive={setActive}
        onSave={handleSave}
        onReset={handleReset}
        saved={saved}
        docTitle={docTitle}
        setDocTitle={setDocTitle}
        author={author}
        onPublish={() => alert("🚀 Namerina ny lahatsoratrao!")}
      />

      {/* MAIN EDITOR */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden", background: "#07111f" }}>
        <EditorToolbar />
        <div style={{ flex: 1, overflowY: "auto" }}>
          <div ref={quillRef} style={{ minHeight: "100%" }} />
        </div>
      </div>

      {/* SUGGESTIONS PANEL (only when writing) */}
      {isWriting && <SuggestionsPanel getText={getText} isWriting={isWriting} />}

      {/* RIGHT PANELS */}
      {active === "chatbot" && (
        <div style={{ width: 300, flexShrink: 0 }}>
          <ChatbotPanel getText={getText} onClose={() => setActive(null)} />
        </div>
      )}

      {active === "synthese" && (
        <div style={{ width: 300, flexShrink: 0 }}>
          <SyntheseVocalePanel onClose={() => setActive(null)} />
        </div>
      )}

      {/* SENTIMENT MODAL */}
      {active === "sentiment" && (
        <SentimentModal getText={getText} onClose={() => setActive(null)} />
      )}
    </div>
  );
}