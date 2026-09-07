/**
 * ECHO OS — Task Store (Zustand)
 */

import { create } from 'zustand';
import api from '../lib/api';

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: string;
  priority: string;
  due_date?: string;
  tags: string[];
  created_at: string;
}

interface TaskState {
  tasks: Task[];
  isLoading: boolean;
  filter: string | null;

  loadTasks: (status?: string) => Promise<void>;
  addTask: (title: string, description?: string, priority?: string) => Promise<void>;
  completeTask: (id: string) => Promise<void>;
  removeTask: (id: string) => Promise<void>;
  setFilter: (f: string | null) => void;
}

export const useTaskStore = create<TaskState>((set, get) => ({
  tasks: [],
  isLoading: false,
  filter: null,

  loadTasks: async (status) => {
    set({ isLoading: true });
    try {
      const data = await api.getTasks(status);
      set({ tasks: Array.isArray(data) ? data : [], isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  addTask: async (title, description, priority) => {
    try {
      await api.createTask(title, description, priority);
      await get().loadTasks();
    } catch {}
  },

  completeTask: async (id) => {
    try {
      await api.completeTask(id);
      set((s) => ({
        tasks: s.tasks.map((t) => (t.id === id ? { ...t, status: 'completed' } : t)),
      }));
    } catch {}
  },

  removeTask: async (id) => {
    try {
      await api.deleteTask(id);
      set((s) => ({ tasks: s.tasks.filter((t) => t.id !== id) }));
    } catch {}
  },

  setFilter: (f) => set({ filter: f }),
}));
