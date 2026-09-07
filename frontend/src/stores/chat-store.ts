/**
 * ECHO OS — Chat Store (Zustand)
 */

import { create } from 'zustand';
import api from '../lib/api';

export interface Message {
  id?: string;
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  toolResults?: any[];
  timestamp: string;
  isStreaming?: boolean;
}

interface ChatState {
  messages: Message[];
  conversationId: string | null;
  conversations: any[];
  isLoading: boolean;
  isStreaming: boolean;

  sendMessage: (content: string) => Promise<void>;
  streamMessage: (content: string) => Promise<void>;
  loadConversations: () => Promise<void>;
  switchConversation: (id: string) => Promise<void>;
  newConversation: () => void;
  addSystemMessage: (content: string) => void;
}

const getTimestamp = () => new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' });

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [
    { role: 'system', content: '// ECHO OS v1.0.0 initialized', timestamp: getTimestamp() },
    { role: 'assistant', content: 'Neural link established. All systems nominal. How can I assist you?', timestamp: getTimestamp() },
  ],
  conversationId: null,
  conversations: [],
  isLoading: false,
  isStreaming: false,

  sendMessage: async (content) => {
    const userMsg: Message = { role: 'user', content, timestamp: getTimestamp() };
    set((s) => ({ messages: [...s.messages, userMsg], isLoading: true }));

    try {
      const response = await api.sendMessage(content, get().conversationId || undefined);
      const assistantMsg: Message = {
        role: 'assistant',
        content: response.message,
        toolResults: response.tool_results,
        timestamp: getTimestamp(),
      };
      set((s) => ({
        messages: [...s.messages, assistantMsg],
        conversationId: response.conversation_id || s.conversationId,
        isLoading: false,
      }));
    } catch (error: any) {
      const errMsg: Message = {
        role: 'assistant',
        content: `Connection error: ${error.message || 'Unable to reach ECHO backend. Is the server running?'}`,
        timestamp: getTimestamp(),
      };
      set((s) => ({ messages: [...s.messages, errMsg], isLoading: false }));
    }
  },

  streamMessage: async (content) => {
    const userMsg: Message = { role: 'user', content, timestamp: getTimestamp() };
    const streamMsg: Message = { role: 'assistant', content: '', timestamp: getTimestamp(), isStreaming: true };

    set((s) => ({ messages: [...s.messages, userMsg, streamMsg], isStreaming: true }));

    try {
      await api.streamMessage(content, get().conversationId || undefined, (token) => {
        set((s) => {
          const msgs = [...s.messages];
          const last = msgs[msgs.length - 1];
          if (last.isStreaming) {
            msgs[msgs.length - 1] = { ...last, content: last.content + token };
          }
          return { messages: msgs };
        });
      });

      set((s) => {
        const msgs = [...s.messages];
        const last = msgs[msgs.length - 1];
        if (last.isStreaming) {
          msgs[msgs.length - 1] = { ...last, isStreaming: false };
        }
        return { messages: msgs, isStreaming: false };
      });
    } catch {
      set((s) => ({ isStreaming: false }));
    }
  },

  loadConversations: async () => {
    try {
      const data = await api.getConversations();
      set({ conversations: data });
    } catch {}
  },

  switchConversation: async (id) => {
    try {
      const data = await api.getMessages(id);
      const messages: Message[] = (data.messages || []).map((m: any) => ({
        role: m.role,
        content: m.content || '',
        timestamp: new Date(m.timestamp || Date.now()).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' }),
      }));
      set({ conversationId: id, messages });
    } catch {}
  },

  newConversation: () => {
    set({
      conversationId: null,
      messages: [
        { role: 'system', content: '// New conversation started', timestamp: getTimestamp() },
        { role: 'assistant', content: 'Ready for your next command.', timestamp: getTimestamp() },
      ],
    });
  },

  addSystemMessage: (content) => {
    set((s) => ({
      messages: [...s.messages, { role: 'system', content, timestamp: getTimestamp() }],
    }));
  },
}));
