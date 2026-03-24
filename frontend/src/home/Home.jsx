import { useState, useEffect, useRef, useCallback } from "react";

// ─── Quill loader ─────────────────────────────────────────────────────────────
function useQuill(containerRef, dark) {
  const quillRef = useRef(null);
  const [ready, setReady] = useState(false);

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
        placeholder: "Start writing your story…",
        modules: { toolbar: "#ql-toolbar-custom" },
      });
      const saved = localStorage.getItem("scriptura_content");
      if (saved) quillRef.current.root.innerHTML = saved;
      setReady(true);
    };
    document.body.appendChild(script);
  }, []);

  const getText = useCallback(() => quillRef.current?.getText() || "", []);
  const reset   = useCallback(() => { if (quillRef.current) quillRef.current.setText(""); }, []);
  const save    = useCallback(() => {
    if (quillRef.current) localStorage.setItem("scriptura_content", quillRef.current.root.innerHTML);
  }, []);

  return { getText, reset, save, ready };
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
  sun:      "M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42M12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10z",
  close:    "M18 6 6 18M6 6l12 12",
  send:     "M22 2 11 13M22 2 15 22 11 13 2 9l20-7z",
  settings: "M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z",
  trash:    "M3 6h18M8 6V4h8v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6M10 11v6M14 11v6",
  publish:  "M22 2 11 13M22 2 15 22 11 13 2 9l20-7z",
  image:    "M21 15l-5-5L5 21M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 5h6M19 2v6",
};

const Ico = ({ n, s = 16, color }) => (
  <svg width={s} height={s} viewBox="0 0 24 24" fill="none"
    stroke={color || "currentColor"} strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
    <path d={ICONS[n]} />
  </svg>
);

