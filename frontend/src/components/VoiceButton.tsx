import { useRef, useState } from "react";
import { Mic } from "lucide-react";
import { motion } from "framer-motion";
import { startRecording, type Recorder } from "@/lib/audio";

export default function VoiceButton({
  disabled,
  listeningLabel,
  onRecorded,
  onStatus,
}: {
  disabled: boolean;
  listeningLabel: string;
  onRecorded: (blob: Blob) => void;
  onStatus: (s: string | null) => void;
}) {
  const recRef = useRef<Recorder | null>(null);
  const [recording, setRecording] = useState(false);

  async function begin() {
    if (disabled || recording) return;
    try {
      recRef.current = await startRecording();
      setRecording(true);
      onStatus(listeningLabel);
    } catch {
      onStatus("Microphone unavailable");
      setTimeout(() => onStatus(null), 2000);
    }
  }

  async function end() {
    if (!recRef.current) return;
    const rec = recRef.current;
    recRef.current = null;
    setRecording(false);
    onStatus(null);
    try {
      const blob = await rec.stop();
      if (blob.size > 1000) onRecorded(blob);
    } catch {
      /* ignore */
    }
  }

  return (
    <motion.button
      onPointerDown={begin}
      onPointerUp={end}
      onPointerCancel={end}
      onPointerLeave={() => recording && end()}
      disabled={disabled}
      animate={recording ? { scale: 1.08 } : { scale: 1 }}
      className={`tap w-14 h-14 rounded-full flex items-center justify-center shadow-soft transition-colors ${
        recording ? "bg-terracotta text-cream" : "bg-sage text-cream"
      } disabled:opacity-50`}
      aria-label="Hold to talk"
    >
      <Mic size={22} />
    </motion.button>
  );
}
