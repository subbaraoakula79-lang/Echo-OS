/**
 * ECHO OS — App Store (Zustand)
 */

import { create } from 'zustand';

export type ModuleId = 'chat' | 'memory' | 'tasks' | 'calendar' | 'email' | 'search' | 'devices' | 'files' | 'settings';

interface AppState {
  activeModule: ModuleId;
  sidebarCollapsed: boolean;
  isAlwaysOnTop: boolean;
  theme: 'jarvis' | 'cyber';
  userName: string;
  userEmail: string;
  isAuthenticated: boolean;

  setActiveModule: (m: ModuleId) => void;
  toggleSidebar: () => void;
  setAlwaysOnTop: (v: boolean) => void;
  setTheme: (t: 'jarvis' | 'cyber') => void;
  setUser: (name: string, email: string) => void;
  setAuthenticated: (v: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeModule: 'chat',
  sidebarCollapsed: false,
  isAlwaysOnTop: false,
  theme: 'jarvis',
  userName: 'USER',
  userEmail: '',
  isAuthenticated: false,

  setActiveModule: (m) => set({ activeModule: m }),
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  setAlwaysOnTop: (v) => set({ isAlwaysOnTop: v }),
  setTheme: (t) => set({ theme: t }),
  setUser: (name, email) => set({ userName: name, userEmail: email }),
  setAuthenticated: (v) => set({ isAuthenticated: v }),
}));
