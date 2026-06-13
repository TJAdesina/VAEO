import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useConversation } from "@/store/useConversation";
import { chatPlain, chatStream, fetchWelcome, tts } from "@/lib/api";
import { ui } from "@/lib/i18n";
import Header from "@/components/Header";
import GreetingHero from "@/components/GreetingHero";
import TopicTiles from "@/components/TopicTiles";
import ChatBubble from "@/components/ChatBubble";
import InputBar from "@/components/InputBar";
import OfflineStrip from "@/components/OfflineStrip";
import AdvisoryBanner from "@/components/AdvisoryBanner";
import TypingIndicator from "@/components/TypingIndicator";
import LanguageSheet from "@/components/LanguageSheet";

const ISO_TO_LANG: Record<string, string> = {
  en: "English",
  pcm: "Pidgin",
  yo: "Yoruba",
  ig: "Igbo",
  ha: "Hausa",
};

export default function Chat() {
  const {
    language,
    messages,
    appendMessage,
    updateLastAssistant,
    isStreaming,
    setStreaming,
    voiceEnabled,
    advisory,
    setAdvisory,
    setLanguage,
    reset,
  } = useConversation();

  const t = ui(language);
  const [welcome, setWelcome] = useState("");
  const [showSheet, setShowSheet] = useState(false);
  const [pendingAudio, setPendingAudio] = useState<{ text: string } | null>(null);
  const scrollerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchWelcome(language).then(setWelcome).catch(() => setWelcome(""));
  }, [language]);

  useEffect(() => {
    scrollerRef.current?.scrollTo({ top: scrollerRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isStreaming]);

  // Auto-play TTS for last finished assistant message when voice enabled
  useEffect(() => {
    if (!voiceEnabled || isStreaming) return;
    if (!pendingAudio) return;
    let cancelled = false;
    (async () => {
      try {
        const url = await tts(pendingAudio.text, language);
        if (cancelled) return;
        const a = new Audio(url);
        a.play().catch(() => {});
      } catch {
        /* ignore */
      } finally {
        setPendingAudio(null);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [pendingAudio, voiceEnabled, isStreaming, language]);

  async function handleSend(text: string) {
    if (!text.trim() || isStreaming) return;
    setAdvisory(null);
    const history = [...messages, { role: "user" as const, content: text }];
    appendMessage({ role: "user", content: text });
    appendMessage({ role: "assistant", content: "" });
    setStreaming(true);
    let buffer = "";
    let advisoryStripped = false;

    try {
      for await (const chunk of chatStream(history, language)) {
        buffer += chunk;
        // Strip leading ADVISORY:xx:msg line once
        if (!advisoryStripped) {
          const m = buffer.match(/^ADVISORY:([a-z]{2}):([^\n]*)\n?/i);
          if (m) {
            setAdvisory({ code: m[1].toLowerCase(), message: m[2].trim() });
            buffer = buffer.slice(m[0].length);
            advisoryStripped = true;
          } else if (buffer.includes("\n") || buffer.length > 80) {
            advisoryStripped = true;
          }
        }
        updateLastAssistant(buffer);
      }
      if (buffer.trim()) setPendingAudio({ text: buffer });
    } catch (e) {
      updateLastAssistant(`⚠️ ${t.err_response}`);
    } finally {
      setStreaming(false);
    }
  }

  async function switchLanguageWithAck(targetLang: string) {
    const trigger = `[LANG_SWITCH] User has switched to ${targetLang}. Please acknowledge and re-deliver your previous response in ${targetLang}.`;
    setLanguage(targetLang);
    setAdvisory(null);
    const history = [...messages, { role: "user" as const, content: trigger }];
    appendMessage({ role: "assistant", content: "…" });
    setStreaming(true);
    try {
      const text = await chatPlain(history, targetLang);
      updateLastAssistant(text);
      setPendingAudio({ text });
    } catch {
      updateLastAssistant(`⚠️ ${ui(targetLang).err_response}`);
    } finally {
      setStreaming(false);
    }
  }

  const empty = messages.length === 0;

  return (
    <div className="min-h-screen flex flex-col bg-cream">
      <Header
        language={language}
        onOpenLanguages={() => setShowSheet(true)}
        onNewChat={() => {
          reset();
          fetchWelcome(language).then(setWelcome).catch(() => {});
        }}
      />
      <OfflineStrip />
      <AnimatePresence>
        {advisory && (
          <AdvisoryBanner
            label={`${t.switch_to} ${ISO_TO_LANG[advisory.code] || advisory.code.toUpperCase()}`}
            message={advisory.message}
            onSwitch={() => switchLanguageWithAck(ISO_TO_LANG[advisory.code] || language)}
            onDismiss={() => setAdvisory(null)}
          />
        )}
      </AnimatePresence>

      <main
        ref={scrollerRef}
        className="flex-1 overflow-y-auto scroll-fade"
      >
        <div className="mx-auto max-w-conv px-4 py-6 pb-8">
          {empty ? (
            <>
              <GreetingHero greeting={t.greeting} subtitle={welcome || t.page_subtitle} />
              <TopicTiles
                labels={[t.topic_crops, t.topic_pests, t.topic_soil, t.topic_livestock]}
                onPick={(label) => handleSend(label)}
              />
            </>
          ) : (
            <div className="flex flex-col gap-3">
              {messages.map((m, i) => (
                <ChatBubble
                  key={i}
                  role={m.role}
                  text={m.content}
                  streaming={isStreaming && i === messages.length - 1 && m.role === "assistant"}
                  language={language}
                />
              ))}
              {isStreaming && messages[messages.length - 1]?.content === "" && <TypingIndicator />}
            </div>
          )}
        </div>
      </main>

      <InputBar
        disabled={isStreaming}
        placeholder={t.chat_input_placeholder}
        listeningLabel={t.listening}
        understandingLabel={t.understanding}
        onSend={handleSend}
        language={language}
      />

      <AnimatePresence>
        {showSheet && (
          <LanguageSheet
            current={language}
            onClose={() => setShowSheet(false)}
            onPick={(l) => {
              setShowSheet(false);
              if (l !== language) switchLanguageWithAck(l);
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
