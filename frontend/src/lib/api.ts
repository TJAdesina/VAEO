const BASE = import.meta.env.VITE_API_BASE_URL || "";

export type Msg = { role: "user" | "assistant"; content: string };

export type LanguageInfo = {
  name: string;
  code: string;
  flag: string;
  native?: string;
};

export async function fetchLanguages(): Promise<LanguageInfo[]> {
  const r = await fetch(`${BASE}/api/languages`);
  if (!r.ok) throw new Error("languages failed");
  return r.json();
}

export async function fetchWelcome(language: string): Promise<string> {
  const r = await fetch(`${BASE}/api/welcome?language=${encodeURIComponent(language)}`);
  if (!r.ok) throw new Error("welcome failed");
  const { text } = await r.json();
  return text;
}

export async function fetchUiStrings(language: string): Promise<Record<string, string>> {
  const r = await fetch(`${BASE}/api/ui-strings?language=${encodeURIComponent(language)}`);
  if (!r.ok) return {};
  return r.json();
}

export async function chatPlain(history: Msg[], language: string): Promise<string> {
  const r = await fetch(`${BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ history, language }),
  });
  if (!r.ok) throw new Error("chat failed");
  const { text } = await r.json();
  return text;
}

export async function* chatStream(
  history: Msg[],
  language: string,
  signal?: AbortSignal
): AsyncGenerator<string, void, void> {
  const r = await fetch(`${BASE}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ history, language }),
    signal,
  });
  if (!r.ok || !r.body) throw new Error("stream failed");
  const reader = r.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    // SSE frames separated by blank line
    const frames = buf.split("\n\n");
    buf = frames.pop() || "";
    for (const frame of frames) {
      const lines = frame.split("\n");
      let event = "message";
      const dataLines: string[] = [];
      for (const line of lines) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        else if (line.startsWith("data:")) dataLines.push(line.slice(5).replace(/^ /, ""));
      }
      if (event === "done") return;
      if (dataLines.length) yield dataLines.join("\n");
    }
  }
}

export async function transcribe(blob: Blob, language: string): Promise<string> {
  const fd = new FormData();
  fd.append("audio", blob, "recording.webm");
  fd.append("language", language);
  fd.append("mime_type", blob.type || "audio/webm");
  const r = await fetch(`${BASE}/api/transcribe`, { method: "POST", body: fd });
  if (!r.ok) throw new Error("transcribe failed");
  const { text } = await r.json();
  return text;
}

export async function tts(text: string, language: string): Promise<string> {
  const r = await fetch(`${BASE}/api/tts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, language }),
  });
  if (!r.ok) throw new Error("tts failed");
  const blob = await r.blob();
  return URL.createObjectURL(blob);
}
