import { useState } from "react";
import { Send } from "lucide-react";
import VoiceButton from "./VoiceButton";
import { transcribe } from "@/lib/api";

export default function InputBar({
  disabled,
  placeholder,
  listeningLabel,
  understandingLabel,
  onSend,
  language,
}: {
  disabled: boolean;
  placeholder: string;
  listeningLabel: string;
  understandingLabel: string;
  onSend: (text: string) => void;
  language: string;
}) {
  const [val, setVal] = useState("");
  const [status, setStatus] = useState<string | null>(null);

  const send = () => {
    const v = val.trim();
    if (!v) return;
    setVal("");
    onSend(v);
  };

  async function handleAudio(blob: Blob) {
    setStatus(understandingLabel);
    try {
      const text = await transcribe(blob, language);
      setStatus(null);
      if (text.trim()) onSend(text);
    } catch {
      setStatus(null);
    }
  }

  return (
    <div className="border-t border-cream-border bg-white">
      {status && (
        <div className="mx-auto max-w-conv px-4 pt-2 text-xs text-sage-dark">{status}</div>
      )}
      <div className="mx-auto max-w-conv px-4 py-3 flex items-end gap-2">
        <div className="flex-1 bg-cream rounded-2xl px-4 py-2.5 flex items-center">
          <textarea
            value={val}
            onChange={(e) => setVal(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
            placeholder={placeholder}
            rows={1}
            className="w-full bg-transparent resize-none outline-none text-[15px] text-soil placeholder-soil-light/60 max-h-32"
          />
        </div>
        {val.trim() ? (
          <button
            onClick={send}
            disabled={disabled}
            className="tap rounded-full bg-sage text-cream flex items-center justify-center shadow-soft disabled:opacity-50"
            aria-label="Send"
          >
            <Send size={20} />
          </button>
        ) : (
          <VoiceButton
            disabled={disabled}
            listeningLabel={listeningLabel}
            onRecorded={handleAudio}
            onStatus={setStatus}
          />
        )}
      </div>
    </div>
  );
}
