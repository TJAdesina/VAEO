import { useState } from "react";
import { Play, Loader2, Pause } from "lucide-react";
import { tts } from "@/lib/api";

export default function AudioReplayPill({ text, language }: { text: string; language: string }) {
  const [state, setState] = useState<"idle" | "loading" | "playing">("idle");
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null);

  async function toggle() {
    if (state === "playing" && audio) {
      audio.pause();
      setState("idle");
      return;
    }
    if (audio) {
      audio.play();
      setState("playing");
      return;
    }
    setState("loading");
    try {
      const url = await tts(text, language);
      const a = new Audio(url);
      a.onended = () => setState("idle");
      setAudio(a);
      a.play();
      setState("playing");
    } catch {
      setState("idle");
    }
  }

  const Icon = state === "loading" ? Loader2 : state === "playing" ? Pause : Play;
  return (
    <button
      onClick={toggle}
      className="mt-1.5 inline-flex items-center gap-1.5 text-xs text-sage-dark hover:text-sage bg-cream-dark/50 rounded-full px-2.5 py-1"
    >
      <Icon size={12} className={state === "loading" ? "animate-spin" : ""} />
      <span>{state === "playing" ? "Playing" : "Replay"}</span>
    </button>
  );
}
