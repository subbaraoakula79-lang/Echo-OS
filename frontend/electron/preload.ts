/**
 * ECHO OS — Electron Preload Script
 * Secure context bridge exposing native APIs to the renderer.
 */

import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('echoElectron', {
  // ── Window Controls ──
  minimize: () => ipcRenderer.send('window:minimize'),
  maximize: () => ipcRenderer.send('window:maximize'),
  close: () => ipcRenderer.send('window:close'),
  toggleAlwaysOnTop: () => ipcRenderer.send('window:toggle-always-on-top'),

  // ── System Operations ──
  openApp: (appName: string) => ipcRenderer.invoke('system:open-app', appName),
  searchFiles: (query: string, path?: string) => ipcRenderer.invoke('system:search-files', query, path),
  getSystemInfo: () => ipcRenderer.invoke('system:get-info'),

  // ── Event Listeners ──
  onPushToTalk: (callback: () => void) => {
    ipcRenderer.on('push-to-talk', callback);
    return () => ipcRenderer.removeListener('push-to-talk', callback);
  },
  onAlwaysOnTopChanged: (callback: (value: boolean) => void) => {
    ipcRenderer.on('always-on-top-changed', (_event, value) => callback(value));
    return () => ipcRenderer.removeListener('always-on-top-changed', () => {});
  },

  // ── Platform Info ──
  platform: process.platform,
  isElectron: true,
});
