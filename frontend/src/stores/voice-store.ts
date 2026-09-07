/**
 * ECHO OS — Voice Store (Zustand)
 */

import { create } from 'zustand';

interface VoiceState {
  isListening: boolean;
  isSpeaking: boolean;
  audioLevel: number;
  frequencyData: Uint8Array;
  pushToTalkActive: boolean;

  setListening: (v: boolean) => void;
  setSpeaking: (v: boolean) => void;
  setAudioLevel: (v: number) => void;
  setFrequencyData: (d: Uint8Array) => void;
  toggleListening: () => void;
  setPushToTalk: (v: boolean) => void;
}

export const useVoiceStore = create<VoiceState>((set) => ({
  isListening: false,
  isSpeaking: false,
  audioLevel: 0,
  frequencyData: new Uint8Array(0),
  pushToTalkActive: false,

  setListening: (v) => set({ isListening: v }),
  setSpeaking: (v) => set({ isSpeaking: v }),
  setAudioLevel: (v) => set({ audioLevel: v }),
  setFrequencyData: (d) => set({ frequencyData: d }),
  toggleListening: () => set((s) => ({ isListening: !s.isListening })),
  setPushToTalk: (v) => set({ pushToTalkActive: v }),
}));
