import { useEffect, useState } from "react";
import { useConversation } from "@/store/useConversation";
import { ui } from "@/lib/i18n";

export default function OfflineStrip() {
  const language = useConversation((s) => s.language);
  const [online, setOnline] = useState(navigator.onLine);
  useEffect(() => {
    const on = () => setOnline(true);
    const off = () => setOnline(false);
    window.addEventListener("online", on);
    window.addEventListener("offline", off);
    return () => {
      window.removeEventListener("online", on);
      window.removeEventListener("offline", off);
    };
  }, []);
  if (online) return null;
  return (
    <div className="bg-terracotta text-cream text-center text-sm py-1.5 px-4">
      {ui(language).offline}
    </div>
  );
}
