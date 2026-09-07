/**
 * ECHO OS — Sidebar
 * Navigation with module list, system metrics, and JARVIS orange/gold theming.
 */

import { useState, useEffect } from 'react';
import { useAppStore, type ModuleId } from '../stores/app-store';
import { electron, isElectron, type SystemInfo } from '../lib/electron-bridge';

interface Module {
  id: ModuleId;
  name: string;
  icon: string;
  status: 'online' | 'standby' | 'offline';
  description: string;
}

const MODULES: Module[] = [
  { id: 'chat', name: 'NEURAL CHAT', icon: '⬡', status: 'online', description: 'AI conversation engine' },
  { id: 'memory', name: 'MEMORY CORE', icon: '◈', status: 'online', description: 'Long-term knowledge base' },
  { id: 'tasks', name: 'TASK ENGINE', icon: '⬢', status: 'online', description: 'Task & reminder system' },
  { id: 'calendar', name: 'TEMPORAL', icon: '◎', status: 'standby', description: 'Calendar management' },
  { id: 'email', name: 'COMM LINK', icon: '◇', status: 'standby', description: 'Email & messaging' },
  { id: 'search', name: 'WEB SCAN', icon: '◉', status: 'online', description: 'Internet search engine' },
  { id: 'devices', name: 'DEVICE NET', icon: '⬟', status: 'standby', description: 'Connected devices' },
  { id: 'files', name: 'FILE VAULT', icon: '▣', status: 'standby', description: 'File system access' },
  { id: 'settings', name: 'SETTINGS', icon: '⚙', status: 'online', description: 'System configuration' },
];

const STATUS_COLORS: Record<string, string> = {
  online: '#ff5e00',
  standby: '#ffd700',
  offline: '#ff0044',
};

export default function Sidebar() {
  const { activeModule, setActiveModule, userName } = useAppStore();
  const [hoveredModule, setHoveredModule] = useState<string | null>(null);
  const [sysInfo, setSysInfo] = useState<SystemInfo | null>(null);

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const info = await electron.getSystemInfo();
        setSysInfo(info);
      } catch {}
    };
    fetchInfo();
    const interval = setInterval(fetchInfo, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full h-full flex flex-col font-mono overflow-hidden"
      style={{ background: 'rgba(13, 17, 23, 0.95)', borderRight: '1px solid rgba(255, 94, 0, 0.1)' }}>

      {/* Logo */}
      <div className="px-4 pt-5 pb-4" style={{ borderBottom: '1px solid rgba(255, 94, 0, 0.08)' }}>
        <div className="flex items-center gap-2.5 mb-1">
          <div className="w-2 h-2 rounded-full"
            style={{ background: '#ff5e00', boxShadow: '0 0 6px #ff5e00, 0 0 12px rgba(255,94,0,0.3)' }} />
          <span className="text-[13px] font-bold tracking-[4px]"
            style={{ color: '#ff5e00', textShadow: '0 0 8px rgba(255,94,0,0.4)' }}>
            ECHO OS
          </span>
        </div>
        <div className="text-[9px] ml-[18px]" style={{ color: 'rgba(255,255,255,0.25)', letterSpacing: '2px' }}>
          v1.0.0 // SYSTEM ACTIVE
        </div>
      </div>

      {/* System Metrics */}
      <div className="px-4 py-3" style={{ borderBottom: '1px solid rgba(255, 94, 0, 0.08)' }}>
        <div className="text-[8px] mb-2" style={{ color: 'rgba(255,94,0,0.5)', letterSpacing: '2px' }}>
          SYS METRICS
        </div>
        <div className="flex gap-2">
          {[
            { label: 'CPU', value: sysInfo ? `${sysInfo.memoryUsagePercent}%` : '—', color: '#ff5e00' },
            { label: 'MEM', value: sysInfo ? `${sysInfo.freeMemoryGB}G` : '—', color: '#ffd700' },
            { label: 'NET', value: '↑↓', color: '#ff5e00' },
          ].map((m) => (
            <div key={m.label} className="flex-1 py-1.5 px-1 rounded text-center"
              style={{ background: 'rgba(255,94,0,0.04)', border: '1px solid rgba(255,94,0,0.08)' }}>
              <div className="text-[8px]" style={{ color: 'rgba(255,255,255,0.3)', letterSpacing: '1px' }}>{m.label}</div>
              <div className="text-[11px] font-bold mt-0.5" style={{ color: m.color }}>{m.value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Module List */}
      <div className="px-2 py-2 flex-1 overflow-y-auto echo-scrollbar">
        <div className="text-[8px] px-2 pb-2 pt-1" style={{ color: 'rgba(255,94,0,0.5)', letterSpacing: '2px' }}>
          MODULES
        </div>
        {MODULES.map((mod) => {
          const isActive = activeModule === mod.id;
          const isHovered = hoveredModule === mod.id;
          return (
            <button
              key={mod.id}
              onClick={() => setActiveModule(mod.id)}
              onMouseEnter={() => setHoveredModule(mod.id)}
              onMouseLeave={() => setHoveredModule(null)}
              className="w-full flex items-center gap-2.5 py-2.5 px-2.5 mb-0.5 rounded-md border-none cursor-pointer transition-all duration-200 text-left"
              style={{
                background: isActive ? 'rgba(255, 94, 0, 0.12)' : isHovered ? 'rgba(255, 94, 0, 0.06)' : 'transparent',
                borderLeft: isActive ? '2px solid #ff5e00' : '2px solid transparent',
              }}
            >
              <span className="text-[14px] w-5 text-center"
                style={{
                  color: isActive ? '#ff5e00' : 'rgba(255,255,255,0.4)',
                  filter: isActive ? 'drop-shadow(0 0 4px rgba(255,94,0,0.6))' : 'none',
                }}>
                {mod.icon}
              </span>
              <div className="flex-1 min-w-0">
                <div className="text-[10px] font-semibold truncate"
                  style={{
                    letterSpacing: '1.5px',
                    color: isActive ? '#ff5e00' : isHovered ? 'rgba(255,255,255,0.7)' : 'rgba(255,255,255,0.45)',
                  }}>
                  {mod.name}
                </div>
                <div className="text-[8px] truncate mt-px" style={{ color: 'rgba(255,255,255,0.2)' }}>
                  {mod.description}
                </div>
              </div>
              <div className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                style={{ background: STATUS_COLORS[mod.status], boxShadow: `0 0 4px ${STATUS_COLORS[mod.status]}` }} />
            </button>
          );
        })}
      </div>

      {/* User Area */}
      <div className="px-4 py-3 flex items-center gap-2.5"
        style={{ borderTop: '1px solid rgba(255, 94, 0, 0.08)' }}>
        <div className="w-7 h-7 rounded-full flex items-center justify-center text-[12px] font-bold text-white"
          style={{ background: 'linear-gradient(135deg, #ff5e00, #ffd700)' }}>
          {userName.charAt(0).toUpperCase()}
        </div>
        <div>
          <div className="text-[10px]" style={{ color: 'rgba(255,255,255,0.6)', letterSpacing: '1px' }}>{userName}</div>
          <div className="text-[8px]" style={{ color: 'rgba(255,255,255,0.25)' }}>ADMIN ACCESS</div>
        </div>
      </div>
    </div>
  );
}
