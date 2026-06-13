import { Globe, Plus, Volume2, VolumeX } from "lucide-react";
import { useConversation } from "@/store/useConversation";

export default function Header({
  language,
  onOpenLanguages,
  onNewChat,
}: {
  language: string;
  onOpenLanguages: () => void;
  onNewChat: () => void;
}) {
  const { voiceEnabled, setVoiceEnabled } = useConversation();
  return (
    <header className="h-[60px] bg-cream/90 backdrop-blur border-b border-cream-border flex items-center px-4 sticky top-0 z-20">
      <div className="mx-auto max-w-conv w-full flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-sage flex items-center justify-center">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path
                d="M20 4c-8 0-14 5-14 12 0 1.5.3 2.9.8 4 1.1-7.3 6.2-11.5 13.2-12-1 4-3.6 7.1-7.5 8.6.2.7.5 1.4.9 2C19 17 22 12 22 6c0-.7-.1-1.4-.2-2z"
                fill="#FAF6EE"
              />
            </svg>
          </div>
          <span className="font-display font-bold text-soil">VAEO</span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setVoiceEnabled(!voiceEnabled)}
            className="tap rounded-full hover:bg-cream-dark flex items-center justify-center"
            aria-label="Toggle voice"
          >
            {voiceEnabled ? <Volume2 size={20} /> : <VolumeX size={20} />}
          </button>
          <button
            onClick={onOpenLanguages}
            className="tap rounded-full hover:bg-cream-dark flex items-center gap-1.5 px-3 text-sm font-medium text-soil"
          >
            <Globe size={18} />
            <span>{language}</span>
          </button>
          <button
            onClick={onNewChat}
            className="tap rounded-full hover:bg-cream-dark flex items-center justify-center"
            aria-label="New conversation"
          >
            <Plus size={20} />
          </button>
        </div>
      </div>
    </header>
  );
}
