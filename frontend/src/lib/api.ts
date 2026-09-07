/**
 * ECHO OS — API Client
 * Centralized HTTP client with JWT auth and WebSocket management.
 */

import axios from 'axios';
import type { AxiosInstance } from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';
const WS_BASE = 'ws://localhost:8000/api/v1';

class ApiClient {
  private http: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.http = axios.create({
      baseURL: API_BASE,
      timeout: 30000,
      headers: { 'Content-Type': 'application/json' },
    });

    this.http.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    // Auto-refresh on 401
    this.http.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          const refreshToken = localStorage.getItem('echo_refresh_token');
          if (refreshToken) {
            try {
              const { data } = await axios.post(`${API_BASE}/auth/refresh`, {
                refresh_token: refreshToken,
              });
              this.setToken(data.access_token, data.refresh_token);
              error.config.headers.Authorization = `Bearer ${data.access_token}`;
              return this.http.request(error.config);
            } catch {
              this.clearToken();
            }
          }
        }
        return Promise.reject(error);
      }
    );

    // Load saved token
    const saved = localStorage.getItem('echo_access_token');
    if (saved) this.token = saved;
  }

  setToken(access: string, refresh?: string) {
    this.token = access;
    localStorage.setItem('echo_access_token', access);
    if (refresh) localStorage.setItem('echo_refresh_token', refresh);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('echo_access_token');
    localStorage.removeItem('echo_refresh_token');
  }

  isAuthenticated() {
    return !!this.token;
  }

  // ── Auth ──
  async register(email: string, display_name: string, password: string) {
    const { data } = await this.http.post('/auth/register', { email, display_name, password });
    this.setToken(data.access_token, data.refresh_token);
    return data;
  }

  async login(email: string, password: string) {
    const { data } = await this.http.post('/auth/login', { email, password });
    this.setToken(data.access_token, data.refresh_token);
    return data;
  }

  async getMe() {
    const { data } = await this.http.get('/auth/me');
    return data;
  }

  // ── Chat ──
  async sendMessage(message: string, conversationId?: string) {
    const { data } = await this.http.post('/chat/completions', {
      message,
      conversation_id: conversationId,
    });
    return data;
  }

  async streamMessage(message: string, conversationId?: string, onToken?: (token: string) => void) {
    const response = await fetch(`${API_BASE}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
      },
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) return;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value, { stream: true });
      const lines = text.split('\n').filter((l) => l.startsWith('data: '));

      for (const line of lines) {
        try {
          const data = JSON.parse(line.slice(6));
          if (data.token && onToken) onToken(data.token);
          if (data.done) return data.conversation_id;
        } catch {}
      }
    }
  }

  async getConversations(limit = 20) {
    const { data } = await this.http.get('/chat/conversations', { params: { limit } });
    return data;
  }

  async getMessages(conversationId: string) {
    const { data } = await this.http.get(`/chat/conversations/${conversationId}/messages`);
    return data;
  }

  // ── Tasks ──
  async getTasks(status?: string) {
    const { data } = await this.http.get('/tasks/', { params: { status } });
    return data;
  }

  async createTask(title: string, description?: string, priority?: string, due_date?: string) {
    const { data } = await this.http.post('/tasks/', { title, description, priority, due_date });
    return data;
  }

  async completeTask(taskId: string) {
    const { data } = await this.http.post(`/tasks/${taskId}/complete`);
    return data;
  }

  async deleteTask(taskId: string) {
    const { data } = await this.http.delete(`/tasks/${taskId}`);
    return data;
  }

  // ── Memory ──
  async getMemories(category?: string) {
    const { data } = await this.http.get('/memory/', { params: { category } });
    return data;
  }

  async searchMemories(query: string) {
    const { data } = await this.http.post('/memory/search', { query });
    return data;
  }

  // ── Search ──
  async searchWeb(query: string) {
    const { data } = await this.http.post('/search/web', { query });
    return data;
  }

  // ── WebSocket ──
  createVoiceSocket(): WebSocket {
    return new WebSocket(`${WS_BASE}/chat/ws/voice`);
  }
}

export const api = new ApiClient();
export default api;
