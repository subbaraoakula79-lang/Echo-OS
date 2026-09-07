/**
 * ECHO OS — Electron Bridge
 * Type-safe wrapper for Electron preload API with web fallback.
 */

interface EchoElectron {
  minimize: () => void;
  maximize: () => void;
  close: () => void;
  toggleAlwaysOnTop: () => void;
  openApp: (appName: string) => Promise<{ success: boolean; error?: string }>;
  searchFiles: (query: string, path?: string) => Promise<{ results: { path: string; name: string }[] }>;
  getSystemInfo: () => Promise<SystemInfo>;
  onPushToTalk: (callback: () => void) => () => void;
  onAlwaysOnTopChanged: (callback: (value: boolean) => void) => () => void;
  platform: string;
  isElectron: boolean;
}

export interface SystemInfo {
  platform: string;
  arch: string;
  hostname: string;
  cpuModel: string;
  cpuCores: number;
  totalMemoryGB: string;
  freeMemoryGB: string;
  memoryUsagePercent: number;
  uptime: number;
}

declare global {
  interface Window {
    echoElectron?: EchoElectron;
  }
}

export const isElectron = !!(window as any).echoElectron?.isElectron;

export const electron: EchoElectron = (window as any).echoElectron || {
  minimize: () => {},
  maximize: () => {},
  close: () => {},
  toggleAlwaysOnTop: () => {},
  openApp: async () => ({ success: false, error: 'Not in Electron' }),
  searchFiles: async () => ({ results: [] }),
  getSystemInfo: async () => ({
    platform: navigator.platform,
    arch: 'unknown',
    hostname: 'Web Browser',
    cpuModel: 'Unknown',
    cpuCores: navigator.hardwareConcurrency || 4,
    totalMemoryGB: 'N/A',
    freeMemoryGB: 'N/A',
    memoryUsagePercent: 0,
    uptime: 0,
  }),
  onPushToTalk: () => () => {},
  onAlwaysOnTopChanged: () => () => {},
  platform: navigator.platform,
  isElectron: false,
};