// ─── Sentiment Modal ──────────────────────────────────────────────────────────
function SentimentModal({ getText, dark, onClose }) {
  const [phase, setPhase] = useState("loading");
  const [result, setResult] = useState(null);

  useEffect(() => {
    (async () => {
      const text = getText().trim();
      if (!text) {
        setResult({ error: "Nothing to analyze yet — write something first." });
        setPhase("done"); return;
      }
      try {
        const raw = await callClaude(
          [{ role: "user", content: `Analyze the sentiment of this text:\n"${text.slice(0, 3000)}"` }],
          `You are a sentiment analysis engine. Reply ONLY with valid JSON (no markdown):
{"label":"Positive"|"Negative"|"Neutral"|"Mixed","score":0.0-1.0,"emoji":"🟢"|"🔴"|"⚪"|"🟡","summary":"one sentence","highlights":["phrase1","phrase2","phrase3"]}`
        );
        setResult(JSON.parse(raw.replace(/```json|```/g, "").trim()));
      } catch { setResult({ error: "Analysis failed. Please try again." }); }
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
    <div style={{ position:"fixed", inset:0, zIndex:99, display:"flex", alignItems:"center", justifyContent:"center", padding:24, background:"rgba(0,0,0,0.55)", backdropFilter:"blur(10px)" }}>
      <div style={{ background: dark?"#0d1626":"#fff", border:`1px solid ${dark?"#1e2d42":"#e2e8f0"}`, borderRadius:22, padding:28, width:"100%", maxWidth:430, boxShadow:"0 40px 100px rgba(0,0,0,0.35)", animation:"modalIn .28s cubic-bezier(.34,1.56,.64,1)" }}>
        {/* Header */}
        <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:22 }}>
          <div style={{ display:"flex", alignItems:"center", gap:10 }}>
            <div style={{ width:34, height:34, borderRadius:10, background:"linear-gradient(135deg,#6366f1,#a78bfa)", display:"flex", alignItems:"center", justifyContent:"center" }}>
              <Ico n="smile" s={16} color="#fff" />
            </div>
            <span style={{ fontFamily:"'Playfair Display',serif", fontWeight:700, fontSize:16, color: dark?"#f1f5f9":"#0f172a" }}>Sentiment Analysis</span>
          </div>
          <button onClick={onClose} style={{ background: dark?"#1e293b":"#f1f5f9", border:"none", borderRadius:8, width:28, height:28, display:"flex", alignItems:"center", justifyContent:"center", cursor:"pointer", color: dark?"#94a3b8":"#64748b" }}>
            <Ico n="close" s={13} />
          </button>
        </div>

        {phase === "loading" && (
          <div style={{ display:"flex", flexDirection:"column", alignItems:"center", padding:"28px 0", gap:14 }}>
            <div style={{ width:38, height:38, borderRadius:"50%", border:"3px solid #6366f1", borderTopColor:"transparent", animation:"spin 0.75s linear infinite" }} />
            <p style={{ color:"#94a3b8", fontSize:13, fontFamily:"'DM Sans',sans-serif" }}>Analyzing your text…</p>
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
              <div style={{ height:5, borderRadius:99, background: dark?"#1e293b":"rgba(0,0,0,0.1)" }}>
                <div style={{ height:5, borderRadius:99, background:p.a, width:`${(result.score||0)*100}%`, transition:"width 0.8s ease" }} />
              </div>
            </div>
            <p style={{ fontSize:13, lineHeight:1.75, color: dark?"#94a3b8":"#64748b", fontFamily:"'Lora',serif" }}>{result.summary}</p>
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
function ChatbotPanel({ getText, dark, onClose }) {
  const [msgs, setMsgs] = useState([
    { role:"assistant", text:"Hi! I've read your document. Ask me anything — rewrite a section, brainstorm ideas, or check the tone." }
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
      setMsgs(p => [...p, { role:"assistant", text:"Oops — something went wrong. Try again." }]);
    }
    setBusy(false);
  };

  const bg   = dark ? "#0d1626" : "#ffffff";
  const surf = dark ? "#131f35" : "#f8fafc";
  const bord = dark ? "#1e2d42" : "#e2e8f0";
  const mute = dark ? "#475569" : "#94a3b8";
  const txt  = dark ? "#e2e8f0" : "#1e293b";

  return (
    <div style={{ display:"flex", flexDirection:"column", height:"100%", background:bg, borderLeft:`1px solid ${bord}`, animation:"slideIn .22s ease" }}>
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"14px 16px", borderBottom:`1px solid ${bord}`, flexShrink:0 }}>
        <div style={{ display:"flex", alignItems:"center", gap:9 }}>
          <div style={{ width:30, height:30, borderRadius:9, background:"linear-gradient(135deg,#06b6d4,#3b82f6)", display:"flex", alignItems:"center", justifyContent:"center" }}>
            <Ico n="bot" s={14} color="#fff" />
          </div>
          <div>
            <div style={{ fontWeight:700, fontSize:12.5, color:txt, fontFamily:"'Playfair Display',serif" }}>Writing Assistant</div>
            <div style={{ fontSize:10, color:mute }}>Powered by Claude</div>
          </div>
        </div>
        <button onClick={onClose} style={{ background:surf, border:`1px solid ${bord}`, borderRadius:7, width:26, height:26, display:"flex", alignItems:"center", justifyContent:"center", cursor:"pointer", color:mute }}>
          <Ico n="close" s={12} />
        </button>
      </div>

      <div style={{ flex:1, overflowY:"auto", padding:"14px 12px", display:"flex", flexDirection:"column", gap:9 }}>
        {msgs.map((m,i) => (
          <div key={i} style={{ display:"flex", justifyContent: m.role==="user"?"flex-end":"flex-start" }}>
            <div style={{
              maxWidth:"88%", padding:"9px 13px", fontSize:12.5, lineHeight:1.65, fontFamily:"'Lora',Georgia,serif",
              borderRadius: m.role==="user" ? "14px 14px 4px 14px" : "14px 14px 14px 4px",
              background: m.role==="user" ? "linear-gradient(135deg,#6366f1,#8b5cf6)" : surf,
              color: m.role==="user" ? "#fff" : txt,
              border: m.role==="user" ? "none" : `1px solid ${bord}`,
            }}>{m.text}</div>
          </div>
        ))}
        {busy && (
          <div style={{ display:"flex", gap:5, padding:"10px 12px", background:surf, borderRadius:"14px 14px 14px 4px", width:"fit-content", border:`1px solid ${bord}` }}>
            {[0,1,2].map(i => <div key={i} style={{ width:6, height:6, borderRadius:"50%", background:mute, animation:`bounce 0.9s ${i*0.2}s infinite` }} />)}
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div style={{ padding:"10px 12px", borderTop:`1px solid ${bord}`, flexShrink:0 }}>
        <div style={{ display:"flex", gap:8, alignItems:"flex-end", background:surf, border:`1px solid ${bord}`, borderRadius:12, padding:"8px 10px" }}>
          <textarea value={input} onChange={e=>setInput(e.target.value)}
            onKeyDown={e=>{ if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();send();} }}
            placeholder="Ask anything about your text…" rows={1}
            style={{ flex:1, background:"transparent", border:"none", outline:"none", resize:"none", fontSize:12.5, color:txt, fontFamily:"'Lora',Georgia,serif", lineHeight:1.5, minHeight:20, maxHeight:80 }} />
          <button onClick={send} disabled={!input.trim()||busy}
            style={{ width:28, height:28, borderRadius:8, background:"linear-gradient(135deg,#6366f1,#8b5cf6)", border:"none", display:"flex", alignItems:"center", justifyContent:"center", cursor:"pointer", opacity:(!input.trim()||busy)?0.4:1, transition:"opacity .2s", flexShrink:0 }}>
            <Ico n="send" s={12} color="#fff" />
          </button>
        </div>
        <p style={{ fontSize:10, color:mute, textAlign:"center", marginTop:6, fontFamily:"'DM Sans',sans-serif" }}>Enter to send · Shift+Enter for new line</p>
      </div>
    </div>
  );
}

// ─── Settings Panel ───────────────────────────────────────────────────────────
function SettingsPanel({ dark, onClose, docTitle, setDocTitle, author }) {
  const bg   = dark ? "#0d1626" : "#f8fafc";
  const bord = dark ? "#1e2d42" : "#e2e8f0";
  const txt  = dark ? "#e2e8f0" : "#1e293b";
  const mute = dark ? "#475569" : "#94a3b8";

  const Field = ({ label, value, editable, onChange }) => (
    <div style={{ marginBottom:14 }}>
      <div style={{ fontSize:10, fontWeight:700, letterSpacing:"0.08em", color:mute, textTransform:"uppercase", marginBottom:5, fontFamily:"'DM Sans',sans-serif" }}>{label}</div>
      {editable ? (
        <input value={value} onChange={e=>onChange(e.target.value)}
          style={{ width:"100%", background: dark?"#0f172a":"#fff", border:`1px solid ${bord}`, borderRadius:8, padding:"7px 10px", fontSize:12.5, color:txt, outline:"none", fontFamily:"'DM Sans',sans-serif", boxSizing:"border-box" }} />
      ) : (
        <div style={{ background: dark?"#0f172a":"#fff", border:`1px solid ${bord}`, borderRadius:8, padding:"7px 10px", fontSize:12.5, color:mute }}>{value}</div>
      )}
    </div>
  );

  return (
    <div style={{ display:"flex", flexDirection:"column", height:"100%", background:bg, borderLeft:`1px solid ${bord}`, animation:"slideIn .22s ease" }}>
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"14px 16px", borderBottom:`1px solid ${bord}`, flexShrink:0 }}>
        <div style={{ display:"flex", alignItems:"center", gap:9 }}>
          <div style={{ width:30, height:30, borderRadius:9, background:"linear-gradient(135deg,#f59e0b,#f97316)", display:"flex", alignItems:"center", justifyContent:"center" }}>
            <Ico n="settings" s={14} color="#fff" />
          </div>
          <span style={{ fontWeight:700, fontSize:13, color:txt, fontFamily:"'Playfair Display',serif" }}>Document Settings</span>
        </div>
        <button onClick={onClose} style={{ background: dark?"#1e293b":"#f1f5f9", border:"none", borderRadius:7, width:26, height:26, display:"flex", alignItems:"center", justifyContent:"center", cursor:"pointer", color:mute }}>
          <Ico n="close" s={12} />
        </button>
      </div>
      <div style={{ flex:1, overflowY:"auto", padding:18 }}>
        <p style={{ fontSize:10, fontWeight:700, letterSpacing:"0.08em", color:mute, textTransform:"uppercase", marginBottom:12 }}>URL & Author Settings</p>
        <Field label="Document Title" value={docTitle} editable onChange={setDocTitle} />
        <Field label="URL Friendly Title" value={docTitle.toLowerCase().replace(/\s+/g,"-").replace(/[^a-z0-9-]/g,"")} />
        <Field label="Author" value={author} />
        <Field label="Loading Settings" value="Lazy Load" />

        <div style={{ marginTop:20 }}>
          <p style={{ fontSize:10, fontWeight:700, letterSpacing:"0.08em", color:mute, textTransform:"uppercase", marginBottom:12 }}>Image Settings</p>
          <div style={{ background: dark?"#0f172a":"#fff", border:`1px solid ${bord}`, borderRadius:10, overflow:"hidden" }}>
            <div style={{ height:100, background:"linear-gradient(135deg,#1e3a5f,#2d6a9f)", display:"flex", alignItems:"center", justifyContent:"center" }}>
              <Ico n="image" s={30} color="rgba(255,255,255,0.3)" />
            </div>
            <div style={{ padding:"8px 10px" }}>
              <button style={{ fontSize:11, color:"#6366f1", background:"none", border:"none", cursor:"pointer", fontWeight:600 }}>Edit Cover Image</button>
            </div>
          </div>
          <div style={{ marginTop:10 }}>
            <div style={{ fontSize:10, fontWeight:700, letterSpacing:"0.08em", color:mute, textTransform:"uppercase", marginBottom:5 }}>Image Alt Text</div>
            <input placeholder="Placeholder Text" style={{ width:"100%", background: dark?"#0f172a":"#fff", border:`1px solid ${bord}`, borderRadius:8, padding:"7px 10px", fontSize:12.5, color:txt, outline:"none", fontFamily:"'DM Sans',sans-serif", boxSizing:"border-box" }} />
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Left Sidebar ─────────────────────────────────────────────────────────────
function Sidebar({ dark, active, setActive, onSave, onReset, saved, docTitle, setDocTitle, author, toggleDark, onPublish }) {
  const [editTitle, setEditTitle] = useState(false);

  const bg   = dark ? "#080e1c" : "#f8fafc";
  const bord = dark ? "#16243a" : "#e8edf5";
  const mute = dark ? "#3d5068" : "#94a3b8";
  const txt  = dark ? "#dde4f0" : "#1e293b";
  const surf = dark ? "#0d1828" : "#fff";

  const NAV = [
    { id:"sentiment", icon:"smile",    label:"Sentiment Analysis", color:"#8b5cf6" },
    { id:"chatbot",   icon:"bot",      label:"AI Chatbot",         color:"#06b6d4" },
    { id:"settings",  icon:"settings", label:"Document Settings",  color:"#f59e0b" },
  ];

  return (
    <div style={{ width:230, flexShrink:0, height:"100%", display:"flex", flexDirection:"column", background:bg, borderRight:`1px solid ${bord}` }}>
      {/* Brand logo */}
      <div style={{ padding:"18px 16px 14px" }}>
        <div style={{ display:"flex", alignItems:"center", gap:10 }}>
          <div style={{ width:36, height:36, borderRadius:11, background:"linear-gradient(140deg,#4f46e5,#7c3aed)", display:"flex", alignItems:"center", justifyContent:"center", flexShrink:0, boxShadow:"0 4px 14px rgba(99,102,241,0.4)" }}>
            <Ico n="pen" s={17} color="#fff" />
          </div>
          <div>
            <div style={{ fontFamily:"'Playfair Display',serif", fontWeight:700, fontSize:17, color: dark?"#f0f4ff":"#0f172a", letterSpacing:"-0.3px" }}>Scriptura</div>
            <div style={{ fontSize:10, color:mute, fontFamily:"'DM Sans',sans-serif" }}>Editor v2.0</div>
          </div>
        </div>
      </div>

      {/* Document card */}
      <div style={{ padding:"0 12px 14px", borderBottom:`1px solid ${bord}` }}>
        <div style={{ background:surf, borderRadius:13, padding:"12px 13px", border:`1px solid ${bord}`, boxShadow: dark?"none":"0 1px 6px rgba(0,0,0,0.05)" }}>
          <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:10 }}>
            <div style={{ width:30, height:30, borderRadius:"50%", background:"linear-gradient(135deg,#f59e0b,#ef4444)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:12, fontWeight:700, color:"#fff", flexShrink:0 }}>
              {author[0].toUpperCase()}
            </div>
            <div>
              <div style={{ fontSize:11.5, fontWeight:600, color:txt, fontFamily:"'DM Sans',sans-serif" }}>{author}</div>
              <div style={{ fontSize:10, color:mute }}>Published 2d ago</div>
            </div>
          </div>
          {/* Editable title */}
          {editTitle ? (
            <input autoFocus value={docTitle} onChange={e=>setDocTitle(e.target.value)}
              onBlur={()=>setEditTitle(false)} onKeyDown={e=>e.key==="Enter"&&setEditTitle(false)}
              style={{ width:"100%", fontSize:12, fontWeight:600, color:txt, background:"transparent", border:"none", borderBottom:"1.5px solid #6366f1", outline:"none", fontFamily:"'DM Sans',sans-serif", padding:"2px 0", boxSizing:"border-box" }} />
          ) : (
            <div onClick={()=>setEditTitle(true)} style={{ fontSize:12, fontWeight:600, color:txt, cursor:"text", lineHeight:1.4, display:"flex", alignItems:"flex-start", gap:4 }}>
              <span style={{ flex:1 }}>{docTitle}</span>
              <span style={{ fontSize:9, color:mute, paddingTop:1, flexShrink:0 }}>✏️</span>
            </div>
          )}
          {/* Saved dot */}
          <div style={{ display:"flex", alignItems:"center", gap:5, marginTop:9 }}>
            <div style={{ width:5, height:5, borderRadius:"50%", background:saved?"#10b981":(dark?"#2a3f58":"#cbd5e1"), transition:"background .4s" }} />
            <span style={{ fontSize:10, color:saved?"#10b981":mute, transition:"color .4s", fontFamily:"'DM Sans',sans-serif" }}>
              {saved ? "Saved" : "Unsaved changes"}
            </span>
          </div>
        </div>
      </div>

      {/* Nav tools */}
      <div style={{ padding:"12px 8px 8px" }}>
        <p style={{ fontSize:9, fontWeight:700, letterSpacing:"0.1em", color:mute, padding:"0 8px", marginBottom:6, textTransform:"uppercase", fontFamily:"'DM Sans',sans-serif" }}>AI Tools</p>
        {NAV.map(({ id, icon, label, color }) => {
          const isActive = active === id;
          return (
            <button key={id} onClick={()=>setActive(isActive?null:id)}
              style={{
                display:"flex", alignItems:"center", gap:10, width:"100%", padding:"9px 10px",
                borderRadius:10, border:"none", cursor:"pointer",
                background: isActive ? `${color}18` : "transparent",
                color: isActive ? color : mute,
                fontFamily:"'DM Sans',sans-serif", fontSize:12.5, fontWeight: isActive?600:400,
                transition:"all .15s", textAlign:"left",
              }}
              onMouseEnter={e=>{ if(!isActive){e.currentTarget.style.background=`${color}10`; e.currentTarget.style.color=color;} }}
              onMouseLeave={e=>{ if(!isActive){e.currentTarget.style.background="transparent"; e.currentTarget.style.color=mute;} }}>
              <Ico n={icon} s={15} />
              <span style={{ flex:1 }}>{label}</span>
              {isActive && <div style={{ width:5, height:5, borderRadius:"50%", background:color, flexShrink:0 }} />}
            </button>
          );
        })}
      </div>

      <div style={{ flex:1 }} />

      {/* Bottom actions */}
      <div style={{ padding:"10px 8px 18px", borderTop:`1px solid ${bord}`, display:"flex", flexDirection:"column", gap:4 }}>
        <button onClick={onSave}
          style={{ display:"flex", alignItems:"center", gap:9, width:"100%", padding:"8px 10px", borderRadius:10, border:`1px solid ${bord}`, cursor:"pointer", background:"transparent", color:mute, fontSize:12, fontFamily:"'DM Sans',sans-serif", transition:"all .15s" }}
          onMouseEnter={e=>{e.currentTarget.style.background=surf; e.currentTarget.style.color=txt;}}
          onMouseLeave={e=>{e.currentTarget.style.background="transparent"; e.currentTarget.style.color=mute;}}>
          <Ico n="save" s={14} /> Save draft
          <span style={{ marginLeft:"auto", fontSize:10, opacity:.6 }}>⌘S</span>
        </button>

        <button onClick={toggleDark}
          style={{ display:"flex", alignItems:"center", gap:9, width:"100%", padding:"8px 10px", borderRadius:10, border:`1px solid ${bord}`, cursor:"pointer", background:"transparent", color:mute, fontSize:12, fontFamily:"'DM Sans',sans-serif", transition:"all .15s" }}
          onMouseEnter={e=>{e.currentTarget.style.background=surf; e.currentTarget.style.color=txt;}}
          onMouseLeave={e=>{e.currentTarget.style.background="transparent"; e.currentTarget.style.color=mute;}}>
          <Ico n={dark?"sun":"moon"} s={14} /> {dark?"Light mode":"Dark mode"}
        </button>

        <button onClick={onPublish}
          style={{ display:"flex", alignItems:"center", justifyContent:"center", gap:7, width:"100%", padding:"10px 14px", borderRadius:11, border:"none", cursor:"pointer", background:"linear-gradient(135deg,#3b82f6,#1d4ed8)", color:"#fff", fontSize:12.5, fontWeight:700, fontFamily:"'DM Sans',sans-serif", boxShadow:"0 4px 16px rgba(59,130,246,0.4)", marginTop:4, transition:"all .2s" }}
          onMouseEnter={e=>e.currentTarget.style.boxShadow="0 6px 20px rgba(59,130,246,0.55)"}
          onMouseLeave={e=>e.currentTarget.style.boxShadow="0 4px 16px rgba(59,130,246,0.4)"}>
          <Ico n="publish" s={13} color="#fff" /> Publish
        </button>

        <button onClick={onReset}
          style={{ display:"flex", alignItems:"center", justifyContent:"center", gap:7, width:"100%", padding:"7px", borderRadius:9, border:"none", cursor:"pointer", background:"transparent", color:"rgba(244,63,94,0.35)", fontSize:11, fontFamily:"'DM Sans',sans-serif", transition:"all .15s", marginTop:2 }}
          onMouseEnter={e=>{e.currentTarget.style.color="#f43f5e"; e.currentTarget.style.background="rgba(244,63,94,0.07)";}}
          onMouseLeave={e=>{e.currentTarget.style.color="rgba(244,63,94,0.35)"; e.currentTarget.style.background="transparent";}}>
          <Ico n="trash" s={12} /> Reset document
        </button>
      </div>
    </div>
  );
}

// ─── Quill Toolbar ────────────────────────────────────────────────────────────
function EditorToolbar({ dark }) {
  const bg   = dark ? "#0b1525" : "#ffffff";
  const bord = dark ? "#16243a" : "#f0f4f8";
  return (
    <div id="ql-toolbar-custom" style={{ background:bg, borderBottom:`1px solid ${bord}`, padding:"7px 20px", display:"flex", flexWrap:"wrap", gap:2, alignItems:"center", flexShrink:0 }}>
      <select className="ql-header" defaultValue="">
        <option value="1">H1</option><option value="2">H2</option><option value="3">H3</option><option value="">¶</option>
      </select>
      <span className="ql-formats">
        <button className="ql-bold"/><button className="ql-italic"/><button className="ql-underline"/><button className="ql-strike"/>
      </span>
      <span className="ql-formats">
        <button className="ql-list" value="ordered"/><button className="ql-list" value="bullet"/>
      </span>
      <span className="ql-formats">
        <button className="ql-link"/><button className="ql-blockquote"/><button className="ql-code-block"/>
      </span>
      <span className="ql-formats"><button className="ql-clean"/></span>
    </div>
  );
}

// ─── App Root ─────────────────────────────────────────────────────────────────
export default function App() {
  const [dark, setDark]         = useState(false);
  const [active, setActive]     = useState(null);
  const [saved, setSaved]       = useState(false);
  const [docTitle, setDocTitle] = useState("Legend Of X_AE_A-22, Part 2");
  const [author]                = useState("X_AE_B-221");
  const quillRef                = useRef(null);
  const { getText, reset, save } = useQuill(quillRef, dark);

  const handleSave = useCallback(() => {
    save(); setSaved(true); setTimeout(() => setSaved(false), 2500);
  }, [save]);

  const handleReset = () => {
    if (confirm("Reset the document? This cannot be undone.")) reset();
  };

  // Ctrl/Cmd+S shortcut
  useEffect(() => {
    const fn = e => { if ((e.ctrlKey||e.metaKey) && e.key==="s") { e.preventDefault(); handleSave(); } };
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
      .ql-toolbar{background:${dark?"#0b1525":"#fff"}!important;}
      .ql-container{font-family:'Lora',Georgia,serif!important;font-size:17.5px!important;line-height:1.9!important;background:${dark?"#07111f":"#fff"}!important;}
      .ql-editor{padding:44px 56px 80px!important;max-width:820px!important;color:${dark?"#dde4f0":"#1e293b"}!important;animation:fadeUp .35s ease;}
      .ql-editor.ql-blank::before{color:${dark?"#2a3f58":"#c8d3e0"}!important;font-style:italic;left:56px!important;}
      .ql-editor h1{font-family:'Playfair Display',serif!important;font-size:2.3em!important;line-height:1.2!important;color:${dark?"#f0f4ff":"#0f172a"}!important;margin-bottom:.5em!important;letter-spacing:-0.5px!important;}
      .ql-editor h2{font-family:'Playfair Display',serif!important;font-size:1.65em!important;color:${dark?"#e2e8f0":"#1e293b"}!important;margin-bottom:.35em!important;}
      .ql-editor h3{font-family:'Playfair Display',serif!important;color:${dark?"#94a3b8":"#475569"}!important;margin-bottom:.25em!important;}
      .ql-editor p{margin-bottom:1em!important;}
      .ql-editor a{color:#6366f1!important;text-decoration:underline!important;text-underline-offset:2px!important;}
      .ql-editor blockquote{border-left:3px solid #6366f1!important;padding-left:18px!important;color:${dark?"#94a3b8":"#64748b"}!important;font-style:italic!important;margin:1em 0!important;}
      .ql-snow .ql-stroke{stroke:${dark?"#3d5068":"#94a3b8"}!important;}
      .ql-snow .ql-fill{fill:${dark?"#3d5068":"#94a3b8"}!important;}
      .ql-snow button:hover .ql-stroke,.ql-snow button.ql-active .ql-stroke{stroke:#6366f1!important;}
      .ql-snow button:hover .ql-fill,.ql-snow button.ql-active .ql-fill{fill:#6366f1!important;}
      .ql-snow .ql-picker-label{color:${dark?"#3d5068":"#94a3b8"}!important;}
      .ql-snow .ql-picker-options{background:${dark?"#0d1828":"#fff"}!important;border-color:${dark?"#1e2d42":"#e2e8f0"}!important;border-radius:9px!important;box-shadow:0 8px 24px rgba(0,0,0,0.15)!important;}
      ::-webkit-scrollbar{width:4px;height:4px;}
      ::-webkit-scrollbar-track{background:transparent;}
      ::-webkit-scrollbar-thumb{background:${dark?"#1e2d42":"#e2e8f0"};border-radius:99px;}
    `;
    document.head.appendChild(s);
    return () => s.remove();
  }, [dark]);

  const editorBg = dark ? "#07111f" : "#ffffff";
  const panelW   = active === "settings" ? 270 : 300;

  return (
    <div style={{ display:"flex", height:"100vh", overflow:"hidden", fontFamily:"'DM Sans',sans-serif" }}>

      {/* LEFT SIDEBAR — all controls here */}
      <Sidebar
        dark={dark}
        active={active}
        setActive={setActive}
        onSave={handleSave}
        onReset={handleReset}
        saved={saved}
        docTitle={docTitle}
        setDocTitle={setDocTitle}
        author={author}
        toggleDark={() => setDark(d => !d)}
        onPublish={() => alert("🚀 Your post has been published!")}
      />

      {/* MAIN EDITOR — no top bar */}
      <div style={{ flex:1, display:"flex", flexDirection:"column", overflow:"hidden", background:editorBg }}>
        <EditorToolbar dark={dark} />
        <div style={{ flex:1, overflowY:"auto" }}>
          <div ref={quillRef} style={{ minHeight:"100%" }} />
        </div>
      </div>

      {/* RIGHT PANELS */}
      {active === "chatbot" && (
        <div style={{ width:panelW, flexShrink:0 }}>
          <ChatbotPanel getText={getText} dark={dark} onClose={()=>setActive(null)} />
        </div>
      )}

      {active === "settings" && (
        <div style={{ width:panelW, flexShrink:0 }}>
          <SettingsPanel dark={dark} onClose={()=>setActive(null)} docTitle={docTitle} setDocTitle={setDocTitle} author={author} />
        </div>
      )}

      {/* SENTIMENT MODAL */}
      {active === "sentiment" && (
        <SentimentModal getText={getText} dark={dark} onClose={()=>setActive(null)} />
      )}
    </div>
  );
}