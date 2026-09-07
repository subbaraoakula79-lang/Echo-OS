/**
 * ECHO OS — Module Panels (Placeholder views for secondary modules)
 * Each panel has a consistent JARVIS-styled header with status indicators.
 */

import { Search, Mail, Calendar, HardDrive, Database, Settings, Globe, Smartphone } from 'lucide-react';

function ModuleShell({ icon: Icon, title, subtitle, children }: {
  icon: any; title: string; subtitle: string; children?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col h-full px-6 py-4">
      <div className="mb-4">
        <div className="flex items-center gap-2">
          <Icon size={14} className="text-echo-orange" />
          <span className="text-[11px] font-mono tracking-[3px] text-echo-orange font-bold">{title}</span>
        </div>
        <div className="text-[9px] text-white/25 mt-1 ml-5">{subtitle}</div>
      </div>
      <div className="flex-1 overflow-y-auto echo-scrollbar">
        {children || (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-full border border-echo-orange/15 flex items-center justify-center mb-4">
              <Icon size={24} className="text-echo-orange/30" />
            </div>
            <div className="text-[12px] text-white/30 mb-1">Module Ready</div>
            <div className="text-[10px] text-white/15">Connect your services to activate this module.</div>
          </div>
        )}
      </div>
    </div>
  );
}

export function SearchPanel() {
  return <ModuleShell icon={Globe} title="WEB SCAN" subtitle="Internet search engine" />;
}

export function EmailPanel() {
  return <ModuleShell icon={Mail} title="COMM LINK" subtitle="Email & messaging hub" />;
}

export function CalendarPanel() {
  return <ModuleShell icon={Calendar} title="TEMPORAL" subtitle="Calendar management" />;
}

export function DevicePanel() {
  return <ModuleShell icon={Smartphone} title="DEVICE NET" subtitle="Connected devices" />;
}

export function MemoryPanel() {
  return <ModuleShell icon={Database} title="MEMORY CORE" subtitle="Long-term knowledge base" />;
}

export function FilePanel() {
  return <ModuleShell icon={HardDrive} title="FILE VAULT" subtitle="File system access" />;
}

export function SettingsPanel() {
  return <ModuleShell icon={Settings} title="SETTINGS" subtitle="System configuration" />;
}
