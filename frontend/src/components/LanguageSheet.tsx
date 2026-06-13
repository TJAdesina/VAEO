import { motion } from "framer-motion";
import { Check } from "lucide-react";

const LANGS = [
  { name: "English", native: "English" },
  { name: "Pidgin", native: "Pidgin" },
  { name: "Yoruba", native: "Yorùbá" },
  { name: "Igbo", native: "Igbo" },
  { name: "Hausa", native: "Hausa" },
];

export default function LanguageSheet({
  current,
  onClose,
  onPick,
}: {
  current: string;
  onClose: () => void;
  onPick: (l: string) => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-30 bg-soil/40 flex items-end justify-center"
      onClick={onClose}
    >
      <motion.div
        initial={{ y: 40 }}
        animate={{ y: 0 }}
        exit={{ y: 40 }}
        transition={{ type: "spring", damping: 24 }}
        className="w-full max-w-md bg-cream rounded-t-3xl p-4 pb-8"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="w-10 h-1 bg-cream-border rounded-full mx-auto mb-4" />
        <h3 className="font-display font-semibold text-soil text-lg mb-3 px-2">Language</h3>
        <div className="flex flex-col gap-2">
          {LANGS.map((l) => {
            const active = l.name === current;
            return (
              <button
                key={l.name}
                onClick={() => onPick(l.name)}
                className={`tap flex items-center justify-between w-full px-4 py-3 rounded-2xl border ${
                  active ? "border-sage bg-white" : "border-cream-border bg-white/60"
                }`}
              >
                <span className="font-display font-semibold text-soil">{l.native}</span>
                {active && <Check size={18} className="text-sage" />}
              </button>
            );
          })}
        </div>
      </motion.div>
    </motion.div>
  );
}
