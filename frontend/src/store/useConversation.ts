import { create } from "zustand";
import type { Msg } from "@/lib/api";

type State = {
  language: string;
  messages: Msg[];
  isStreaming: boolean;
  voiceEnabled: boolean;
  advisory: { code: string; message: string } | null;
  setLanguage: (l: string) => void;
  setMessages: (m: Msg[]) => void;
  appendMessage: (m: Msg) => void;
  updateLastAssistant: (text: string) => void;
  setStreaming: (b: boolean) => void;
  setVoiceEnabled: (b: boolean) => void;
  setAdvisory: (a: { code: string; message: string } | null) => void;
  reset: () => void;
};

const LANG_KEY = "vaeo_language";

export const useConversation = create<State>((set) => ({
  language: localStorage.getItem(LANG_KEY) || "English",
  messages: [],
  isStreaming: false,
  voiceEnabled: true,
  advisory: null,
  setLanguage: (l) => {
    localStorage.setItem(LANG_KEY, l);
    set({ language: l });
  },
  setMessages: (messages) => set({ messages }),
  appendMessage: (m) => set((s) => ({ messages: [...s.messages, m] })),
  updateLastAssistant: (text) =>
    set((s) => {
      const msgs = [...s.messages];
      for (let i = msgs.length - 1; i >= 0; i--) {
        if (msgs[i].role === "assistant") {
          msgs[i] = { ...msgs[i], content: text };
          break;
        }
      }
      return { messages: msgs };
    }),
  setStreaming: (b) => set({ isStreaming: b }),
  setVoiceEnabled: (b) => set({ voiceEnabled: b }),
  setAdvisory: (a) => set({ advisory: a }),
  reset: () => set({ messages: [], advisory: null }),
}));
