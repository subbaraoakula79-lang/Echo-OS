/**
 * ECHO OS — Main Application
 * Root layout with sidebar, hologram HUD, and module-based content.
 */

import { useEffect } from 'react';
import { useAppStore, type ModuleId } from './stores/app-store';
import { useVoiceStore } from './stores/voice-store';
import { electron, isElectron } from './lib/electron-bridge';
import Sidebar from './components/Sidebar';
import HologramCanvas from './components/HologramCanvas';
import VoiceBar from './components/VoiceBar';
import ChatPanel from './components/ChatPanel';
import TaskPanel from './components/TaskPanel';
import {
  SearchPanel, EmailPanel, CalendarPanel,
  DevicePanel, MemoryPanel, FilePanel, SettingsPanel,
} from './components/ModulePanels';

const MODULE_MAP: Record<ModuleId, React.FC> = {
  chat: ChatPanel,
  tasks: TaskPanel,
  memory: MemoryPanel,
  calendar: CalendarPanel,
  email: EmailPanel,
  search: SearchPanel,
  devices: DevicePanel,
  files: FilePanel,
  settings: SettingsPanel,
};

function App() {
  const { activeModule } = useAppStore();
  const { isListening, isSpeaking } = useVoiceStore();

  const ActivePanel = MODULE_MAP[activeModule] || ChatPanel;

  // Register Electron event listeners
  useEffect(() => {
    if (isElectron) {
      const cleanupPTT = electron.onPushToTalk(() => {
        useVoiceStore.getState().toggleListening();
      });
      const cleanupAOT = electron.onAlwaysOnTopChanged((v) => {
        useAppStore.getState().setAlwaysOnTop(v);
      });
      return () => { cleanupPTT(); cleanupAOT(); };
    }
  }, []);

  const hudCorner = (pos: 'tl' | 'tr' | 'bl' | 'br') => {
    const s = 12;
    const b = '1.5px solid rgba(255, 94, 0, 0.3)';
    const m: Record<string, React.CSSProperties> = {
      tl: { top: 0, left: 0, borderTop: b, borderLeft: b },
      tr: { top: 0, right: 0, borderTop: b, borderRight: b },
      bl: { bottom: 0, left: 0, borderBottom: b, borderLeft: b },
      br: { bottom: 0, right: 0, borderBottom: b, borderRight: b },
    };
    return <div style={{ position: 'absolute', width: s, height: s, ...m[pos] }} />;
  };

  return (
    <div className="w-screen h-screen flex bg-echo-dark overflow-hidden font-sans text-white select-none">
      {/* ── Draggable Title Bar (Electron) ── */}
      {isElectron && (
        <div className="fixed top-0 left-0 right-0 h-8 z-50" style={{ WebkitAppRegion: 'drag' } as any}>
          <div className="flex justify-end items-center h-full pr-2 gap-1" style={{ WebkitAppRegion: 'no-drag' } as any}>
            <button onClick={electron.minimize} className="w-6 h-6 rounded flex items-center justify-center text-white/30 hover:bg-white/10 text-[10px]">─</button>
            <button onClick={electron.maximize} className="w-6 h-6 rounded flex items-center justify-center text-white/30 hover:bg-white/10 text-[10px]">□</button>
            <button onClick={electron.close} className="w-6 h-6 rounded flex items-center justify-center text-white/30 hover:bg-red-500/30 hover:text-red-400 text-[10px]">✕</button>
          </div>
        </div>
      )}

      {/* ── Left Sidebar ── */}
      <div className="w-[260px] flex-shrink-0 h-full">
        <Sidebar />
      </div>

      {/* ── Main Panel ── */}
      <div className="flex-1 flex flex-col h-full relative" style={{ background: 'linear-gradient(180deg, #0d1117 0%, #0a0e15 100%)' }}>
        {/* Top Bar */}
        <div className="px-6 py-3 flex justify-between items-center border-b border-echo-orange/[0.08] bg-black/20">
          <div className="flex items-center gap-4">
            <span className="text-[11px] tracking-[3px] text-echo-orange font-mono font-bold">
              ◈ {activeModule === 'chat' ? 'NEURAL CHAT' : activeModule.toUpperCase()}
            </span>
            <span className="text-[9px] px-2 py-0.5 rounded bg-green-500/10 text-green-400 border border-green-500/20 tracking-[1px]">
              ACTIVE
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span className={`text-[9px] tracking-[1.5px] font-mono transition-all ${
              isListening ? 'text-echo-orange text-shadow-glow' : 'text-white/30'
            }`}>
              {isListening ? '● REC' : '○ IDLE'}
            </span>
            <span className="text-[9px] text-white/20 font-mono tracking-[1px]">
              {new Date().toLocaleTimeString('en-US', { hour12: false })}
            </span>
          </div>
        </div>

        {/* Hologram HUD */}
        <div className="h-[220px] relative flex-shrink-0 border-b border-echo-orange/[0.06]">
          <HologramCanvas isSpeaking={isListening || isSpeaking} />
          <div className="absolute inset-3 pointer-events-none">
            {hudCorner('tl')}{hudCorner('tr')}{hudCorner('bl')}{hudCorner('br')}
          </div>
          <div className="absolute top-4 left-5 text-[8px] text-echo-orange/40 font-mono tracking-[1px]">
            HOLOGRAPHIC INTERFACE // ACTIVE
          </div>
          <div className="absolute bottom-4 right-5 text-[8px] text-echo-gold/40 font-mono tracking-[1px]">
            NEURAL PROC: {isListening ? '87%' : '12%'}
          </div>
        </div>

        {/* Active Module Content */}
        <div className="flex-1 overflow-hidden">
          <ActivePanel />
        </div>

        {/* Voice Waveform Bar */}
        <div className="h-10 border-t border-echo-orange/[0.06] border-b border-echo-orange/[0.06] bg-black/30">
          <VoiceBar isActive={isListening} />
        </div>
      </div>
    </div>
  );
}

export default App;
