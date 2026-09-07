/**
 * ECHO OS — Chat Panel
 * Main conversation interface with streaming and tool visualization.
 */

import { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Volume2, Loader2 } from 'lucide-react';
import { useChatStore, type Message } from '../stores/chat-store';
import { useVoiceStore } from '../stores/voice-store';

export default function ChatPanel() {
  const { messages, isLoading, isStreaming, sendMessage, streamMessage } = useChatStore();
  const { isListening, toggleListening } = useVoiceStore();
  const [input, setInput] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading || isStreaming) return;
    const msg = input;
    setInput('');
    await streamMessage(msg);
  };

  const renderMessage = (m: Message, i: number) => {
    const isUser = m.role === 'user';
    const isSystem = m.role === 'system';

    return (
      <div key={i} className="flex gap-2" style={{ justifyContent: isUser ? 'flex-end' : 'flex-start' }}>
        {!isUser && (
          <div className={`w-6 h-6 rounded flex-shrink-0 flex items-center justify-center text-[10px] mt-0.5 border ${
            isSystem
              ? 'bg-white/5 border-white/10 text-white/30'
              : 'border-echo-orange/30 text-echo-orange'
          }`} style={!isSystem ? { background: 'linear-gradient(135deg, rgba(255,94,0,0.3), rgba(255,215,0,0.3))' } : {}}>
            {isSystem ? '>' : 'E'}
          </div>
        )}
        <div className={`max-w-[75%] px-3.5 py-2.5 text-[13px] leading-relaxed ${
          isUser
            ? 'rounded-xl rounded-br-sm bg-echo-orange/10 border border-echo-orange/20 text-orange-200'
            : isSystem
              ? 'text-white/20 font-mono text-[10px] py-1 px-0'
              : 'rounded-xl rounded-bl-sm bg-white/[0.04] border border-echo-gold/10 text-white/80'
        }`}>
          {m.content}
          {m.isStreaming && <span className="inline-block w-1.5 h-4 bg-echo-orange/60 ml-0.5 animate-pulse" />}
          {m.toolResults && (
            <div className="mt-2 pt-2 border-t border-echo-gold/10">
              {m.toolResults.map((tr, j) => (
                <div key={j} className="text-[10px] font-mono text-echo-gold/60 mt-1">
                  ⚡ {tr.tool}: {tr.result?.status || 'done'}
                </div>
              ))}
            </div>
          )}
          {!isSystem && (
            <div className="text-[9px] text-white/15 mt-1 font-mono">{m.timestamp}</div>
          )}
        </div>
        {isUser && (
          <div className="w-6 h-6 rounded flex-shrink-0 flex items-center justify-center text-[10px] mt-0.5 bg-echo-orange/15 border border-echo-orange/25 text-echo-orange">
            U
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-2 echo-scrollbar">
        {messages.map(renderMessage)}
        {isLoading && !isStreaming && (
          <div className="flex gap-2 items-center">
            <div className="w-6 h-6 rounded flex-shrink-0 flex items-center justify-center border border-echo-orange/30" style={{ background: 'linear-gradient(135deg, rgba(255,94,0,0.3), rgba(255,215,0,0.3))' }}>
              <Loader2 size={10} className="animate-spin text-echo-orange" />
            </div>
            <div className="text-[12px] text-echo-orange/50 font-mono animate-pulse">Processing neural query...</div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input Bar */}
      <div className="px-6 py-3 bg-black/30 border-t border-echo-orange/[0.06] flex items-center gap-3">
        <button
          onClick={toggleListening}
          className={`w-10 h-10 rounded-full border-2 flex items-center justify-center cursor-pointer transition-all duration-300 flex-shrink-0 ${
            isListening
              ? 'border-echo-orange bg-echo-orange/15 text-echo-orange shadow-[0_0_16px_rgba(255,94,0,0.3)] animate-pulse'
              : 'border-white/10 bg-white/[0.03] text-white/40 hover:border-echo-orange/30'
          }`}
        >
          {isListening ? <Mic size={18} /> : <MicOff size={18} />}
        </button>

        <div className="flex-1 relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Enter command..."
            className="w-full bg-white/[0.03] border border-echo-orange/10 rounded-lg px-3.5 py-2.5 pr-12 text-[13px] text-white outline-none transition-colors focus:border-echo-orange/30 placeholder:text-white/20"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className={`absolute right-1 w-9 h-9 rounded-md flex items-center justify-center cursor-pointer transition-all ${
              input.trim() ? 'bg-echo-orange/20 text-echo-orange' : 'text-white/15'
            }`}
          >
            <Send size={16} />
          </button>
        </div>

        <button className="w-9 h-9 rounded-md border border-white/[0.06] bg-white/[0.02] text-white/30 flex items-center justify-center flex-shrink-0">
          <Volume2 size={14} />
        </button>
      </div>
    </div>
  );
}
