import { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Send, Volume2 } from 'lucide-react';
import Sidebar from './components/Sidebar';
import HologramCanvas from './components/HologramCanvas';
import VoiceBar from './components/VoiceBar';

function App() {
  const [isListening, setIsListening] = useState(false);
  const [activeModule, setActiveModule] = useState('chat');
  const [messages, setMessages] = useState<{ role: string; content: string; time: string }[]>([
    { role: 'system', content: '// ECHO OS v1.0.0 initialized', time: getTime() },
    { role: 'assistant', content: 'Neural link established. All systems nominal. How can I assist you?', time: getTime() },
  ]);
  const [input, setInput] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  function getTime() {
    return new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' });
  }

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user', content: input, time: getTime() };
    const echoReply = {
      role: 'assistant',
      content: `Acknowledged. Processing request: "${input}". Analysis complete — mock response generated.`,
      time: getTime()
    };
    setMessages(prev => [...prev, userMsg, echoReply]);
    setInput('');
  };

  const hudCorner = (position: 'tl' | 'tr' | 'bl' | 'br') => {
    const size = 12;
    const borderStyle = '1.5px solid rgba(0, 153, 255, 0.4)';
    const styles: Record<string, React.CSSProperties> = {
      tl: { top: 0, left: 0, borderTop: borderStyle, borderLeft: borderStyle },
      tr: { top: 0, right: 0, borderTop: borderStyle, borderRight: borderStyle },
      bl: { bottom: 0, left: 0, borderBottom: borderStyle, borderLeft: borderStyle },
      br: { bottom: 0, right: 0, borderBottom: borderStyle, borderRight: borderStyle },
    };
    return (
      <div style={{
        position: 'absolute', width: `${size}px`, height: `${size}px`,
        ...styles[position]
      }} />
    );
  };

  return (
    <div style={{
      width: '100vw', height: '100vh', display: 'flex',
      background: '#0d1117', overflow: 'hidden',
      fontFamily: "'Segoe UI', system-ui, sans-serif",
      color: 'white'
    }}>
      {/* ─── LEFT SIDEBAR (30%) ─── */}
      <div style={{ width: '260px', flexShrink: 0, height: '100%' }}>
        <Sidebar activeModule={activeModule} onModuleSelect={setActiveModule} />
      </div>

      {/* ─── MAIN PANEL (70%) ─── */}
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column',
        height: '100%', position: 'relative',
        background: 'linear-gradient(180deg, #0d1117 0%, #0a0e15 100%)'
      }}>

        {/* ── Top Bar ── */}
        <div style={{
          padding: '12px 24px', display: 'flex', justifyContent: 'space-between',
          alignItems: 'center', borderBottom: '1px solid rgba(0,153,255,0.08)',
          background: 'rgba(0,0,0,0.2)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span style={{
              fontSize: '11px', letterSpacing: '3px', color: '#0099ff',
              fontFamily: "'Courier New', monospace", fontWeight: 700
            }}>
              {activeModule === 'chat' ? '◈ NEURAL CHAT' : `◈ ${activeModule.toUpperCase()}`}
            </span>
            <span style={{
              fontSize: '9px', padding: '2px 8px', borderRadius: '3px',
              background: 'rgba(0,255,136,0.1)', color: '#00ff88',
              border: '1px solid rgba(0,255,136,0.2)',
              letterSpacing: '1px'
            }}>ACTIVE</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span style={{
              fontSize: '9px', color: isListening ? '#ff0080' : 'rgba(255,255,255,0.3)',
              letterSpacing: '1.5px', fontFamily: "'Courier New', monospace",
              textShadow: isListening ? '0 0 6px rgba(255,0,128,0.5)' : 'none',
              transition: 'all 0.3s'
            }}>
              {isListening ? '● REC' : '○ IDLE'}
            </span>
            <span style={{
              fontSize: '9px', color: 'rgba(255,255,255,0.2)',
              fontFamily: "'Courier New', monospace", letterSpacing: '1px'
            }}>
              {new Date().toLocaleTimeString('en-US', { hour12: false })}
            </span>
          </div>
        </div>

        {/* ── Hologram HUD Area ── */}
        <div style={{
          height: '220px', position: 'relative', flexShrink: 0,
          borderBottom: '1px solid rgba(0,153,255,0.06)',
        }}>
          <HologramCanvas isSpeaking={isListening} />
          {/* HUD Corners */}
          <div style={{ position: 'absolute', inset: '12px', pointerEvents: 'none' }}>
            {hudCorner('tl')}
            {hudCorner('tr')}
            {hudCorner('bl')}
            {hudCorner('br')}
          </div>
          {/* Status overlay text */}
          <div style={{
            position: 'absolute', top: '16px', left: '20px',
            fontSize: '8px', color: 'rgba(0,153,255,0.4)',
            fontFamily: "'Courier New', monospace", letterSpacing: '1px'
          }}>
            HOLOGRAPHIC INTERFACE // ACTIVE
          </div>
          <div style={{
            position: 'absolute', bottom: '16px', right: '20px',
            fontSize: '8px', color: 'rgba(255,0,128,0.4)',
            fontFamily: "'Courier New', monospace", letterSpacing: '1px'
          }}>
            NEURAL PROC: {isListening ? '87%' : '12%'}
          </div>
        </div>

        {/* ── Chat Messages ── */}
        <div style={{
          flex: 1, overflowY: 'auto', padding: '16px 24px',
          display: 'flex', flexDirection: 'column', gap: '8px',
        }}>
          {messages.map((m, i) => (
            <div key={i} style={{
              display: 'flex',
              justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start',
              alignItems: 'flex-start', gap: '8px'
            }}>
              {m.role !== 'user' && (
                <div style={{
                  width: '24px', height: '24px', borderRadius: '4px', flexShrink: 0,
                  background: m.role === 'system'
                    ? 'rgba(255,255,255,0.05)'
                    : 'linear-gradient(135deg, rgba(0,153,255,0.3), rgba(255,0,128,0.3))',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '10px', marginTop: '2px',
                  border: '1px solid rgba(0,153,255,0.15)',
                }}>
                  {m.role === 'system' ? '>' : 'E'}
                </div>
              )}
              <div style={{
                maxWidth: '75%', padding: '10px 14px',
                borderRadius: m.role === 'user' ? '10px 10px 4px 10px' : '10px 10px 10px 4px',
                fontSize: '13px', lineHeight: '1.6',
                ...(m.role === 'user' ? {
                  background: 'rgba(0, 153, 255, 0.1)',
                  border: '1px solid rgba(0, 153, 255, 0.15)',
                  color: '#8ecfff',
                } : m.role === 'system' ? {
                  background: 'transparent',
                  border: 'none',
                  color: 'rgba(255,255,255,0.2)',
                  fontFamily: "'Courier New', monospace",
                  fontSize: '10px',
                  padding: '4px 0',
                } : {
                  background: 'rgba(255, 0, 128, 0.06)',
                  border: '1px solid rgba(255, 0, 128, 0.12)',
                  color: 'rgba(255,255,255,0.8)',
                })
              }}>
                {m.content}
                {m.role !== 'system' && (
                  <div style={{
                    fontSize: '9px', color: 'rgba(255,255,255,0.15)',
                    marginTop: '4px', fontFamily: "'Courier New', monospace"
                  }}>{m.time}</div>
                )}
              </div>
              {m.role === 'user' && (
                <div style={{
                  width: '24px', height: '24px', borderRadius: '4px', flexShrink: 0,
                  background: 'rgba(0,153,255,0.15)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '10px', marginTop: '2px',
                  border: '1px solid rgba(0,153,255,0.2)',
                  color: '#0099ff'
                }}>
                  U
                </div>
              )}
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        {/* ── Voice Waveform Bar ── */}
        <div style={{
          height: '40px', borderTop: '1px solid rgba(0,153,255,0.06)',
          borderBottom: '1px solid rgba(0,153,255,0.06)',
          background: 'rgba(0,0,0,0.3)',
        }}>
          <VoiceBar isActive={isListening} />
        </div>

        {/* ── Bottom Input Toolbar ── */}
        <div style={{
          padding: '12px 24px',
          background: 'rgba(0,0,0,0.3)',
          display: 'flex', alignItems: 'center', gap: '12px',
          borderTop: '1px solid rgba(0,153,255,0.06)'
        }}>
          {/* Mode toggles */}
          <button
            onClick={() => setIsListening(prev => !prev)}
            style={{
              width: '42px', height: '42px', borderRadius: '50%',
              border: `2px solid ${isListening ? '#ff0080' : 'rgba(255,255,255,0.1)'}`,
              background: isListening ? 'rgba(255,0,128,0.12)' : 'rgba(255,255,255,0.03)',
              color: isListening ? '#ff0080' : 'rgba(255,255,255,0.4)',
              cursor: 'pointer', transition: 'all 0.3s ease',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: isListening ? '0 0 16px rgba(255,0,128,0.3)' : 'none',
              animation: isListening ? 'micGlow 1.5s ease-in-out infinite' : 'none',
              flexShrink: 0,
            }}
          >
            {isListening ? <Mic size={18} /> : <MicOff size={18} />}
          </button>

          {/* Input field */}
          <div style={{
            flex: 1, position: 'relative', display: 'flex', alignItems: 'center',
          }}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Enter command..."
              style={{
                width: '100%',
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(0,153,255,0.1)',
                borderRadius: '8px',
                padding: '10px 48px 10px 14px',
                fontSize: '13px',
                color: 'white',
                outline: 'none',
                fontFamily: "'Segoe UI', sans-serif",
                transition: 'border-color 0.2s',
              }}
              onFocus={(e) => e.currentTarget.style.borderColor = 'rgba(0,153,255,0.3)'}
              onBlur={(e) => e.currentTarget.style.borderColor = 'rgba(0,153,255,0.1)'}
            />
            <button
              onClick={handleSend}
              style={{
                position: 'absolute', right: '4px',
                width: '36px', height: '36px',
                borderRadius: '6px', border: 'none',
                background: input.trim() ? 'rgba(0,153,255,0.2)' : 'transparent',
                color: input.trim() ? '#0099ff' : 'rgba(255,255,255,0.15)',
                cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                transition: 'all 0.2s',
              }}
            >
              <Send size={16} />
            </button>
          </div>

          {/* Extra controls */}
          <button style={{
            width: '36px', height: '36px', borderRadius: '6px',
            border: '1px solid rgba(255,255,255,0.06)',
            background: 'rgba(255,255,255,0.02)',
            color: 'rgba(255,255,255,0.3)',
            cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexShrink: 0,
          }}>
            <Volume2 size={14} />
          </button>
        </div>
      </div>

      {/* ─── Global Styles ─── */}
      <style>{`
        @keyframes micGlow {
          0%, 100% { box-shadow: 0 0 16px rgba(255,0,128,0.3); }
          50% { box-shadow: 0 0 24px rgba(255,0,128,0.5); }
        }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(0,153,255,0.15); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(0,153,255,0.3); }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { margin: 0; background: #0d1117; }
        ::placeholder { color: rgba(255,255,255,0.2); }
      `}</style>
    </div>
  );
}

export default App;
