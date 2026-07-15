import { useState } from 'react';

interface Module {
  id: string;
  name: string;
  icon: string;
  status: 'online' | 'standby' | 'offline';
  description: string;
}

const MODULES: Module[] = [
  { id: 'chat', name: 'NEURAL CHAT', icon: '⬡', status: 'online', description: 'AI conversation engine' },
  { id: 'memory', name: 'MEMORY CORE', icon: '◈', status: 'online', description: 'Long-term knowledge base' },
  { id: 'tasks', name: 'TASK ENGINE', icon: '⬢', status: 'standby', description: 'Task & reminder system' },
  { id: 'calendar', name: 'TEMPORAL', icon: '◎', status: 'standby', description: 'Calendar management' },
  { id: 'email', name: 'COMM LINK', icon: '◇', status: 'offline', description: 'Email & messaging' },
  { id: 'search', name: 'WEB SCAN', icon: '◉', status: 'online', description: 'Internet search engine' },
  { id: 'devices', name: 'DEVICE NET', icon: '⬟', status: 'offline', description: 'Connected devices' },
  { id: 'files', name: 'FILE VAULT', icon: '▣', status: 'standby', description: 'File system access' },
];

const STATUS_COLORS: Record<string, string> = {
  online: '#00ff88',
  standby: '#ffaa00',
  offline: '#ff0044',
};

interface SidebarProps {
  activeModule: string;
  onModuleSelect: (id: string) => void;
}

export default function Sidebar({ activeModule, onModuleSelect }: SidebarProps) {
  const [hoveredModule, setHoveredModule] = useState<string | null>(null);

  return (
    <div style={{
      width: '100%', height: '100%',
      background: 'rgba(13, 17, 23, 0.95)',
      borderRight: '1px solid rgba(0, 153, 255, 0.1)',
      display: 'flex', flexDirection: 'column',
      fontFamily: "'Courier New', 'Consolas', monospace",
      overflow: 'hidden'
    }}>
      {/* Logo Section */}
      <div style={{
        padding: '20px 16px 16px',
        borderBottom: '1px solid rgba(0, 153, 255, 0.08)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
          <div style={{
            width: '8px', height: '8px', borderRadius: '50%',
            background: '#00ff88',
            boxShadow: '0 0 6px #00ff88, 0 0 12px rgba(0,255,136,0.3)',
          }} />
          <span style={{
            fontSize: '13px', fontWeight: 700, letterSpacing: '4px',
            color: '#0099ff',
            textShadow: '0 0 8px rgba(0,153,255,0.4)'
          }}>ECHO OS</span>
        </div>
        <div style={{
          fontSize: '9px', color: 'rgba(255,255,255,0.25)',
          letterSpacing: '2px', marginLeft: '18px'
        }}>
          v1.0.0 // SYSTEM ACTIVE
        </div>
      </div>

      {/* System Metrics */}
      <div style={{
        padding: '12px 16px',
        borderBottom: '1px solid rgba(0, 153, 255, 0.08)',
      }}>
        <div style={{ fontSize: '8px', color: 'rgba(0,153,255,0.5)', letterSpacing: '2px', marginBottom: '8px' }}>
          SYS METRICS
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {[
            { label: 'CPU', value: '24%', color: '#00ff88' },
            { label: 'MEM', value: '1.2G', color: '#0099ff' },
            { label: 'NET', value: '↑↓', color: '#ff0080' },
          ].map(m => (
            <div key={m.label} style={{
              flex: 1, padding: '6px',
              background: 'rgba(0,153,255,0.04)',
              borderRadius: '4px',
              border: '1px solid rgba(0,153,255,0.08)',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '8px', color: 'rgba(255,255,255,0.3)', letterSpacing: '1px' }}>{m.label}</div>
              <div style={{ fontSize: '11px', color: m.color, fontWeight: 700, marginTop: '2px' }}>{m.value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Module List */}
      <div style={{
        padding: '8px',
        flex: 1, overflowY: 'auto',
      }}>
        <div style={{ fontSize: '8px', color: 'rgba(0,153,255,0.5)', letterSpacing: '2px', padding: '4px 8px 8px', }}>
          MODULES
        </div>
        {MODULES.map(mod => {
          const isActive = activeModule === mod.id;
          const isHovered = hoveredModule === mod.id;
          return (
            <button
              key={mod.id}
              onClick={() => onModuleSelect(mod.id)}
              onMouseEnter={() => setHoveredModule(mod.id)}
              onMouseLeave={() => setHoveredModule(null)}
              style={{
                width: '100%',
                display: 'flex', alignItems: 'center', gap: '10px',
                padding: '10px 10px',
                marginBottom: '2px',
                borderRadius: '6px',
                border: 'none',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                background: isActive
                  ? 'rgba(0, 153, 255, 0.12)'
                  : isHovered ? 'rgba(0, 153, 255, 0.06)' : 'transparent',
                borderLeft: isActive ? '2px solid #0099ff' : '2px solid transparent',
                textAlign: 'left',
              }}
            >
              {/* Icon */}
              <span style={{
                fontSize: '14px',
                color: isActive ? '#0099ff' : 'rgba(255,255,255,0.4)',
                width: '20px', textAlign: 'center',
                filter: isActive ? 'drop-shadow(0 0 4px rgba(0,153,255,0.6))' : 'none'
              }}>
                {mod.icon}
              </span>
              {/* Label + desc */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  fontSize: '10px', fontWeight: 600,
                  letterSpacing: '1.5px',
                  color: isActive ? '#0099ff' : isHovered ? 'rgba(255,255,255,0.7)' : 'rgba(255,255,255,0.45)',
                  transition: 'color 0.2s',
                  whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                }}>
                  {mod.name}
                </div>
                <div style={{
                  fontSize: '8px', color: 'rgba(255,255,255,0.2)',
                  marginTop: '1px',
                  whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                }}>
                  {mod.description}
                </div>
              </div>
              {/* Status dot */}
              <div style={{
                width: '6px', height: '6px', borderRadius: '50%',
                background: STATUS_COLORS[mod.status],
                boxShadow: `0 0 4px ${STATUS_COLORS[mod.status]}`,
                flexShrink: 0
              }} />
            </button>
          );
        })}
      </div>

      {/* Bottom user area */}
      <div style={{
        padding: '12px 16px',
        borderTop: '1px solid rgba(0, 153, 255, 0.08)',
        display: 'flex', alignItems: 'center', gap: '10px',
      }}>
        <div style={{
          width: '28px', height: '28px', borderRadius: '50%',
          background: 'linear-gradient(135deg, #0099ff, #ff0080)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '12px', fontWeight: 700, color: 'white'
        }}>U</div>
        <div>
          <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.6)', letterSpacing: '1px' }}>USER</div>
          <div style={{ fontSize: '8px', color: 'rgba(255,255,255,0.25)' }}>ADMIN ACCESS</div>
        </div>
      </div>
    </div>
  );
}
