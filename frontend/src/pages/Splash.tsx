import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useConversation } from "@/store/useConversation";

const LANGS = [
  { name: "English", native: "English" },
  { name: "Pidgin", native: "Pidgin" },
  { name: "Yoruba", native: "Yorùbá" },
  { name: "Igbo", native: "Igbo" },
  { name: "Hausa", native: "Hausa" },
];

export default function Splash() {
  const nav = useNavigate();
  const setLanguage = useConversation((s) => s.setLanguage);

  const pick = (name: string) => {
    setLanguage(name);
    nav("/chat");
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-cream px-6">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex flex-col items-center"
      >
        <div className="w-20 h-20 rounded-full bg-sage flex items-center justify-center shadow-soft">
          <Leaf />
        </div>
        <h1 className="mt-5 font-display text-4xl font-bold text-soil tracking-tight">VAEO</h1>
        <p className="mt-2 text-soil-light text-sm max-w-xs text-center">
          Your agricultural extension officer, by voice.
        </p>
      </motion.div>

      <div className="mt-12 w-full max-w-sm flex flex-col gap-3">
        {LANGS.map((l, i) => (
          <motion.button
            key={`${l.name}-${i}`}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + i * 0.05 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => pick(l.name)}
            className="tap rounded-full bg-white border border-cream-border text-soil font-display font-semibold text-lg py-3.5 px-6 shadow-soft hover:shadow-lift hover:border-sage transition-all"
          >
            {l.native}
          </motion.button>
        ))}
      </div>

      <p className="mt-10 text-xs text-soil-light">VAEO · Gemini · Spitch</p>
    </div>
  );
}

function Leaf() {
  return (
    <svg width="36" height="36" viewBox="0 0 24 24" fill="none">
      <path
        d="M20 4c-8 0-14 5-14 12 0 1.5.3 2.9.8 4 1.1-7.3 6.2-11.5 13.2-12-1 4-3.6 7.1-7.5 8.6.2.7.5 1.4.9 2C19 17 22 12 22 6c0-.7-.1-1.4-.2-2C21.3 4 20.7 4 20 4z"
        fill="#FAF6EE"
      />
    </svg>
  );
}
